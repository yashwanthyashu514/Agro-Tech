# Crop Recommendation Model (Random Forest)
pip install pandas numpy scikit-learn xgboost lightgbm matplotlib joblib
Retrain:  python train_crop_model.py
Model:    models/crop_model.pkl

import joblib, pandas as pd
b = joblib.load("models/crop_model.pkl")
x = pd.DataFrame([{"N":80,"P":45,"K":20,"temperature":24.5,"humidity":66,"ph":6.6,"rainfall":85}])
probs = b["model"].predict_proba(x[b["features"]])[0]
print(sorted(zip(b["label_encoder"].classes_, probs), key=lambda t: -t[1])[:5])
