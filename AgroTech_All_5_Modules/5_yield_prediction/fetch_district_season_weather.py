"""
Weather features for the yield model: one row per Karnataka district x crop year x season.
Downloads daily NASA POWER data for each district's centre point (30 requests, free, no key).

Crop year Y in the APY statistics = agricultural year Y-(Y+1), so seasons are:
    Kharif      Jun-Oct of Y
    Rabi        Nov Y - Mar Y+1
    Summer      Mar-May of Y+1
    Whole Year  Jun Y - May Y+1
    Autumn      Jul-Oct of Y        Winter  Nov Y - Feb Y+1

Usage:   pip install pandas requests
         python fetch_district_season_weather.py
Output:  district_season_weather.csv   (train_yield_model.py uses it automatically)
"""
import time
import requests
import pandas as pd

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = {"T2M_MAX": "tmax", "T2M_MIN": "tmin", "RH2M": "rh", "PRECTOTCORR": "rain",
          "ALLSKY_SFC_SW_DWN": "solar", "GWETROOT": "soil_moist"}
SEASONS = {"Kharif": (6, 0, 10, 0), "Rabi": (11, 0, 3, 1), "Summer": (3, 1, 5, 1),
           "Whole Year": (6, 0, 5, 1), "Autumn": (7, 0, 10, 0), "Winter": (11, 0, 2, 1)}


def fetch(lat, lon, start="19970101", end="20161231"):
    r = requests.get(URL, params={"parameters": ",".join(PARAMS), "community": "AG", "latitude": lat,
                                  "longitude": lon, "start": start, "end": end, "format": "JSON"}, timeout=300)
    r.raise_for_status()
    p = r.json()["properties"]["parameter"]
    df = pd.DataFrame({v: pd.Series(p[k]) for k, v in PARAMS.items()})
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    return df.replace(-999, pd.NA).astype(float)


def longest_dry_spell(rain):
    run = best = 0
    for x in rain.fillna(0):
        run = run + 1 if x < 2.5 else 0     # < 2.5 mm/day counts as dry (IMD 'rainy day' threshold)
        best = max(best, run)
    return best


def season_rows(w, district):
    rows = []
    for y in range(1997, 2016):
        for s, (m1, o1, m2, o2) in SEASONS.items():
            a = pd.Timestamp(y + o1, m1, 1)
            b = pd.Timestamp(y + o2, m2, 1) + pd.offsets.MonthEnd(0)
            x = w.loc[a:b]
            if len(x) < 25:
                continue
            rows.append(dict(district=district, crop_year=y, season=s,
                             rain_total_mm=round(x.rain.sum(), 1),
                             rainy_days=int((x.rain >= 2.5).sum()),
                             longest_dry_spell_days=longest_dry_spell(x.rain),
                             tmax_mean=round(x.tmax.mean(), 2), tmin_mean=round(x.tmin.mean(), 2),
                             hot_days_over_35=int((x.tmax > 35).sum()),
                             rh_mean=round(x.rh.mean(), 1), solar_mean=round(x.solar.mean(), 2),
                             soil_moist_mean=round(x.soil_moist.mean(), 3)))
    return rows


def main():
    prof = pd.read_csv("karnataka_district_profile.csv")
    out = []
    for r in prof.itertuples():
        print("Downloading", r.district)
        out += season_rows(fetch(r.lat, r.lon), r.district)
        time.sleep(1)
    pd.DataFrame(out).to_csv("district_season_weather.csv", index=False)
    print("Saved district_season_weather.csv", len(out), "rows")


if __name__ == "__main__":
    main()
