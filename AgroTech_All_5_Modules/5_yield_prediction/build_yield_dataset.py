"""
Builds the historical crop-yield dataset for the yield-prediction model.

Source: Government of India, Directorate of Economics & Statistics - district-wise, season-wise
crop Area-Production-Yield (APY) statistics 1997-2015 (data.gov.in), copy from
github.com/renukadhule/crop_production_python_analysis  ("crop_production Dataset.csv").

Outputs
  yield_india_clean.csv        all states, cleaned, yield in tonnes/hectare
  yield_karnataka_features.csv Karnataka + model features (history, soil, agro-zone, location)
  karnataka_district_profile.csv  district centroid, agro-zone, soil-type shares
"""
import numpy as np
import pandas as pd

SRC = "y_crop_production_python_analysis/crop_production Dataset.csv"

# APY district spellings -> current official names (same as karnataka_location_soil.csv)
KA_DISTRICTS = {
    "BAGALKOT": "Bagalkot", "BANGALORE RURAL": "Bengaluru Rural", "BELGAUM": "Belagavi", "BELLARY": "Ballari",
    "BENGALURU URBAN": "Bengaluru Urban", "BIDAR": "Bidar", "BIJAPUR": "Vijayapura",
    "CHAMARAJANAGAR": "Chamarajanagar", "CHIKBALLAPUR": "Chikkaballapur", "CHIKMAGALUR": "Chikkamagaluru",
    "CHITRADURGA": "Chitradurga", "DAKSHIN KANNAD": "Dakshina Kannada", "DAVANGERE": "Davanagere",
    "DHARWAD": "Dharwad", "GADAG": "Gadag", "GULBARGA": "Kalaburagi", "HASSAN": "Hassan", "HAVERI": "Haveri",
    "KODAGU": "Kodagu", "KOLAR": "Kolar", "KOPPAL": "Koppal", "MANDYA": "Mandya", "MYSORE": "Mysuru",
    "RAICHUR": "Raichur", "RAMANAGARA": "Ramanagara", "SHIMOGA": "Shivamogga", "TUMKUR": "Tumakuru",
    "UDUPI": "Udupi", "UTTAR KANNAD": "Uttara Kannada", "YADGIR": "Yadgir",
}
# APY crop names -> names used in the crop recommendation / growth datasets
CROP_KEY = {
    "Rice": "rice", "Maize": "maize", "Jowar": "sorghum", "Ragi": "finger millet", "Bajra": "pearl millet",
    "Wheat": "wheat", "Gram": "chickpea", "Arhar/Tur": "pigeonpeas", "Moong(Green Gram)": "mungbean",
    "Urad": "blackgram", "Moth": "mothbeans", "Masoor": "lentil", "Rajmash Kholar": "kidneybeans",
    "Groundnut": "groundnut", "Soyabean": "soybean", "Sunflower": "sunflower", "Cotton(lint)": "cotton",
    "Jute": "jute", "Sugarcane": "sugarcane", "Potato": "potato", "Onion": "onion", "Tomato": "tomato",
    "Dry chillies": "chilli", "Banana": "banana", "Papaya": "papaya", "Mango": "mango", "Grapes": "grapes",
    "Pome Granet": "pomegranate", "Water Melon": "watermelon", "Coffee": "coffee", "Arecanut": "arecanut",
    "Horse-gram": "horsegram", "Cowpea(Lobia)": "cowpea", "Sesamum": "sesame", "Castor seed": "castor",
    "Safflower": "safflower", "Turmeric": "turmeric",
}
# Production reported in bales, not tonnes
BALES_KG = {"Cotton(lint)": 170, "Jute": 180, "Mesta": 180, "Jute & mesta": 180}
DROP = {"Coconut "}   # production reported in number of nuts


def clean():
    d = pd.read_csv(SRC)
    d.columns = ["state", "district", "crop_year", "season", "crop", "area_ha", "production_t"]
    d["season"] = d.season.str.strip()
    d["state"] = d.state.str.strip()
    d = d[~d.crop.isin(DROP)]
    for c, kg in BALES_KG.items():
        d.loc[d.crop == c, "production_t"] *= kg / 1000
    n0 = len(d)
    d = d.dropna(subset=["area_ha", "production_t"])
    d = d[(d.area_ha >= 10) & (d.production_t > 0)]          # tiny areas give unreliable yields
    d["yield_t_ha"] = d.production_t / d.area_ha
    # Remove implausible yields: > 10x away from the crop's median (data-entry errors)
    lg = np.log(d.yield_t_ha)
    med = lg.groupby(d.crop).transform("median")
    d = d[(lg - med).abs() <= np.log(10)]
    d = d.drop_duplicates(["state", "district", "crop_year", "season", "crop"])
    d["crop"] = d.crop.str.strip()
    d["crop_key"] = d.crop.map(CROP_KEY)
    d["yield_t_ha"] = d.yield_t_ha.round(4)
    print(f"India: {n0:,} rows -> {len(d):,} after cleaning")
    d.to_csv("yield_india_clean.csv", index=False)
    return d


def district_profile():
    loc = pd.read_csv("karnataka_location_soil.csv")
    g = loc.groupby("district")
    prof = pd.DataFrame({
        "lat": g.latitude.mean().round(4), "lon": g.longitude.mean().round(4),
        "agro_zone_no": g.agro_zone_no.agg(lambda s: s.mode().iat[0]),
        "soil_black_share": g.dominant_soil.apply(lambda s: (s == "Black").mean()).round(3),
        "soil_red_share": g.dominant_soil.apply(lambda s: s.str.contains("Red sandy|Red loamy|Red clay").mean()).round(3),
        "soil_lateritic_share": g.dominant_soil.apply(lambda s: s.str.contains("lateritic|Lateritic").mean()).round(3),
        "zone_rainfall_mid_mm": ((g.zone_rainfall_min_mm.mean() + g.zone_rainfall_max_mm.mean()) / 2).round(0),
    }).reset_index()
    prof.to_csv("karnataka_district_profile.csv", index=False)
    return prof


def features(d, prof):
    k = d[d.state == "Karnataka"].copy()
    k["district"] = k.district.map(KA_DISTRICTS)
    k = k.sort_values(["district", "crop", "season", "crop_year"])
    grp = k.groupby(["district", "crop", "season"])
    # History features use ONLY earlier years (no leakage)
    k["prev_year"] = grp.crop_year.shift(1)
    k["yield_lag1"] = grp.yield_t_ha.shift(1).where(k.crop_year - k.prev_year == 1)
    k["yield_mean_prev3"] = grp.yield_t_ha.transform(lambda s: s.shift(1).rolling(3, min_periods=2).mean())
    k["area_lag1"] = grp.area_ha.shift(1)
    # Same crop's state-wide median yield last year (captures statewide good/bad years)
    st = k.groupby(["crop", "season", "crop_year"]).yield_t_ha.median().rename("state_median_yield")
    st = st.reset_index()
    st["crop_year"] += 1
    k = k.merge(st.rename(columns={"state_median_yield": "state_yield_lag1"}), on=["crop", "season", "crop_year"], how="left")
    k = k.drop(columns=["prev_year"]).merge(prof, on="district", how="left")
    k["years_since_1997"] = k.crop_year - 1997
    k.to_csv("yield_karnataka_features.csv", index=False)
    print(f"Karnataka: {len(k):,} rows, {k.crop.nunique()} crops, {k.district.nunique()} districts, "
          f"{k.crop_year.min()}-{k.crop_year.max()}")
    return k


if __name__ == "__main__":
    d = clean()
    features(d, district_profile())
