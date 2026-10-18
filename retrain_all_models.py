"""
Retrain all AgroTech models with the currently installed library versions
and save to backend/models_store/  for production use.

Run once:
    python retrain_all_models.py

This avoids XGBoost / sklearn version mismatch errors with pre-built .pkl files.
"""
import os, sys, time, warnings
import joblib, numpy as np, pandas as pd
warnings.filterwarnings("ignore")

# â”€â”€ paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
DATA = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "AgroTech_All_5_Modules", "AgroTech_All_5_Modules"))
OUT  = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "models_store"))
os.makedirs(OUT, exist_ok=True)

# â”€â”€ imports â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor

SEED = 42
t_total = time.time()

print("=" * 70)
print("AGROTECH MODEL RETRAINING")
print("=" * 70)

# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘  MODULE 2 â€“ CROP RECOMMENDATION                                      â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("\n[1/3] Crop Recommendation Model ...")
t0 = time.time()

df = pd.read_csv(os.path.join(DATA, "2_crop_recommendation", "Crop_recommendation.csv"))
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
le = LabelEncoder()
y = le.fit_transform(df["label"])
X = df[FEATURES]

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)

candidates = {
    "Random Forest": RandomForestClassifier(n_estimators=400, random_state=SEED, n_jobs=-1),
    "XGBoost":       XGBClassifier(n_estimators=400, learning_rate=0.1, max_depth=6,
                                   random_state=SEED, n_jobs=-1, eval_metric="mlogloss"),
    "LightGBM":      LGBMClassifier(n_estimators=400, learning_rate=0.05, random_state=SEED, verbose=-1),
}

cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
best_name, best_score, best_model = None, -1, None
for name, m in candidates.items():
    s = cross_validate(m, Xtr, ytr, cv=cv, scoring="f1_macro", n_jobs=1)
    score = s["test_score"].mean()
    acc = accuracy_score(yte, m.fit(Xtr, ytr).predict(Xte))
    print(f"   {name:20s}  CV-F1={score:.4f}  Test-Acc={acc:.4f}")
    if score > best_score:
        best_score, best_name, best_model = score, name, m

print(f"   âœ“ Best: {best_name} (CV-F1={best_score:.4f})")

# retrain on ALL data for production
final_crop = candidates[best_name].fit(X, y)
ranges = df.groupby("label")[FEATURES].quantile([0.05, 0.95]).unstack()
joblib.dump({
    "model": final_crop,
    "label_encoder": le,
    "features": FEATURES,
    "model_name": best_name,
    "crop_ranges": ranges,
}, os.path.join(OUT, "crop_model.pkl"))
print(f"   Saved â†’ models_store/crop_model.pkl  [{time.time()-t0:.0f}s]")


# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘  MODULE 5 â€“ YIELD PREDICTION                                         â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("\n[2/3] Yield Prediction Model ...")
t0 = time.time()

CAT = ["crop", "season", "district"]
NUM = ["yield_lag1", "yield_mean_prev3", "area_lag1", "state_yield_lag1", "years_since_1997",
       "lat", "lon", "agro_zone_no", "soil_black_share", "soil_red_share", "soil_lateritic_share",
       "zone_rainfall_mid_mm"]

d = pd.read_csv(os.path.join(DATA, "5_yield_prediction", "yield_karnataka_features.csv"))
d = d[d["crop_year"] >= 1998]
d = d[d.groupby("crop")["crop"].transform("size") >= 60]

tr = d[d["crop_year"] <= 2011]
va = d[d["crop_year"].between(2012, 2013)]
te = d[d["crop_year"] == 2014]
trva = pd.concat([tr, va])

def metrics_yield(y, p):
    y, p = np.asarray(y), np.asarray(p)
    return {"MAE": mean_absolute_error(y, p),
            "RMSE": mean_squared_error(y, p)**0.5,
            "R2": r2_score(y, p),
            "MdPctErr": float(np.median(np.abs(p - y) / (y + 1e-9)) * 100)}

def make_yield_pipeline(num):
    pre_tree = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), CAT),
        ("num", "passthrough", num),
    ])
    return {
        "XGBoost": Pipeline([("pre", pre_tree), ("m", XGBRegressor(
            n_estimators=600, learning_rate=0.03, max_depth=6, subsample=0.8,
            colsample_bytree=0.8, random_state=SEED, n_jobs=-1))]),
        "LightGBM": Pipeline([("pre", pre_tree), ("m", LGBMRegressor(
            n_estimators=600, learning_rate=0.03, max_depth=6, subsample=0.8,
            colsample_bytree=0.8, random_state=SEED, verbose=-1, n_jobs=-1))]),
        "Random Forest": Pipeline([
            ("pre", ColumnTransformer([
                ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), CAT),
                ("num", SimpleImputer(strategy="median", add_indicator=True), num),
            ])),
            ("m", RandomForestRegressor(n_estimators=300, min_samples_leaf=3, n_jobs=-1, random_state=SEED))
        ]),
    }

X_cols = CAT + NUM
models_y = make_yield_pipeline(NUM)
best_yn, best_ys = None, 1e9

for name, m in models_y.items():
    m.fit(tr[X_cols], np.log1p(tr["yield_t_ha"]))
    p_va = np.expm1(m.predict(va[X_cols]))
    mt = metrics_yield(va["yield_t_ha"], p_va)
    print(f"   {name:20s}  MAE={mt['MAE']:.3f}  R2={mt['R2']:.3f}  MdPctErr={mt['MdPctErr']:.1f}%")
    if mt["MAE"] < best_ys:
        best_ys, best_yn = mt["MAE"], name

print(f"   âœ“ Best yield model: {best_yn}")
final_yield = make_yield_pipeline(NUM)[best_yn]
final_yield.fit(trva[X_cols], np.log1p(trva["yield_t_ha"]))
p_te = np.expm1(final_yield.predict(te[X_cols]))
mt = metrics_yield(te["yield_t_ha"], p_te)
print(f"   Test â†’ MAE={mt['MAE']:.3f}  R2={mt['R2']:.3f}")

joblib.dump({
    "model": final_yield,
    "features": X_cols,
    "target": "log1p(yield_t_ha)",
    "model_name": best_yn,
}, os.path.join(OUT, "yield_model.pkl"))
print(f"   Saved â†’ models_store/yield_model.pkl  [{time.time()-t0:.0f}s]")


# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘  MODULE 3 â€“ WEATHER PREDICTION (trimmed for speed, 7-day horizon)    â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("\n[3/3] Weather Prediction Model ...")
t0 = time.time()

# Add the weather module path
sys.path.insert(0, os.path.join(DATA, "3_weather_prediction"))
from train_karnataka_weather_model import (
    load, climatology, build, features_one, targets_one,
    reg_models, clf_models, fit_reg, pred_reg,
    REG_TARGETS, RAIN_DAY_MM, HORIZONS
)
from sklearn.metrics import roc_auc_score

w, vars_ = load(os.path.join(DATA, "3_weather_prediction", "weather_karnataka_districts.csv"))
dates = np.sort(w.index.unique())
d_tr = dates[int(len(dates) * 0.6)]
d_va = dates[int(len(dates) * 0.8)]
clim = climatology(w[w.index < d_tr], vars_)
regs = [v for v in REG_TARGETS if v in vars_]
print(f"   {w['district'].nunique()} districts | {len(dates):,} days | "
      f"train<{pd.Timestamp(d_tr).date()} | val<{pd.Timestamp(d_va).date()}")

# evaluate on validation to pick model per target
chosen = {}
for h in (1, 3, 7):
    X_b, T_b = build(w, clim, vars_, h)
    idx = X_b.index
    tr_m = idx < (d_tr - np.timedelta64(h, "D"))
    va_m = (idx >= d_tr) & (idx < (d_va - np.timedelta64(h, "D")))
    best_reg, best_clf = {}, {}
    for v in regs + ["rainfall_mm"]:
        scores = {}
        for name, m in reg_models().items():
            fit_reg(m, X_b[tr_m], T_b.loc[tr_m, v], v)
            scores[name] = mean_absolute_error(T_b.loc[va_m, v], pred_reg(m, X_b[va_m], v))
        best_reg[v] = min(scores, key=scores.get)
    cscores = {}
    for name, m in clf_models().items():
        m.fit(X_b[tr_m], T_b.loc[tr_m, "rain_day"])
        cscores[name] = -roc_auc_score(T_b.loc[va_m, "rain_day"], m.predict_proba(X_b[va_m])[:, 1])
    best_clf["rain_day"] = min(cscores, key=cscores.get)
    if h == 1:
        chosen = {**best_reg, **best_clf}

print(f"   Chosen models: {chosen}")

# train final models on train+val, compute intervals, save
final_wx, intervals, by_dist = {}, {}, []
for h in HORIZONS:
    X_b, T_b = build(w, clim, vars_, h)
    idx = X_b.index
    tr_m = idx < (d_tr - np.timedelta64(h, "D"))
    va_m = (idx >= d_tr) & (idx < (d_va - np.timedelta64(h, "D")))
    fit_m = idx < (d_va - np.timedelta64(h, "D"))
    for v in regs + ["rainfall_mm"]:
        m0 = fit_reg(reg_models()[chosen.get(v, "XGBoost")], X_b[tr_m], T_b.loc[tr_m, v], v)
        if v != "rainfall_mm":
            res = T_b.loc[va_m, v] - pred_reg(m0, X_b[va_m], v)
            intervals[(v, h)] = (float(res.quantile(0.1)), float(res.quantile(0.9)))
        m_f = fit_reg(reg_models()[chosen.get(v, "XGBoost")], X_b[fit_m], T_b.loc[fit_m, v], v)
        final_wx[(v, h)] = m_f
    m_clf = clf_models()[chosen.get("rain_day", "XGBoost")]
    m_clf.fit(X_b[fit_m], T_b.loc[fit_m, "rain_day"])
    final_wx[("rain_day", h)] = m_clf
    print(f"   Horizon +{h} trained â€¦ [{time.time()-t0:.0f}s]")

coords = w.groupby("district")[["latitude", "longitude"]].first()
X_last, _ = build(w, clim, vars_, 1)
bundle = {
    "models": final_wx,
    "intervals": intervals,
    "climatology": clim,
    "chosen": chosen,
    "vars": vars_,
    "reg_targets": regs,
    "feature_columns": list(X_last.columns),
    "districts": coords,
}
joblib.dump(bundle, os.path.join(OUT, "weather_model_karnataka.pkl"), compress=3)
print(f"   Saved â†’ models_store/weather_model_karnataka.pkl  [{time.time()-t0:.0f}s]")

print(f"\nâœ…  ALL MODELS SAVED to backend/models_store/")
print(f"   Total time: {(time.time()-t_total)/60:.1f} min")

