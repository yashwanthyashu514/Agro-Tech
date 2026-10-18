"""
AgroTech prediction engine - one call answers:
  "I am in <taluk/district>, it is <season>. What should I grow, when will it grow, what yield?"

Combines:
  location + soil type  karnataka_location_soil.csv / karnataka_taluk_soil_values.csv (if present)
  crop recommendation   models/crop_model.pkl              (train_crop_model.py)
  crop growth stages    predict_growth_stages.py            (heat-unit model)
  yield prediction      yield_model.pkl                     (train_yield_model.py)
  season weather        your NASA POWER weather CSV         (fetch_weather_nasa_power.py)

Usage examples:
  python agro_engine.py --taluk Davanagere --season Kharif --weather weather_davanagere_1991_2025.csv
  python agro_engine.py --taluk Davanagere --season Kharif --N 80 --P 40 --K 40 --ph 7.2 \
         --temperature 26 --humidity 75 --rainfall 120 --sow 2026-06-20
Soil values (N, P, K, pH) come from --N/--P/--K/--ph, else from the Soil Health Card medians
for the taluk (karnataka_taluk_soil_values.csv, made by add_soil_health_values.py).
"""
import argparse
import json
import os
import warnings
import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
SEASON_MONTHS = {"Kharif": [6, 7, 8, 9], "Rabi": [10, 11, 12, 1], "Summer": [2, 3, 4, 5]}
SEASON_SOW = {"Kharif": "06-20", "Rabi": "10-20", "Summer": "02-01"}
APY_SEASON = {"Kharif": "Kharif", "Rabi": "Rabi", "Summer": "Summer"}
# crop recommendation label -> crop name in the yield statistics
YIELD_CROP = {"rice": "Rice", "maize": "Maize", "chickpea": "Gram", "pigeonpeas": "Arhar/Tur",
              "mungbean": "Moong(Green Gram)", "blackgram": "Urad", "mothbeans": "Moth", "lentil": "Masoor",
              "cotton": "Cotton(lint)", "jute": "Jute", "banana": "Banana", "mango": "Mango",
              "grapes": "Grapes", "pomegranate": "Pome Granet", "watermelon": "Water Melon",
              "papaya": "Papaya", "coffee": "Coffee", "kidneybeans": "Rajmash Kholar"}
PERENNIAL = {"mango", "coconut", "coffee", "grapes", "pomegranate", "orange", "apple"}


def find_location(taluk=None, district=None):
    ts = pd.read_csv("karnataka_taluk_soil.csv")
    if taluk:
        m = ts[ts.taluk.str.lower() == taluk.lower()]
        if m.empty:
            raise SystemExit(f"Taluk '{taluk}' not found. Examples: {', '.join(ts.taluk.head(8))}")
        return m.iloc[0]
    m = ts[ts.district.str.lower() == (district or "").lower()]
    if m.empty:
        raise SystemExit(f"District '{district}' not found.")
    return m.iloc[0]


def soil_values(loc, args):
    vals = {k: getattr(args, k) for k in ("N", "P", "K", "ph")}
    src = "entered by farmer"
    if any(v is None for v in vals.values()) and os.path.exists("karnataka_taluk_soil_values.csv"):
        s = pd.read_csv("karnataka_taluk_soil_values.csv").set_index("taluk").loc[loc.taluk]
        fill = {"N": s.taluk_median_n_kg_ha, "P": s.taluk_median_p_kg_ha, "K": s.taluk_median_k_kg_ha,
                "ph": s.taluk_median_ph}
        vals = {k: (v if v is not None else fill[k]) for k, v in vals.items()}
        src = "Soil Health Card median for the taluk"
    missing = [k for k, v in vals.items() if v is None or pd.isna(v)]
    if missing:
        raise SystemExit(f"Need soil values {missing}: pass --N --P --K --ph, or run add_soil_health_values.py")
    return vals, src


def season_weather(args, season):
    if all(getattr(args, k) is not None for k in ("temperature", "humidity", "rainfall")):
        return {"temperature": args.temperature, "humidity": args.humidity, "rainfall": args.rainfall}, "entered"
    if not args.weather:
        raise SystemExit("Give --weather <NASA CSV> or --temperature --humidity --rainfall")
    w = pd.read_csv(args.weather, parse_dates=["date"])
    w = w[w.date.dt.month.isin(SEASON_MONTHS[season])]
    years = w.date.dt.year.nunique()
    t = w.temp_avg_c.mean() if "temp_avg_c" in w else ((w.temp_min_c + w.temp_max_c) / 2).mean()
    return ({"temperature": round(float(t), 1), "humidity": round(float(w.humidity_pct.mean()), 1),
             # the training data's rainfall column is treated as average MONTHLY rainfall (mm)
             "rainfall": round(float(w.rainfall_mm.sum() / years / len(SEASON_MONTHS[season])), 1)},
            f"long-term {season} average from {args.weather}")


def recommend(soil, weather, top=5):
    b = joblib.load("models/crop_model.pkl")
    x = pd.DataFrame([{**soil, **weather}])[b["features"]]
    prob = b["model"].predict_proba(x)[0]
    order = np.argsort(-prob)[:top]
    r = b["crop_ranges"]
    out = []
    for i in order:
        crop = b["label_encoder"].classes_[i]
        reasons = []
        for f in b["features"]:
            lo, hi = r.loc[crop, (f, 0.05)], r.loc[crop, (f, 0.95)]
            ok = lo <= x[f].iat[0] <= hi
            reasons.append(f"{'OK ' if ok else 'OUT'} {f} {x[f].iat[0]:g} (typical for {crop}: {lo:.0f}-{hi:.0f})")
        out.append({"crop": crop, "suitability": round(float(prob[i]), 3), "reasons": reasons})
    return out


def predict_yield(crop, district, season):
    apy = YIELD_CROP.get(crop)
    if not apy or not os.path.exists("yield_model.pkl"):
        return None
    d = pd.read_csv("yield_karnataka_features.csv")
    h = d[(d.district == district) & (d.crop == apy) & (d.season == APY_SEASON[season])].sort_values("crop_year")
    if len(h) < 2:
        return None
    b = joblib.load("yield_model.pkl")
    last = h.iloc[-1]
    st = d[(d.crop == apy) & (d.season == APY_SEASON[season]) & (d.crop_year == last.crop_year)].yield_t_ha.median()
    row = last.copy()
    row["yield_lag1"], row["yield_mean_prev3"] = last.yield_t_ha, h.yield_t_ha.tail(3).mean()
    row["area_lag1"], row["state_yield_lag1"] = last.area_ha, st
    row["years_since_1997"] = last.crop_year + 1 - 1997
    x = pd.DataFrame([row])
    for c in b["features"]:
        if c not in x:
            x[c] = np.nan
    p = float(np.expm1(b["model"].predict(x[b["features"]])[0]))
    return {"predicted_yield_t_ha": round(p, 2), "based_on_history_to": int(last.crop_year),
            "district_avg_last3_t_ha": round(h.yield_t_ha.tail(3).mean(), 2)}


def growth(crop, sow, weather_path):
    if crop in PERENNIAL:
        c = pd.read_csv("perennial_crop_calendar.csv").set_index("crop")
        return {"type": "perennial calendar", **c.loc[crop].to_dict()} if crop in c.index else None
    if weather_path:
        from predict_growth_stages import predict
        df, _ = predict(crop, sow, weather_path)
        return {"type": "heat-unit prediction", "stages": df[["stage", "start_date", "end_date",
                                                              "days_after_sowing", "water_need"]].astype(str).to_dict("records")}
    st = pd.read_csv("crop_growth_stages.csv")
    st = st[st.crop == crop]
    if st.empty:
        return None
    s0 = pd.Timestamp(sow)
    return {"type": "typical durations", "stages": [
        {"stage": r.growth_stage, "start_date": str((s0 + pd.Timedelta(days=int(r.start_day))).date()),
         "end_date": str((s0 + pd.Timedelta(days=int(r.end_day))).date()),
         "days_after_sowing": f"{r.start_day}-{r.end_day}", "water_need": r.water_need} for r in st.itertuples()]}


def district_weather_file(path, district):
    """If the weather file covers many districts, keep only this district (temp file)."""
    if not path:
        default = os.path.join("..", "3_weather_prediction", "weather_karnataka_districts.csv")
        path = default if os.path.exists(default) else None
    if not path:
        return None
    w = pd.read_csv(path, nrows=2)
    if "district" not in w:
        return path
    w = pd.read_csv(path)
    w = w[w.district == district]
    out = f"_weather_{district.replace(' ', '_')}.csv"
    w.to_csv(out, index=False)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--taluk"); ap.add_argument("--district")
    ap.add_argument("--season", choices=list(SEASON_MONTHS), default="Kharif")
    ap.add_argument("--sow", help="sowing date YYYY-MM-DD (default: typical date this season)")
    for k in ("N", "P", "K", "ph", "temperature", "humidity", "rainfall"):
        ap.add_argument(f"--{k}", type=float)
    ap.add_argument("--weather"); ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    loc = find_location(a.taluk, a.district)
    a.weather = district_weather_file(a.weather, loc.district)
    soil, soil_src = soil_values(loc, a)
    weather, w_src = season_weather(a, a.season)
    sow = a.sow or f"{pd.Timestamp.today().year}-{SEASON_SOW[a.season]}"
    recs = recommend(soil, weather, a.top)
    for r in recs:
        r["yield"] = predict_yield(r["crop"], loc.district, a.season)
    top_growth = growth(recs[0]["crop"], sow, a.weather)
    result = {"location": {"taluk": loc.taluk, "district": loc.district, "agro_zone": loc.agro_zone,
                           "soil_type": f"{loc.dominant_soil}" + (f" / {loc.secondary_soil}" if isinstance(loc.secondary_soil, str) and loc.secondary_soil else "")},
              "season": a.season, "soil_inputs": soil, "soil_source": soil_src,
              "weather_inputs": weather, "weather_source": w_src,
              "recommendations": recs, "growth_plan_for_top_crop": {"crop": recs[0]["crop"], "sow_date": sow, **(top_growth or {})}}
    if a.json:
        print(json.dumps(result, indent=2, default=str))
        return
    L = result["location"]
    print(f"\nLOCATION  {L['taluk']}, {L['district']} | {L['agro_zone']} | soil: {L['soil_type']}")
    print(f"SEASON    {a.season}    soil {soil} ({soil_src})")
    print(f"WEATHER   {weather} ({w_src})\n")
    print("RECOMMENDED CROPS")
    for i, r in enumerate(recs, 1):
        y = r["yield"]
        ytxt = f" | predicted yield {y['predicted_yield_t_ha']} t/ha (district 3-yr avg {y['district_avg_last3_t_ha']})" if y else ""
        print(f" {i}. {r['crop']:12s} suitability {r['suitability']:.2f}{ytxt}")
        if i == 1:
            for s in r["reasons"]:
                print("      " + s)
    g = result["growth_plan_for_top_crop"]
    print(f"\nGROWTH PLAN - {g['crop']} sown {g['sow_date']} ({g.get('type', 'n/a')})")
    for s in g.get("stages", []):
        print(f"   {s['stage']:32s} {s['start_date']} -> {s['end_date']}  (DAS {s['days_after_sowing']}, water {s['water_need']})")
    if g.get("type") == "perennial calendar":
        print("  ", {k: v for k, v in g.items() if k not in ("crop", "sow_date", "type")})


if __name__ == "__main__":
    main()
