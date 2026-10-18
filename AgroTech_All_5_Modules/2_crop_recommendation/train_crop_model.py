"""
Module 2 - Crop Recommendation: train, compare and save the model.

Data:   Crop_recommendation.csv  (N, P, K, temperature, humidity, ph, rainfall -> 22 crops)
Output (models/):
    crop_model.pkl                 best model + crop ranges for explanations
    crop_model_comparison.csv      cross-validation + test scores for every algorithm
    crop_classification_report.csv precision / recall / F1 per crop
    crop_confusion_matrix.png/.csv
    crop_feature_importance.csv/.png

Usage:  pip install pandas scikit-learn xgboost lightgbm matplotlib joblib
        python train_crop_model.py
"""
import os
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, f1_score, precision_score, recall_score,
                             classification_report, confusion_matrix)
from sklearn.inspection import permutation_importance
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
OUT = "models"
SEED = 42
# Realistic measurement error, used for the robustness test (lab / sensor / forecast error)
NOISE = {"N": 0.15, "P": 0.15, "K": 0.15, "ph": 0.3, "temperature": 1.5, "humidity": 5.0, "rainfall": 0.20}
RELATIVE = {"N", "P", "K", "rainfall"}   # noise as a fraction of the value; others in absolute units


def add_noise(X, rng):
    X = X.copy()
    for c, s in NOISE.items():
        e = rng.normal(0, s, len(X))
        X[c] = X[c] * (1 + e) if c in RELATIVE else X[c] + e
    X[["N", "P", "K", "rainfall"]] = X[["N", "P", "K", "rainfall"]].clip(lower=0)
    X["humidity"] = X.humidity.clip(0, 100)
    return X


def models():
    return {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)),
        "K-Nearest Neighbours": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=7)),
        "Decision Tree": DecisionTreeClassifier(random_state=SEED),
        "Random Forest": RandomForestClassifier(n_estimators=400, random_state=SEED, n_jobs=-1),
        "XGBoost": XGBClassifier(n_estimators=400, learning_rate=0.1, max_depth=6, random_state=SEED,
                                 n_jobs=-1, eval_metric="mlogloss"),
        "LightGBM": LGBMClassifier(n_estimators=400, learning_rate=0.05, random_state=SEED, verbose=-1),
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    df = pd.read_csv("Crop_recommendation.csv")
    le = LabelEncoder()
    y = le.fit_transform(df.label)
    X = df[FEATURES]
    # 80% train / 20% test, every crop in equal proportion in both
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    rng = np.random.default_rng(SEED)
    Xte_noisy = add_noise(Xte, rng)

    rows, fitted = [], {}
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    for name, m in models().items():
        t = time.time()
        s = cross_validate(m, Xtr, ytr, cv=cv, scoring=["accuracy", "f1_macro"], n_jobs=1)
        m.fit(Xtr, ytr)
        p, pn = m.predict(Xte), m.predict(Xte_noisy)
        t0 = time.time(); m.predict_proba(Xte.iloc[:1]); latency = (time.time() - t0) * 1000
        rows.append({"model": name,
                     "cv_accuracy": s["test_accuracy"].mean(), "cv_accuracy_std": s["test_accuracy"].std(),
                     "cv_f1_macro": s["test_f1_macro"].mean(),
                     "test_accuracy": accuracy_score(yte, p),
                     "test_precision_macro": precision_score(yte, p, average="macro"),
                     "test_recall_macro": recall_score(yte, p, average="macro"),
                     "test_f1_macro": f1_score(yte, p, average="macro"),
                     "noisy_test_accuracy": accuracy_score(yte, pn),
                     "noisy_test_top3_accuracy": float(np.mean([yy in np.argsort(-pr)[:3] for yy, pr in zip(yte, m.predict_proba(Xte_noisy))])),
                     "train_seconds": time.time() - t, "predict_ms": latency})
        fitted[name] = m
        print(f"{name:22s} CV acc {rows[-1]['cv_accuracy']:.4f}  test acc {rows[-1]['test_accuracy']:.4f}  "
              f"noisy acc {rows[-1]['noisy_test_accuracy']:.4f}  noisy top-3 {rows[-1]['noisy_test_top3_accuracy']:.4f}")
    comp = pd.DataFrame(rows)
    # Choose on cross-validation F1, tie-break on robustness to measurement error (never on the test set)
    best = comp.sort_values(["cv_f1_macro", "noisy_test_accuracy"], ascending=False).iloc[0]["model"]
    comp["selected"] = comp.model.eq(best)
    comp.round(4).to_csv(f"{OUT}/crop_model_comparison.csv", index=False)
    m = fitted[best]
    print("\nSelected:", best)

    p = m.predict(Xte)
    rep = pd.DataFrame(classification_report(yte, p, target_names=le.classes_, output_dict=True)).T
    rep.round(4).to_csv(f"{OUT}/crop_classification_report.csv")
    cm = confusion_matrix(yte, p)
    pd.DataFrame(cm, index=le.classes_, columns=le.classes_).to_csv(f"{OUT}/crop_confusion_matrix.csv")
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.imshow(cm, cmap="Greens")
    ax.set_xticks(range(len(le.classes_)), le.classes_, rotation=90)
    ax.set_yticks(range(len(le.classes_)), le.classes_)
    for i in range(len(cm)):
        for j in range(len(cm)):
            if cm[i, j]:
                ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=7,
                        color="white" if cm[i, j] > cm.max() / 2 else "black")
    ax.set_xlabel("Predicted crop"); ax.set_ylabel("Actual crop")
    ax.set_title(f"Crop recommendation - confusion matrix ({best}, test set)")
    fig.tight_layout(); fig.savefig(f"{OUT}/crop_confusion_matrix.png", dpi=130); plt.close(fig)

    # Which inputs matter most: permutation importance on the noisy test set
    pi = permutation_importance(m, Xte_noisy, yte, n_repeats=10, random_state=SEED, scoring="accuracy")
    imp = pd.DataFrame({"feature": FEATURES, "importance": pi.importances_mean, "std": pi.importances_std}
                       ).sort_values("importance", ascending=False)
    imp.round(4).to_csv(f"{OUT}/crop_feature_importance.csv", index=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(imp.feature[::-1], imp.importance[::-1], color="#3b7d3e")
    ax.set_xlabel("Drop in accuracy when the input is shuffled")
    ax.set_title("Which inputs drive the crop recommendation")
    fig.tight_layout(); fig.savefig(f"{OUT}/crop_feature_importance.png", dpi=130); plt.close(fig)

    # Retrain on all data for deployment; keep each crop's observed ranges for explanations
    final = models()[best].fit(X, y)
    ranges = df.groupby("label")[FEATURES].quantile([0.05, 0.95]).unstack()
    joblib.dump({"model": final, "label_encoder": le, "features": FEATURES, "model_name": best,
                 "crop_ranges": ranges}, f"{OUT}/crop_model.pkl")
    print(f"Saved {OUT}/crop_model.pkl")


if __name__ == "__main__":
    main()
