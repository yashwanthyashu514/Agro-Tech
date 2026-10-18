"""
Train and compare crop-yield models (tonnes/hectare) for Karnataka.

Inputs   yield_karnataka_features.csv             (build_yield_dataset.py)
         district_season_weather.csv  [optional]  (fetch_district_season_weather.py) - added if present
         karnataka_taluk_soil_values.csv [optional] (add_soil_health_values.py) - district soil N,P,K,pH,OC

Split by TIME (no shuffling - avoids future data leaking into training):
    train 1998-2011 | validation 2012-2013 | test 2014

Models compared: 2 baselines (last year's yield, 3-year average), Ridge regression,
Random Forest, XGBoost. Best model on validation is retrained on train+validation,
scored on the test year and saved to yield_model.pkl.

Usage:  pip install pandas scikit-learn xgboost joblib
        python train_yield_model.py
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

CAT = ["crop", "season", "district"]
NUM = ["yield_lag1", "yield_mean_prev3", "area_lag1", "state_yield_lag1", "years_since_1997",
       "lat", "lon", "agro_zone_no", "soil_black_share", "soil_red_share", "soil_lateritic_share",
       "zone_rainfall_mid_mm"]
WEATHER = ["rain_total_mm", "rainy_days", "longest_dry_spell_days", "tmax_mean", "tmin_mean",
           "hot_days_over_35", "rh_mean", "solar_mean", "soil_moist_mean"]
SOIL = ["ph", "oc_pct", "n_kg_ha", "p_kg_ha", "k_kg_ha"]


def load():
    d = pd.read_csv("yield_karnataka_features.csv")
    d = d[d.crop_year >= 1998]
    num = list(NUM)
    if os.path.exists("district_season_weather.csv"):
        w = pd.read_csv("district_season_weather.csv")
        d = d.merge(w, on=["district", "crop_year", "season"], how="left")
        num += WEATHER
        print("Weather features added")
    if os.path.exists("karnataka_taluk_soil_values.csv"):
        s = pd.read_csv("karnataka_taluk_soil_values.csv")
        cols = {f"taluk_median_{c}": c for c in SOIL}
        s = s.groupby("district")[list(cols)].median().rename(columns=cols).reset_index()
        d = d.merge(s, on="district", how="left")
        num += SOIL
        print("Soil Health Card features added")
    # Keep crops with enough history to learn from
    d = d[d.groupby("crop").crop.transform("size") >= 60]
    return d, num


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    return dict(MAE=mean_absolute_error(y, p), RMSE=mean_squared_error(y, p) ** 0.5, R2=r2_score(y, p),
                median_pct_error=float(np.median(np.abs(p - y) / y) * 100))


def baseline(df, train, kind):
    fallback = train.groupby(["district", "crop", "season"]).yield_t_ha.median()
    crop_med = train.groupby("crop").yield_t_ha.median()
    first = df.yield_lag1 if kind == "lag1" else df.yield_mean_prev3
    fb = pd.Series(list(zip(df.district, df.crop, df.season)), index=df.index).map(fallback)
    return first.fillna(df.yield_mean_prev3).fillna(fb).fillna(df.crop.map(crop_med)).fillna(train.yield_t_ha.median())


def make_models(num):
    pre_lin = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
        ("num", Pipeline([("imp", SimpleImputer(strategy="median", add_indicator=True)),
                          ("sc", StandardScaler())]), num)])
    pre_tree = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), CAT),
        ("num", "passthrough", num)])
    return {
        "Ridge regression": Pipeline([("pre", pre_lin), ("m", Ridge(alpha=1.0))]),
        "Random Forest": Pipeline([("pre", ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), CAT),
            ("num", SimpleImputer(strategy="median", add_indicator=True), num)])), ("m", RandomForestRegressor(
            n_estimators=300, min_samples_leaf=3, n_jobs=-1, random_state=42))]),
        "XGBoost": Pipeline([("pre", pre_tree), ("m", XGBRegressor(
            n_estimators=600, learning_rate=0.03, max_depth=6, subsample=0.8, colsample_bytree=0.8,
            random_state=42, n_jobs=-1))]),
    }


def main():
    d, num = load()
    tr, va, te = d[d.crop_year <= 2011], d[d.crop_year.between(2012, 2013)], d[d.crop_year == 2014]
    print(f"Rows  train {len(tr):,} | validation {len(va):,} | test {len(te):,}")
    X = CAT + num
    res = {}
    for kind, name in (("lag1", "Baseline: last year's yield"), ("mean3", "Baseline: 3-year average")):
        res[name] = metrics(va.yield_t_ha, baseline(va, tr, kind))
    models = make_models(num)
    for name, m in models.items():
        m.fit(tr[X], np.log1p(tr.yield_t_ha))          # log target: crops range 0.2 to 100 t/ha
        res[name] = metrics(va.yield_t_ha, np.expm1(m.predict(va[X])))
    table = pd.DataFrame(res).T.round(3)
    print("\nValidation (2012-2013):\n", table.to_string())

    best = min(models, key=lambda n: res[n]["median_pct_error"])
    m = make_models(num)[best]
    trva = pd.concat([tr, va])
    m.fit(trva[X], np.log1p(trva.yield_t_ha))
    pred = np.expm1(m.predict(te[X]))
    test = pd.DataFrame({"Best model: " + best: metrics(te.yield_t_ha, pred),
                         "Baseline: last year's yield": metrics(te.yield_t_ha, baseline(te, trva, "lag1")),
                         "Baseline: 3-year average": metrics(te.yield_t_ha, baseline(te, trva, "mean3"))}).T.round(3)
    print("\nTest (2014):\n", test.to_string())

    out = te[["district", "crop", "season", "crop_year", "yield_t_ha"]].assign(predicted_t_ha=pred.round(3))
    out["abs_pct_error"] = (100 * (out.predicted_t_ha - out.yield_t_ha).abs() / out.yield_t_ha).round(1)
    out.to_csv("yield_test_predictions.csv", index=False)
    per_crop = out.groupby("crop").agg(rows=("crop", "size"), actual_mean=("yield_t_ha", "mean"),
                                       median_error_pct=("abs_pct_error", "median")).round(2)
    per_crop.sort_values("rows", ascending=False).to_csv("yield_test_error_by_crop.csv")
    pd.concat([table.assign(split="validation 2012-13"), test.assign(split="test 2014")]).to_csv("yield_model_results.csv")
    joblib.dump({"model": m, "features": X, "target": "log1p(yield_t_ha)", "model_name": best}, "yield_model.pkl")
    print(f"\nSaved yield_model.pkl ({best}), yield_model_results.csv, yield_test_predictions.csv")


if __name__ == "__main__":
    main()
