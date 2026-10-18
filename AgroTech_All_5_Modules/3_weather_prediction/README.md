# Weather Prediction Model - whole Karnataka (30 districts, one model)

## Install (once)
pip install pandas numpy scikit-learn xgboost joblib requests

## Step 1 - download weather for all 30 districts, 1991-2025 (needs internet, 5-10 min)
python fetch_karnataka_weather.py
-> weather_karnataka_districts.csv   (~3.8 lakh rows)
If it stops halfway, run it again - it continues where it stopped.

## Step 2 - train (15-40 min on a normal laptop)
python train_karnataka_weather_model.py
-> models/weather_model_karnataka.pkl             the trained model
-> models/weather_model_comparison_karnataka.csv  model vs baselines, 1/3/7 days ahead
-> models/weather_accuracy_by_district.csv         test error for each district

## Step 3 - forecast
python forecast_karnataka_weather.py --district Davanagere
python forecast_karnataka_weather.py --taluk Harapanahalli
python forecast_karnataka_weather.py --all

For each of the next 7 days: rain probability (%), expected rain (mm), max/min temperature,
humidity (with 80% range). Days 8-15 use the long-term average for that date.
Rain day = 2.5 mm or more (IMD definition).

## ALREADY TRAINED (models/weather_model_karnataka.pkl)
Trained on 30 districts x 1991-2025 (3,83,520 days). Test = 2019-2025.
Put weather_karnataka_districts.csv (your download) in this folder, then just run Step 3.
Results: models/weather_model_comparison_karnataka.csv, weather_accuracy_by_district.csv,
         weather_model_results.png
