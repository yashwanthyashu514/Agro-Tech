# AgroTech – AI Agriculture Intelligence System (all 5 modules)

Install once:
  pip install pandas numpy scikit-learn xgboost lightgbm matplotlib joblib scipy requests

| Folder | Module | Type | Ready-to-use output |
|---|---|---|---|
| 1_location_soil      | Location & soil intelligence | Data lookup (no training)   | karnataka_location_soil.csv, karnataka_taluk_soil.csv |
| 2_crop_recommendation| Crop recommendation          | ML – Random Forest (trained)| models/crop_model.pkl |
| 3_weather_prediction | Weather prediction (7 days)  | ML – XGBoost (trained)      | models/weather_model_karnataka.pkl |
| 4_crop_growth        | Crop growth stages           | Heat-unit calculation       | crop_growth_stages.csv + predict_growth_stages.py |
| 5_yield_prediction   | Yield prediction (t/ha)      | ML – XGBoost (trained)      | yield_model.pkl |
| agro_engine          | All modules together         | –                           | agro_engine.py |

## Try everything at once
  cd agro_engine
  python agro_engine.py --taluk Davanagere --season Kharif --N 80 --P 45 --K 20 --ph 6.6
  (add --json for app/API output)

## Each module on its own
  1: python build_location_soil.py            (rebuild tables) / add_soil_health_values.py <SHC file>
  2: python train_crop_model.py               (retrain + compare 6 algorithms)
  3: python forecast_karnataka_weather.py --district Davanagere
     python train_karnataka_weather_model.py  (retrain, ~15-40 min)
  4: python predict_growth_stages.py --crop maize --sow 2026-06-20 --weather <one-district weather csv>
  5: python train_yield_model.py              (retrain + compare vs baselines)

Each module folder has its result tables / charts for the project report.
