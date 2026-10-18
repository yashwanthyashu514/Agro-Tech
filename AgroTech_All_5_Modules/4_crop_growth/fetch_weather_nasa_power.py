"""
Download daily historical weather for one location from NASA POWER
(free, no API key) and save it as a CSV ready for the AgroTech project.

Usage:
    pip install pandas requests
    python fetch_weather_nasa_power.py                      # Davanagere, 1991-2025
    python fetch_weather_nasa_power.py --name Mysuru --lat 12.30 --lon 76.64

Output columns:
    date, location, latitude, longitude,
    temp_min_c, temp_max_c, temp_avg_c, humidity_pct,
    rainfall_mm, rain_occurred, rainfall_category,
    wind_speed_ms, solar_rad_mj_m2, soil_moisture_surface, soil_moisture_root, season

Rainfall category follows IMD's daily rainfall terminology.
Zero-rainfall days are KEPT on purpose (they capture dry spells).
"""
import argparse
import requests
import pandas as pd

PARAMS = {
    "T2M_MIN": "temp_min_c",
    "T2M_MAX": "temp_max_c",
    "T2M": "temp_avg_c",
    "RH2M": "humidity_pct",
    "PRECTOTCORR": "rainfall_mm",
    "WS2M": "wind_speed_ms",
    "ALLSKY_SFC_SW_DWN": "solar_rad_mj_m2",
    "GWETTOP": "soil_moisture_surface",   # 0-1 (0 = dry, 1 = saturated), top ~5 cm
    "GWETROOT": "soil_moisture_root",     # 0-1, root zone (~1 m)
}
URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def imd_category(mm):
    """IMD daily rainfall terminology (mm/day)."""
    if pd.isna(mm):
        return None
    if mm == 0:
        return "No rain"
    if mm < 2.5:
        return "Very light"
    if mm < 15.6:
        return "Light"
    if mm < 64.5:
        return "Moderate"
    if mm < 115.6:
        return "Heavy"
    if mm < 204.5:
        return "Very heavy"
    return "Extremely heavy"


def indian_season(month):
    """Agricultural season by month (broad, adjust for your state)."""
    if month in (6, 7, 8, 9, 10):
        return "Kharif"
    if month in (11, 12, 1, 2, 3):
        return "Rabi"
    return "Zaid"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="Davanagere")
    ap.add_argument("--lat", type=float, default=14.4644)
    ap.add_argument("--lon", type=float, default=75.9218)
    ap.add_argument("--start", default="19910101")
    ap.add_argument("--end", default="20251231")
    a = ap.parse_args()

    r = requests.get(URL, params={
        "parameters": ",".join(PARAMS),
        "community": "AG",
        "latitude": a.lat,
        "longitude": a.lon,
        "start": a.start,
        "end": a.end,
        "format": "JSON",
    }, timeout=300)
    r.raise_for_status()
    data = r.json()["properties"]["parameter"]

    df = pd.DataFrame({PARAMS[p]: pd.Series(data[p]) for p in PARAMS})
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df = df.replace(-999, pd.NA).astype(float)   # -999 = missing in NASA POWER
    df.index.name = "date"
    df = df.reset_index()

    # Rain below 0.1 mm is treated as no rain (trace amounts)
    df["rainfall_mm"] = df["rainfall_mm"].where(df["rainfall_mm"] >= 0.1, 0.0)
    df["rain_occurred"] = (df["rainfall_mm"] > 0).astype(int)
    df["rainfall_category"] = df["rainfall_mm"].apply(imd_category)
    df["season"] = df["date"].dt.month.apply(indian_season)
    df.insert(1, "location", a.name)
    df.insert(2, "latitude", a.lat)
    df.insert(3, "longitude", a.lon)

    out = f"weather_{a.name.lower()}_{a.start[:4]}_{a.end[:4]}.csv"
    df.round(2).to_csv(out, index=False)
    print(f"Saved {len(df)} days to {out}")
    print(df["rainfall_category"].value_counts())


if __name__ == "__main__":
    main()
