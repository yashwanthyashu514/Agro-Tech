"""
Predict the dates of each growth stage for a crop, a sowing date and a location's weather.

Method (thermal time / Growing Degree Days - the standard way crop models time phenology):
  1. GDD for a day = max(0, min(Tavg, T_upper) - T_base)    (T_base per crop, T_upper = 35 C)
  2. Calibrate: sow the crop on its TYPICAL sowing date in an AVERAGE year at this location and
     add up the GDD reached at the end of each stage in crop_growth_stages.csv.
     That gives the heat each stage needs at this place.
  3. Predict: from YOUR sowing date, add up GDD day by day (actual weather where available,
     the average year for future days) and record when each stage's GDD is reached.
  So a crop sown into cooler weather takes longer, and one sown into warmer weather finishes sooner.

Usage:
    python predict_growth_stages.py --crop maize --sow 2025-07-05 --weather weather_davanagere_1991_2025.csv
    python predict_growth_stages.py --crop chickpea --sow 2025-11-10 --weather weather_davanagere_1991_2025.csv --out maize_plan.csv

The weather file is the one made by fetch_weather_nasa_power.py (needs date, temp_min_c, temp_max_c).
"""
import argparse
import numpy as np
import pandas as pd

T_UPPER = 35.0


def load_weather(path):
    w = pd.read_csv(path, parse_dates=["date"])
    w["tavg"] = (w.temp_min_c + w.temp_max_c) / 2
    w = w.dropna(subset=["tavg"])
    w["doy"] = w.date.dt.dayofyear.clip(upper=365)
    clim = w.groupby("doy").tavg.mean().reindex(range(1, 366)).interpolate().bfill().ffill()
    return w.set_index("date").tavg, clim


def daily_temps(start, n_days, actual, clim):
    dates = pd.date_range(start, periods=n_days)
    t = actual.reindex(dates)
    from_clim = t.isna()
    t[from_clim] = clim.loc[dates[from_clim].dayofyear.to_numpy().clip(max=365)].values
    return dates, t.values, from_clim.values


def gdd(t, tbase):
    return np.maximum(0, np.minimum(t, T_UPPER) - tbase)


def predict(crop, sow, weather_path, stages_path="crop_growth_stages.csv", master_path="crop_growth_master.csv"):
    st = pd.read_csv(stages_path)
    ms = pd.read_csv(master_path).set_index("crop")
    if crop not in ms.index:
        raise SystemExit(f"Unknown crop '{crop}'. Choose from: {', '.join(ms.index)}")
    info, cs = ms.loc[crop], st[st.crop == crop].sort_values("stage_no")
    tbase = info.base_temp_c
    actual, clim = load_weather(weather_path)

    # 2. Calibrate GDD targets on the typical sowing date in an average year
    typical = pd.Timestamp(f"2001-{info.typical_sowing_date}")
    horizon = int(cs.end_day.max()) + 1
    cal_dates = pd.date_range(typical, periods=horizon)
    cum_ref = np.cumsum(gdd(clim.loc[cal_dates.dayofyear.to_numpy().clip(max=365)].values, tbase))
    targets = [(r.growth_stage, cum_ref[min(int(r.end_day), horizon - 1)]) for r in cs.itertuples()]

    # 3. Accumulate GDD from the actual sowing date (allow up to 2x the typical duration)
    sow = pd.Timestamp(sow)
    dates, t, est = daily_temps(sow, horizon * 2, actual, clim)
    cum = np.cumsum(gdd(t, tbase))
    rows, start = [], sow
    for (name, target), r in zip(targets, cs.itertuples()):
        idx = int(np.searchsorted(cum, target))
        if idx >= len(dates):
            rows.append(dict(stage=name, start_date=start.date(), end_date=None, note="not reached - too cold"))
            break
        end = dates[idx]
        rows.append(dict(stage=name, start_date=start.date(), end_date=end.date(),
                         days_after_sowing=f"{(start - sow).days}-{(end - sow).days}",
                         typical_das=f"{r.start_day}-{r.end_day}", kc=r.kc, water_need=r.water_need,
                         critical_irrigation=r.critical_irrigation,
                         weather_used="forecast / average year" if est[idx] else "actual"))
        start = end + pd.Timedelta(days=1)
    return pd.DataFrame(rows), info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crop", required=True)
    ap.add_argument("--sow", required=True, help="sowing date YYYY-MM-DD")
    ap.add_argument("--weather", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    df, info = predict(a.crop.lower(), a.sow, a.weather)
    print(f"\n{a.crop.title()} sown {a.sow}  (typical duration {info.total_duration_days} days, base temp {info.base_temp_c} C)\n")
    print(df.to_string(index=False))
    if a.out:
        df.to_csv(a.out, index=False)


if __name__ == "__main__":
    main()
