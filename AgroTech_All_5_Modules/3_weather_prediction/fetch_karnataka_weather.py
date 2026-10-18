"""
Step 1: download daily weather (1991-2025) for the centre of all 30 Karnataka districts
from NASA POWER (free, no key). Takes about 5-10 minutes.

    pip install pandas requests
    python fetch_karnataka_weather.py
Output: weather_karnataka_districts.csv  (one row per district per day)

Needs karnataka_district_profile.csv (district name + centre latitude/longitude) in the same folder.
If the download stops halfway, just run it again - finished districts are skipped.
"""
import os
import time
import requests
import pandas as pd

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = {"T2M_MIN": "temp_min_c", "T2M_MAX": "temp_max_c", "RH2M": "humidity_pct",
          "PRECTOTCORR": "rainfall_mm", "WS2M": "wind_speed_ms", "ALLSKY_SFC_SW_DWN": "solar_rad_mj_m2",
          "GWETROOT": "soil_moisture_root"}
START, END = "19910101", "20251231"
PARTS = "weather_parts"


def fetch(name, lat, lon):
    for attempt in range(4):
        try:
            r = requests.get(URL, params={"parameters": ",".join(PARAMS), "community": "AG", "latitude": lat,
                                          "longitude": lon, "start": START, "end": END, "format": "JSON"},
                             timeout=300)
            r.raise_for_status()
            p = r.json()["properties"]["parameter"]
            df = pd.DataFrame({v: pd.Series(p[k]) for k, v in PARAMS.items()})
            df.index = pd.to_datetime(df.index, format="%Y%m%d")
            df = df.replace(-999, pd.NA).astype(float).rename_axis("date").reset_index()
            df.insert(0, "district", name)
            df.insert(1, "latitude", lat)
            df.insert(2, "longitude", lon)
            return df
        except Exception as e:
            print(f"   retry {attempt + 1} for {name}: {e}")
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"Could not download {name}")


def main():
    os.makedirs(PARTS, exist_ok=True)
    prof = pd.read_csv("karnataka_district_profile.csv")
    for i, r in enumerate(prof.itertuples(), 1):
        path = f"{PARTS}/{r.district}.csv"
        if os.path.exists(path):
            continue
        print(f"[{i}/{len(prof)}] {r.district}")
        fetch(r.district, r.lat, r.lon).round(3).to_csv(path, index=False)
        time.sleep(2)
    allw = pd.concat([pd.read_csv(f"{PARTS}/{d}.csv") for d in prof.district])
    allw.to_csv("weather_karnataka_districts.csv", index=False)
    print(f"Saved weather_karnataka_districts.csv: {len(allw):,} rows, {allw.district.nunique()} districts")


if __name__ == "__main__":
    main()
