"""
Step 3: 15-day weather forecast for any Karnataka district or taluk.

    python forecast_karnataka_weather.py --district Davanagere
    python forecast_karnataka_weather.py --taluk Harapanahalli
    python forecast_karnataka_weather.py --all          # every district -> forecast_karnataka_all.csv

The forecast starts the day after the last date in weather_karnataka_districts.csv.
For a live forecast, re-run fetch_karnataka_weather.py after setting END to yesterday
(and deleting the weather_parts folder) so the history is up to date.
"""
import argparse
import joblib
import pandas as pd
from train_karnataka_weather_model import load, forecast

ap = argparse.ArgumentParser()
ap.add_argument("--district")
ap.add_argument("--taluk")
ap.add_argument("--all", action="store_true")
a = ap.parse_args()

bundle = joblib.load("models/weather_model_karnataka.pkl")
history, _ = load()
if a.all:
    fc = pd.concat([forecast(bundle, history, d) for d in bundle["districts"].index])
    fc.to_csv("forecast_karnataka_all.csv", index=False)
    print(fc[fc.days_ahead == 1].to_string(index=False))
    print("\nSaved forecast_karnataka_all.csv")
else:
    district = a.district
    if a.taluk:
        ts = pd.read_csv("karnataka_taluk_soil.csv")
        m = ts[ts.taluk.str.lower() == a.taluk.lower()]
        if m.empty:
            raise SystemExit(f"Taluk {a.taluk} not found")
        district = m.district.iat[0]
        print(f"{a.taluk} is in {district} district")
    fc = forecast(bundle, history, district)
    print(fc.to_string(index=False))
    fc.to_csv(f"forecast_{district.lower().replace(' ', '_')}.csv", index=False)
