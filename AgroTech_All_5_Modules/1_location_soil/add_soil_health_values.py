"""
Adds real soil-test values (pH, N, P, K, organic carbon, EC, S, Zn, Fe, Cu, Mn, B)
to karnataka_location_soil.csv, using the Soil Health Card dataset.

STEP 1 - Download (free) the Karnataka Soil Health Card file:
    https://dataful.in/datasets/24072/
    "Soil Health Data: District and Village wise Soil Health Information for Karnataka"
    (Ministry of Agriculture & Farmers Welfare; ~6 lakh soil samples with GPS)
    Save it next to this script as CSV, XLSX or Parquet.

STEP 2 - Run:
    pip install pandas scipy openpyxl pyarrow
    python add_soil_health_values.py <downloaded_file>

OUTPUT:
    karnataka_location_soil_full.csv  - each village/post office + median soil values of the
                                        soil samples within RADIUS_KM of it (falls back to taluk medians)
    karnataka_taluk_soil_values.csv   - median soil values per taluk
"""
import sys, re
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

RADIUS_KM = 5          # use soil samples within this distance of the village
MIN_SAMPLES = 5        # need at least this many samples, otherwise use the taluk median

# Keyword patterns to find each column, whatever the exact header spelling is
PATTERNS = {
    "n_kg_ha": r"^(n|nitrogen|available_?n)\b|nitrogen",
    "p_kg_ha": r"^(p|phosphorus|phosphorous|available_?p)\b|phosph",
    "k_kg_ha": r"^(k|potassium|available_?k)\b|potass",
    "ph": r"^ph\b|^p_?h$",
    "oc_pct": r"^oc\b|organic",
    "ec_ds_m": r"^ec\b|electric|conductiv",
    "s_ppm": r"^s\b|sulph|sulfur",
    "zn_ppm": r"^zn\b|zinc",
    "fe_ppm": r"^fe\b|iron",
    "cu_ppm": r"^cu\b|copper",
    "mn_ppm": r"^mn\b|mangan",
    "b_ppm": r"^b\b|boron",
    "latitude": r"^lat",
    "longitude": r"^lon|^lng",
}
# Sanity limits - values outside are treated as lab/entry errors
LIMITS = {"ph": (3, 11), "oc_pct": (0, 10), "ec_ds_m": (0, 20), "n_kg_ha": (0, 2000),
          "p_kg_ha": (0, 500), "k_kg_ha": (0, 3000), "s_ppm": (0, 500), "zn_ppm": (0, 100),
          "fe_ppm": (0, 500), "cu_ppm": (0, 100), "mn_ppm": (0, 500), "b_ppm": (0, 50)}


def load(path):
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    if path.endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    return pd.read_csv(path, low_memory=False)


def find_columns(df):
    cols, used = {}, set()
    norm = {c: re.sub(r"[^a-z0-9_]", "", str(c).lower().replace(" ", "_")) for c in df.columns}
    for target, pat in PATTERNS.items():
        for c, n in norm.items():
            if c not in used and re.search(pat, n):
                cols[target] = c
                used.add(c)
                break
    return cols


def main(path):
    shc = load(path)
    cols = find_columns(shc)
    print("Detected columns:", {k: v for k, v in cols.items()})
    missing = [c for c in ("latitude", "longitude", "ph") if c not in cols]
    if missing:
        sys.exit(f"Could not find {missing}. Edit PATTERNS at the top of this script to match: {list(shc.columns)}")

    s = pd.DataFrame({t: pd.to_numeric(shc[c], errors="coerce") for t, c in cols.items()})
    for c, (lo, hi) in LIMITS.items():
        if c in s:
            s.loc[~s[c].between(lo, hi), c] = np.nan
    s = s[s.latitude.between(11, 19) & s.longitude.between(74, 79)]   # Karnataka bounding box
    values = [c for c in LIMITS if c in s]
    print(f"{len(s):,} soil samples with valid GPS")

    loc = pd.read_csv("karnataka_location_soil.csv")
    tal = pd.read_csv("karnataka_taluk_soil.csv")

    # Give every soil sample a taluk = taluk of its nearest village/post office
    lg = loc.dropna(subset=["latitude", "longitude"])
    tree_loc = cKDTree(np.radians(lg[["latitude", "longitude"]].values))
    _, i = tree_loc.query(np.radians(s[["latitude", "longitude"]].values))
    s["taluk"] = lg.taluk.values[i]
    taluk_vals = s.groupby("taluk")[values].median().round(2).add_prefix("taluk_median_")
    taluk_vals["taluk_samples"] = s.groupby("taluk").size()
    tal.merge(taluk_vals, left_on="taluk", right_index=True, how="left").to_csv(
        "karnataka_taluk_soil_values.csv", index=False)

    # Village-level: median of samples within RADIUS_KM
    tree = cKDTree(np.radians(s[["latitude", "longitude"]].values))
    r = RADIUS_KM / 6371.0
    out_rows = []
    for lat, lon in loc[["latitude", "longitude"]].itertuples(index=False):
        if np.isnan(lat):
            out_rows.append({})
            continue
        idx = tree.query_ball_point(np.radians([lat, lon]), r)
        if len(idx) >= MIN_SAMPLES:
            row = s.iloc[idx][values].median().round(2).to_dict()
            row["soil_samples_used"], row["soil_value_level"] = len(idx), f"within {RADIUS_KM} km"
        else:
            row = {}
        out_rows.append(row)
    v = pd.DataFrame(out_rows, index=loc.index)
    full = pd.concat([loc, v], axis=1)
    # Fallback to taluk median where the village had too few nearby samples
    full = full.merge(taluk_vals, left_on="taluk", right_index=True, how="left")
    for c in values:
        if c not in full:
            full[c] = np.nan
        fb = full[c].isna()
        full.loc[fb, c] = full.loc[fb, "taluk_median_" + c]
        full.loc[fb & full[c].notna(), "soil_value_level"] = "taluk median"
    full = full.drop(columns=[c for c in full if c.startswith("taluk_median_")] + ["taluk_samples"])
    full.to_csv("karnataka_location_soil_full.csv", index=False)
    print("Saved karnataka_location_soil_full.csv and karnataka_taluk_soil_values.csv")
    print(full.soil_value_level.value_counts(dropna=False))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
