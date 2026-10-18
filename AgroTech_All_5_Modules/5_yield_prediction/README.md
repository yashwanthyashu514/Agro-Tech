# Yield Prediction Model (XGBoost, tonnes/hectare)
pip install pandas numpy scikit-learn xgboost joblib requests
Retrain:  python train_yield_model.py
Model:    yield_model.pkl  -> output is log1p(yield); apply numpy.expm1() to get t/ha
Add weather later: python fetch_district_season_weather.py, then retrain.
