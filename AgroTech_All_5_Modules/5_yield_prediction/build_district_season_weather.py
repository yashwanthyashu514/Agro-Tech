"""Season weather features for the yield model, built from weather_karnataka_districts.csv
(so no second download is needed). Output: district_season_weather.csv"""
import pandas as pd
from fetch_district_season_weather import season_rows

d = pd.read_csv("weather_karnataka_districts.csv", parse_dates=["date"])
d = d.rename(columns={"temp_max_c": "tmax", "temp_min_c": "tmin", "humidity_pct": "rh", "rainfall_mm": "rain",
                      "solar_rad_mj_m2": "solar", "soil_moisture_root": "soil_moist"})
rows = []
for name, g in d.groupby("district"):
    rows += season_rows(g.set_index("date"), name)
out = pd.DataFrame(rows)
out.to_csv("district_season_weather.csv", index=False)
print(f"Saved district_season_weather.csv: {len(out):,} rows")
