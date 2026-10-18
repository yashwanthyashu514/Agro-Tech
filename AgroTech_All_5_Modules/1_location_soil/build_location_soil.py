"""
Builds:
  1. india_locations.csv        - all-India: state, district, taluk, village/post office, pincode, lat/long
  2. karnataka_taluk_soil.csv   - 176 Karnataka taluks -> agro-climatic zone, soil types, rainfall
  3. karnataka_location_soil.csv- every Karnataka village/post office with cleaned taluk + zone + soil type
"""
import bz2, json, os, re, difflib
import numpy as np
import pandas as pd
import indiapins
from scipy.spatial import cKDTree

SRC_TALUK = "pin_repo/all-india-pincode-html-csv.csv"   # github.com/saravanakumargn/All-India-Pincode-Directory
SRC_GEO = os.path.join(os.path.dirname(indiapins.__file__), "pins.json.bz2")  # PyPI indiapins (India Post + GPS)

# ---------------------------------------------------------------------------
# Karnataka agro-climatic zones (UAS / KSDA classification).
# Soil text and rainfall: NDDB Dairy Knowledge Portal table of Karnataka zones.
# Taluk lists for zones 4-7: UAS Bangalore agro-climatic zone page.
# ---------------------------------------------------------------------------
ZONES = {
    1: ("North Eastern Transition Zone", "Black", "Red lateritic",
        "Shallow to medium black clay soils in major areas; red lateritic soils in remaining areas", 829, 919),
    2: ("North Eastern Dry Zone", "Black", "Black (shallow-medium)",
        "Deep to very deep black clay soils in major areas; shallow to medium black soils in minor pockets", 633, 806),
    3: ("Northern Dry Zone", "Black", "Sandy loam",
        "Black clay, medium and deep, in major areas; sandy loams in remaining areas", 464, 785),
    4: ("Central Dry Zone", "Red sandy loam", "Black",
        "Red sandy loams in major areas; shallow to deep black soil in remaining areas", 455, 717),
    5: ("Eastern Dry Zone", "Red loamy", "Lateritic",
        "Red loamy soils in major areas; clay lateritic soils in remaining areas", 679, 888),
    6: ("Southern Dry Zone", "Red sandy loam", "Black",
        "Red sandy loams predominate, with black soils in remaining areas", 670, 888),
    7: ("Southern Transition Zone", "Red sandy loam", "Red loamy",
        "Red sandy loams in major areas; red loamy soils in remaining areas", 611, 1053),
    8: ("Northern Transition Zone", "Black", "Red sandy loam",
        "Shallow to medium black clay soils and red sandy loam soils in equal proportion", 618, 1303),
    9: ("Hilly Zone", "Red clay loam", "",
        "Red clay loamy soils in major areas", 904, 3695),
    10: ("Coastal Zone", "Red lateritic", "Coastal alluvial",
         "Red lateritic and coastal alluvial soils", 3010, 4694),
}

# district -> {taluk: zone}  (176 taluks, pre-2017 taluk boundaries)
TALUKS = {
    "Bidar": {"Aurad": 1, "Basavakalyan": 1, "Bhalki": 1, "Bidar": 1, "Humnabad": 1},
    "Kalaburagi": {"Aland": 1, "Chincholi": 1, "Afzalpur": 2, "Chittapur": 2, "Kalaburagi": 2, "Jewargi": 2, "Sedam": 2},
    "Yadgir": {"Shahapur": 2, "Shorapur": 2, "Yadgir": 2},
    "Raichur": {"Devadurga": 2, "Manvi": 2, "Raichur": 2, "Lingasugur": 3, "Sindhanur": 3},
    "Koppal": {"Gangavathi": 3, "Koppal": 3, "Kushtagi": 3, "Yelburga": 3},
    "Gadag": {"Gadag": 3, "Mundargi": 3, "Nargund": 3, "Ron": 3, "Shirahatti": 8},
    "Dharwad": {"Navalgund": 3, "Dharwad": 8, "Hubballi": 8, "Kundgol": 8, "Kalghatgi": 9},
    "Belagavi": {"Athani": 3, "Gokak": 3, "Raibag": 3, "Ramdurg": 3, "Saundatti": 3,
                 "Bailhongal": 8, "Belagavi": 8, "Chikkodi": 8, "Hukkeri": 8, "Khanapur": 9},
    "Vijayapura": {"Basavana Bagewadi": 3, "Vijayapura": 3, "Indi": 3, "Muddebihal": 3, "Sindgi": 3},
    "Bagalkot": {"Badami": 3, "Bagalkot": 3, "Bilagi": 3, "Hungund": 3, "Jamkhandi": 3, "Mudhol": 3},
    "Ballari": {"Ballari": 3, "Hoovina Hadagali": 3, "Hagaribommanahalli": 3, "Hosapete": 3,
                "Kudligi": 3, "Sandur": 3, "Siruguppa": 3},
    "Davanagere": {"Harapanahalli": 3, "Davanagere": 4, "Harihar": 4, "Jagalur": 4, "Channagiri": 7, "Honnali": 7},
    "Chitradurga": {"Challakere": 4, "Chitradurga": 4, "Hiriyur": 4, "Holalkere": 4, "Hosadurga": 4, "Molakalmuru": 4},
    "Tumakuru": {"Chikkanayakanahalli": 4, "Gubbi": 4, "Madhugiri": 4, "Pavagada": 4, "Sira": 4, "Tumakuru": 4,
                 "Koratagere": 5, "Kunigal": 6, "Tiptur": 6, "Turuvekere": 6},
    "Chikkamagaluru": {"Kadur": 4, "Tarikere": 7, "Chikkamagaluru": 9, "Koppa": 9, "Mudigere": 9,
                       "Narasimharajapura": 9, "Sringeri": 9},
    "Bengaluru Urban": {"Anekal": 5, "Bengaluru North": 5, "Bengaluru South": 5},
    "Bengaluru Rural": {"Devanahalli": 5, "Doddaballapura": 5, "Hoskote": 5, "Nelamangala": 5},
    "Ramanagara": {"Channapatna": 5, "Kanakapura": 5, "Magadi": 5, "Ramanagara": 5},
    "Kolar": {"Bangarapet": 5, "Kolar": 5, "Malur": 5, "Mulbagal": 5, "Srinivaspur": 5},
    "Chikkaballapur": {"Bagepalli": 5, "Chikkaballapur": 5, "Chintamani": 5, "Gauribidanur": 5,
                       "Gudibande": 5, "Sidlaghatta": 5},
    "Mysuru": {"Krishnarajanagara": 6, "Mysuru": 6, "Nanjangud": 6, "Tirumakudalu Narasipura": 6,
               "Heggadadevankote": 7, "Hunsur": 7, "Periyapatna": 7},
    "Chamarajanagar": {"Chamarajanagar": 6, "Gundlupet": 6, "Kollegal": 6, "Yelandur": 6},
    "Mandya": {"Krishnarajpet": 6, "Maddur": 6, "Malavalli": 6, "Mandya": 6, "Nagamangala": 6,
               "Pandavapura": 6, "Srirangapatna": 6},
    "Hassan": {"Arsikere": 6, "Channarayapatna": 6, "Hassan": 6, "Alur": 7, "Arkalgud": 7, "Belur": 7,
               "Holenarasipur": 7, "Sakleshpur": 9},
    "Shivamogga": {"Bhadravati": 7, "Shikaripura": 7, "Shivamogga": 7, "Hosanagara": 9, "Sagar": 9,
                   "Soraba": 9, "Thirthahalli": 9},
    "Haveri": {"Byadgi": 8, "Haveri": 8, "Hirekerur": 8, "Ranebennur": 8, "Savanur": 8, "Shiggaon": 8, "Hangal": 9},
    "Uttara Kannada": {"Haliyal": 9, "Joida": 9, "Mundgod": 9, "Siddapur": 9, "Sirsi": 9, "Yellapur": 9,
                       "Ankola": 10, "Bhatkal": 10, "Honnavar": 10, "Karwar": 10, "Kumta": 10},
    "Kodagu": {"Madikeri": 9, "Somwarpet": 9, "Virajpet": 9},
    "Udupi": {"Karkala": 10, "Kundapura": 10, "Udupi": 10},
    "Dakshina Kannada": {"Bantwal": 10, "Belthangady": 10, "Mangaluru": 10, "Puttur": 10, "Sullia": 10},
}

# Old names / postal spellings that fuzzy matching can't guess
ALIASES = {
    "gulbarga": "Kalaburagi", "hubli": "Hubballi", "belgaum": "Belagavi", "chikodi": "Chikkodi",
    "bijapur": "Vijayapura", "bbagewadi": "Basavana Bagewadi", "basavanabagevadi": "Basavana Bagewadi",
    "bellary": "Ballari", "hospet": "Hosapete", "hbhalli": "Hagaribommanahalli",
    "huvinahadagali": "Hoovina Hadagali", "hadagalli": "Hoovina Hadagali",
    "tumkur": "Tumakuru", "cnhalli": "Chikkanayakanahalli", "cnhally": "Chikkanayakanahalli",
    "chikmagalur": "Chikkamagaluru", "shimoga": "Shivamogga", "shikarpur": "Shikaripura", "sorab": "Soraba",
    "tirthahalli": "Thirthahalli", "mysore": "Mysuru", "krnagar": "Krishnarajanagara",
    "hdkote": "Heggadadevankote", "tnarasipura": "Tirumakudalu Narasipura", "piriyapatna": "Periyapatna",
    "krpete": "Krishnarajpet", "kepete": "Krishnarajpet", "mangalore": "Mangaluru", "bantval": "Bantwal",
    "sulya": "Sullia", "beltangadi": "Belthangady", "honavar": "Honnavar", "supa": "Joida",
    "sampgaon": "Bailhongal", "parasgad": "Saundatti", "londa": "Khanapur", "athni": "Athani",
    "raybag": "Raibag", "deodurga": "Devadurga", "yadgiri": "Yadgir", "shahpur": "Shahapur",
    "afjalpur": "Afzalpur", "homnabad": "Humnabad", "aurad(b)": "Aurad", "aurad b": "Aurad",
    "bilgi": "Bilagi", "chickballapur": "Chikkaballapur", "chikballapur": "Chikkaballapur",
    "gudibanda": "Gudibande", "bangarpet": "Bangarapet", "navunda": "Kundapura", "karkal": "Karkala",
    "davangere": "Davanagere", "davanangere": "Davanagere", "harihara": "Harihar",
    "chamarajanagara": "Chamarajanagar", "ramanagaram": "Ramanagara", "ramangaram": "Ramanagara",
    "bangalorenorth": "Bengaluru North", "bgnorth": "Bengaluru North",
    "bangaloresouth": "Bengaluru South", "bgsouth": "Bengaluru South",
    "dodballapura": "Doddaballapura", "dodballapur": "Doddaballapura", "hosakote": "Hoskote",
    "srinivasapura": "Srinivaspur", "bhadravathi": "Bhadravati", "lingsugur": "Lingasugur",
    "puttur(dk)": "Puttur", "kalghatagi": "Kalghatgi", "somvarpet": "Somwarpet",
}

TALUK_TO_DISTRICT = {t: d for d, ts in TALUKS.items() for t in ts}
TALUK_TO_ZONE = {t: z for ts in TALUKS.values() for t, z in ts.items()}
CANON_KEYS = {re.sub(r"[^a-z]", "", t.lower()): t for t in TALUK_TO_DISTRICT}


def key(s):
    return re.sub(r"[^a-z()]", "", str(s).lower().replace("taluk", "").replace(" tq", "").replace(" ho", ""))


def match_taluk(raw):
    if pd.isna(raw):
        return None
    k = key(raw)
    for cand in (k, k.replace("(", "").replace(")", "")):
        if cand in ALIASES:
            return ALIASES[cand]
        if cand in CANON_KEYS:
            return CANON_KEYS[cand]
    k2 = k.replace("(", "").replace(")", "")
    pool = list(CANON_KEYS) + [a.replace("(", "").replace(")", "") for a in ALIASES]
    best = difflib.get_close_matches(k2, pool, n=1, cutoff=0.8)
    if not best:
        return None
    b = best[0]
    return CANON_KEYS.get(b) or ALIASES.get(b) or next(v for a, v in ALIASES.items() if a.replace("(", "").replace(")", "") == b)


def office_key(s):
    return re.sub(r"[^a-z]", "", re.sub(r"\b(b\.?o|s\.?o|h\.?o)\b\.?", "", str(s).lower()))


def title(s):
    return str(s).strip().title() if pd.notna(s) else s


def main():
    # ---- all-India locations ------------------------------------------------
    a = pd.read_csv(SRC_TALUK, encoding="latin1")
    g = pd.DataFrame([json.loads(l) for l in bz2.open(SRC_GEO, "rt")])
    a["k"], g["k"] = a.officename.map(office_key), g.Name.map(office_key)
    g = g.drop_duplicates(["Pincode", "k"])
    m = a.merge(g[["Pincode", "k", "Latitude", "Longitude", "District"]],
                left_on=["pincode", "k"], right_on=["Pincode", "k"], how="left")
    # Fill missing GPS with the average of other offices in the same pincode
    for c in ("Latitude", "Longitude"):
        m[c] = m[c].fillna(m.groupby("pincode")[c].transform("mean"))
    # Drop impossible coordinates (outside India's bounding box)
    bad = ~m.Latitude.between(6, 37.5) | ~m.Longitude.between(68, 97.5)
    m.loc[bad, ["Latitude", "Longitude"]] = np.nan

    loc = pd.DataFrame({
        "state": m.statename.map(title),
        "district": m.District.fillna(m.Districtname).map(title),
        "taluk": m.Taluk.map(title),
        "village_or_post_office": m.officename.str.replace(r"\s*[BSH]\.O\.?$", "", regex=True).str.strip(),
        "office_type": m.officeType,
        "pincode": m.pincode,
        "latitude": m.Latitude.round(5),
        "longitude": m.Longitude.round(5),
    }).drop_duplicates()
    loc.to_csv("india_locations.csv", index=False)
    print("india_locations.csv:", len(loc), "rows,", f"{loc.latitude.notna().mean():.0%} with GPS")

    # ---- Karnataka taluk -> zone -> soil ---------------------------------------
    rows = []
    for d, ts in TALUKS.items():
        for t, z in ts.items():
            name, dom, sec, desc, rmin, rmax = ZONES[z]
            rows.append(dict(state="Karnataka", district=d, taluk=t, agro_zone_no=z, agro_zone=name,
                             dominant_soil=dom, secondary_soil=sec, soil_description=desc,
                             zone_rainfall_min_mm=rmin, zone_rainfall_max_mm=rmax))
    ts = pd.DataFrame(rows)
    ts.to_csv("karnataka_taluk_soil.csv", index=False)
    print("karnataka_taluk_soil.csv:", len(ts), "taluks")

    # ---- Karnataka villages with soil -----------------------------------------
    k = m[m.statename.str.upper() == "KARNATAKA"].copy()
    k["taluk_clean"] = k.Taluk.map(match_taluk)
    k["taluk_source"] = np.where(k.taluk_clean.notna(), "postal record", None)
    # Unmatched taluks -> taluk of the nearest matched post office
    has = k.taluk_clean.notna() & k.Latitude.notna()
    need = k.taluk_clean.isna() & k.Latitude.notna()
    if need.any():
        tree = cKDTree(k.loc[has, ["Latitude", "Longitude"]].values)
        _, idx = tree.query(k.loc[need, ["Latitude", "Longitude"]].values)
        k.loc[need, "taluk_clean"] = k.loc[has, "taluk_clean"].values[idx]
        k.loc[need, "taluk_source"] = "nearest neighbour"
    k = k[k.taluk_clean.notna()]
    out = pd.DataFrame({
        "state": "Karnataka",
        "district": k.taluk_clean.map(TALUK_TO_DISTRICT),
        "taluk": k.taluk_clean,
        "village_or_post_office": k.officename.str.replace(r"\s*[BSH]\.O\.?$", "", regex=True).str.strip(),
        "office_type": k.officeType,
        "pincode": k.pincode,
        "latitude": k.Latitude.round(5),
        "longitude": k.Longitude.round(5),
        "taluk_source": k.taluk_source,
    }).merge(ts.drop(columns=["state", "district"]), on="taluk", how="left").drop_duplicates()
    out = out.sort_values(["district", "taluk", "village_or_post_office"])
    out.to_csv("karnataka_location_soil.csv", index=False)
    print("karnataka_location_soil.csv:", len(out), "rows,",
          out.taluk.nunique(), "taluks,", f"{out.latitude.notna().mean():.0%} with GPS")
    print(out.taluk_source.value_counts())


if __name__ == "__main__":
    main()
