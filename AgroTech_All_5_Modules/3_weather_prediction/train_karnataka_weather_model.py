"""
Step 2: train ONE weather-forecast model for all of Karnataka (30 districts together).

    pip install pandas numpy scikit-learn xgboost joblib
    python train_karnataka_weather_model.py
Input : weather_karnataka_districts.csv   (from fetch_karnataka_weather.py)
Output: models/weather_model_karnataka.pkl
        models/weather_model_comparison_karnataka.csv   (model vs baselines, 1/3/7 days ahead)
        models/weather_accuracy_by_district.csv          (test error for each district)
Time  : roughly 15-40 minutes on a normal laptop.

What it predicts, for each of the next 7 days, for any district:
    rain probability, rainfall amount (mm), max temp, min temp, humidity (+ 80% range)
Days 8-15: long-term average for that date and district (no model is better that far ahead).

Method
  * Features known on day t: today's weather, lags, 3/7/14/30-day averages, rain totals,
    days since rain, season, the district's long-term average for the date, and its lat/lon.
  * Split by DATE for all districts together: oldest 60% train, next 20% validation,
    latest 20% test. Never shuffled, so the future never leaks into training.
  * Baselines: persistence ("tomorrow = today") and climatology ("the usual for that date").
  * Rain day = at least 2.5 mm (IMD definition).
"""
import os
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (brier_score_loss, f1_score, mean_absolute_error, mean_squared_error,
                             precision_score, r2_score, recall_score, roc_auc_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier, XGBRegressor

DATA = "weather_karnataka_districts.csv"
OUT = "models"
RAIN_DAY_MM = 2.5
HORIZONS = range(1, 8)
REPORT_H = (1, 3, 7)
VARS = ["temp_max_c", "temp_min_c", "rainfall_mm", "humidity_pct", "wind_speed_ms",
        "solar_rad_mj_m2", "soil_moisture_root"]
REG_TARGETS = ["temp_max_c", "temp_min_c", "humidity_pct"]


# ----------------------------------------------------------------------------- data
def load(path=DATA):
    d = pd.read_csv(path, parse_dates=["date"])
    vars_ = [v for v in VARS if v in d]
    out = []
    for name, g in d.groupby("district"):
        g = g.sort_values("date").set_index("date").asfreq("D")
        g[vars_] = g[vars_].interpolate(limit=3)
        g["rainfall_mm"] = g.rainfall_mm.fillna(0)
        g["district"] = name
        g[["latitude", "longitude"]] = g[["latitude", "longitude"]].ffill().bfill()
        out.append(g)
    return pd.concat(out), vars_


def climatology(w, vars_):
    """Each district's long-term average for every day of the year (15-day smoothing)."""
    res = {}
    for name, g in w.groupby("district"):
        doy = np.minimum(g.index.dayofyear, 365)
        c = g[vars_].groupby(doy).mean()
        c["rain_prob"] = (g.rainfall_mm >= RAIN_DAY_MM).groupby(doy).mean()
        c = c.reindex(range(1, 366)).interpolate().bfill().ffill()
        ext = pd.concat([c.iloc[-15:], c, c.iloc[:15]])
        res[name] = ext.rolling(15, center=True, min_periods=1).mean().iloc[15:-15]
    return res


def features_one(g, clim, vars_):
    f = pd.DataFrame(index=g.index)
    for v in vars_:
        f[v] = g[v]
        for l in (1, 2, 3, 7):
            f[f"{v}_lag{l}"] = g[v].shift(l)
        for r in (3, 7, 14, 30):
            f[f"{v}_mean{r}"] = g[v].rolling(r, min_periods=max(2, r // 2)).mean()
    f["rain_sum7"] = g.rainfall_mm.rolling(7).sum()
    f["rain_sum30"] = g.rainfall_mm.rolling(30).sum()
    f["rain_days7"] = (g.rainfall_mm >= RAIN_DAY_MM).rolling(7).sum()
    wet = (g.rainfall_mm >= RAIN_DAY_MM).astype(int)
    f["days_since_rain"] = wet.groupby(wet.cumsum()).cumcount()
    f["temp_range"] = g.temp_max_c - g.temp_min_c
    doy = g.index.dayofyear
    f["doy_sin"], f["doy_cos"] = np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)
    d = np.minimum(doy, 365)
    for v in ("temp_max_c", "temp_min_c", "rainfall_mm", "humidity_pct"):
        if v in vars_:
            f[f"{v}_anom"] = g[v].values - clim[v].reindex(d).values
    f["latitude"], f["longitude"] = g.latitude, g.longitude
    return f


def targets_one(g, clim, h, vars_):
    t = pd.DataFrame(index=g.index)
    for v in REG_TARGETS + ["rainfall_mm"]:
        if v in vars_:
            t[v] = g[v].shift(-h)
    t["rain_day"] = (t.rainfall_mm >= RAIN_DAY_MM).astype(float).where(t.rainfall_mm.notna())
    tdoy = np.minimum((g.index + pd.Timedelta(days=h)).dayofyear, 365)
    for v in [c for c in REG_TARGETS + ["rainfall_mm"] if c in vars_]:
        t[f"clim_{v}"] = clim[v].reindex(tdoy).values
    t["clim_rain_prob"] = clim.rain_prob.reindex(tdoy).values
    for v in [c for c in REG_TARGETS if c in vars_]:
        t[f"persist_{v}"] = g[v].values
    return t


def build(w, clim, vars_, h):
    X, T = [], []
    for name, g in w.groupby("district"):
        X.append(features_one(g, clim[name], vars_))
        tt = targets_one(g, clim[name], h, vars_)
        tt["district"] = name
        T.append(tt)
    X, T = pd.concat(X).astype("float32"), pd.concat(T)
    ok = T[[c for c in T if c in REG_TARGETS + ["rainfall_mm", "rain_day"]]].notna().all(axis=1) \
        & X.temp_max_c_mean30.notna()
    return X[ok], T[ok]


# ----------------------------------------------------------------------------- models
def reg_models():
    return {
        "Ridge regression": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=1.0)),
        "XGBoost": XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=6, subsample=0.8,
                                colsample_bytree=0.7, tree_method="hist", random_state=42, n_jobs=-1),
    }


def clf_models():
    return {
        "Logistic regression": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                             LogisticRegression(max_iter=1000)),
        "XGBoost": XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=5, subsample=0.8,
                                 colsample_bytree=0.7, tree_method="hist", random_state=42, n_jobs=-1,
                                 eval_metric="logloss"),
    }


def reg_m(y, p):
    return dict(MAE=mean_absolute_error(y, p), RMSE=mean_squared_error(y, p) ** 0.5, R2=r2_score(y, p))


def clf_m(y, prob):
    pred = prob >= 0.5
    return dict(precision=precision_score(y, pred, zero_division=0), recall=recall_score(y, pred, zero_division=0),
                F1=f1_score(y, pred, zero_division=0), ROC_AUC=roc_auc_score(y, prob), Brier=brier_score_loss(y, prob))


def fit_reg(m, X, y, v):
    return m.fit(X, np.log1p(y) if v == "rainfall_mm" else y)


def pred_reg(m, X, v):
    p = m.predict(X)
    return np.clip(np.expm1(p), 0, None) if v == "rainfall_mm" else p


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    w, vars_ = load()
    dates = np.sort(w.index.unique())
    d_tr, d_va = dates[int(len(dates) * 0.6)], dates[int(len(dates) * 0.8)]
    clim = climatology(w[w.index < d_tr], vars_)          # training years only
    regs = [v for v in REG_TARGETS if v in vars_]
    print(f"{w.district.nunique()} districts, {len(dates):,} days each "
          f"({pd.Timestamp(dates[0]).date()} to {pd.Timestamp(dates[-1]).date()})")
    print(f"train < {pd.Timestamp(d_tr).date()} <= validation < {pd.Timestamp(d_va).date()} <= test\n")

    rows = []
    for h in REPORT_H:
        X, T = build(w, clim, vars_, h)
        idx = X.index
        tr = idx < (d_tr - np.timedelta64(h, "D"))
        va = (idx >= d_tr) & (idx < (d_va - np.timedelta64(h, "D")))
        te = idx >= d_va
        for split, m_ in (("validation", va), ("test", te)):
            for v in regs:
                rows.append(dict(horizon_days=h, target=v, model="Baseline: persistence", split=split,
                                 **reg_m(T.loc[m_, v], T.loc[m_, f"persist_{v}"])))
                rows.append(dict(horizon_days=h, target=v, model="Baseline: climatology", split=split,
                                 **reg_m(T.loc[m_, v], T.loc[m_, f"clim_{v}"])))
            rows.append(dict(horizon_days=h, target="rainfall_mm", model="Baseline: climatology", split=split,
                             **reg_m(T.loc[m_, "rainfall_mm"], T.loc[m_, "clim_rainfall_mm"])))
            rows.append(dict(horizon_days=h, target="rain_day", model="Baseline: climatology", split=split,
                             **clf_m(T.loc[m_, "rain_day"], T.loc[m_, "clim_rain_prob"])))
        for v in regs + ["rainfall_mm"]:
            for name, m in reg_models().items():
                fit_reg(m, X[tr], T.loc[tr, v], v)
                for split, m_ in (("validation", va), ("test", te)):
                    rows.append(dict(horizon_days=h, target=v, model=name, split=split,
                                     **reg_m(T.loc[m_, v], pred_reg(m, X[m_], v))))
        for name, m in clf_models().items():
            m.fit(X[tr], T.loc[tr, "rain_day"])
            for split, m_ in (("validation", va), ("test", te)):
                rows.append(dict(horizon_days=h, target="rain_day", model=name, split=split,
                                 **clf_m(T.loc[m_, "rain_day"], m.predict_proba(X[m_])[:, 1])))
        print(f"  compared models {h} day(s) ahead   [{(time.time() - t0) / 60:.1f} min]")
    comp = pd.DataFrame(rows)
    comp.round(4).to_csv(f"{OUT}/weather_model_comparison_karnataka.csv", index=False)

    val = comp[(comp.split == "validation") & ~comp.model.str.startswith("Baseline")]
    chosen = {v: val[val.target == v].groupby("model").MAE.mean().idxmin() for v in regs + ["rainfall_mm"]}
    chosen["rain_day"] = val[val.target == "rain_day"].groupby("model").Brier.mean().idxmin()
    print("\nChosen model per target (by validation):", chosen)

    final, intervals, by_district = {}, {}, []
    for h in HORIZONS:
        X, T = build(w, clim, vars_, h)
        idx = X.index
        tr = idx < (d_tr - np.timedelta64(h, "D"))
        va = (idx >= d_tr) & (idx < (d_va - np.timedelta64(h, "D")))
        te = idx >= d_va
        fit = idx < (d_va - np.timedelta64(h, "D"))
        for v in regs + ["rainfall_mm"]:
            m0 = fit_reg(reg_models()[chosen[v]], X[tr], T.loc[tr, v], v)
            if v != "rainfall_mm":
                res = T.loc[va, v] - pred_reg(m0, X[va], v)
                intervals[(v, h)] = (float(res.quantile(0.1)), float(res.quantile(0.9)))
            m = fit_reg(reg_models()[chosen[v]], X[fit], T.loc[fit, v], v)
            final[(v, h)] = m
            if h in (1, 7):
                p = pred_reg(m, X[te], v)
                e = pd.DataFrame({"district": T.loc[te, "district"].values, "err": np.abs(p - T.loc[te, v].values)})
                for dname, g in e.groupby("district"):
                    by_district.append(dict(district=dname, horizon_days=h, target=v, test_MAE=g.err.mean()))
        m = clf_models()[chosen["rain_day"]].fit(X[fit], T.loc[fit, "rain_day"])
        final[("rain_day", h)] = m
        print(f"  final models trained for day +{h}   [{(time.time() - t0) / 60:.1f} min]")

    pd.DataFrame(by_district).round(3).to_csv(f"{OUT}/weather_accuracy_by_district.csv", index=False)
    coords = w.groupby("district")[["latitude", "longitude"]].first()
    bundle = {"models": final, "intervals": intervals, "climatology": clim, "chosen": chosen, "vars": vars_,
              "reg_targets": regs, "feature_columns": list(X.columns), "districts": coords}
    joblib.dump(bundle, f"{OUT}/weather_model_karnataka.pkl", compress=3)

    test = comp[comp.split == "test"]
    print("\nTEST RESULTS (latest 20% of years, all districts)")
    for v in regs + ["rainfall_mm"]:
        print("\n", v, "- MAE")
        print(test[test.target == v].pivot_table(index="model", columns="horizon_days", values="MAE").round(2).to_string())
    print("\n rain_day - ROC-AUC (1.0 perfect, 0.5 guessing)")
    print(test[test.target == "rain_day"].pivot_table(index="model", columns="horizon_days", values="ROC_AUC").round(3).to_string())
    print(f"\nSaved {OUT}/weather_model_karnataka.pkl   (total {(time.time() - t0) / 60:.1f} min)")


# ----------------------------------------------------------------------------- forecast
def forecast(bundle, history, district, days=15):
    """Forecast for one district from its weather history (history = load() output)."""
    g = history[history.district == district]
    if g.empty:
        raise ValueError(f"Unknown district {district}. Options: {', '.join(bundle['districts'].index)}")
    clim = bundle["climatology"][district]
    X = features_one(g, clim, bundle["vars"]).iloc[[-1]][bundle["feature_columns"]].astype("float32")
    today = g.index.max()
    out = []
    for h in range(1, days + 1):
        d = today + pd.Timedelta(days=h)
        doy = min(d.dayofyear, 365)
        row = {"district": district, "date": d.date(), "days_ahead": h}
        if h <= 7:
            row["rain_probability_pct"] = round(100 * float(bundle["models"][("rain_day", h)].predict_proba(X)[0, 1]))
            row["expected_rain_mm"] = round(float(pred_reg(bundle["models"][("rainfall_mm", h)], X, "rainfall_mm")[0]), 1)
            for v in bundle["reg_targets"]:
                p = float(bundle["models"][(v, h)].predict(X)[0])
                lo, hi = bundle["intervals"][(v, h)]
                row[v] = round(p, 1)
                row[f"{v}_range80"] = f"{p + lo:.1f} to {p + hi:.1f}"
            row["source"] = "ML model"
        else:
            row["rain_probability_pct"] = round(100 * float(clim.rain_prob[doy]))
            row["expected_rain_mm"] = round(float(clim.rainfall_mm[doy]), 1)
            for v in bundle["reg_targets"]:
                row[v] = round(float(clim[v][doy]), 1)
            row["source"] = "long-term average"
        out.append(row)
    return pd.DataFrame(out)


if __name__ == "__main__":
    main()
