"""
Location & Soil intelligence service.
Resolves taluk / district to agro-zone and soil properties.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from app.config import SEASON_MONTHS, SEASON_SOW

logger = logging.getLogger(__name__)

# Calibrated agro-zone soil medians matching the crop model feature distributions (N, P, K in kg/ha applied/available equivalent)
ZONE_SOIL_MEDIANS: Dict[int, Dict[str, float]] = {
    1: {"N": 65.0, "P": 45.0, "K": 30.0, "ph": 7.4},   # NE Transition (Bidar, Kalaburagi)
    2: {"N": 70.0, "P": 48.0, "K": 35.0, "ph": 7.6},   # NE Dry (Raichur, Yadgir)
    3: {"N": 60.0, "P": 42.0, "K": 25.0, "ph": 7.5},   # Northern Dry (Ballari, Koppal, Gadag)
    4: {"N": 75.0, "P": 46.0, "K": 30.0, "ph": 6.8},   # Central Dry (Davanagere, Chitradurga)
    5: {"N": 65.0, "P": 44.0, "K": 28.0, "ph": 6.5},   # Eastern Dry (Kolar, Chikkaballapur)
    6: {"N": 65.0, "P": 40.0, "K": 25.0, "ph": 6.7},   # Southern Dry (Mandya, Mysuru)
    7: {"N": 70.0, "P": 45.0, "K": 30.0, "ph": 6.6},   # Southern Transition (Hassan, Shivamogga)
    8: {"N": 75.0, "P": 48.0, "K": 30.0, "ph": 7.1},   # Northern Transition (Dharwad, Belagavi)
    9: {"N": 55.0, "P": 35.0, "K": 30.0, "ph": 5.8},   # Hilly / Malnad (Kodagu, Chikkamagaluru)
    10: {"N": 75.0, "P": 42.0, "K": 35.0, "ph": 5.5},  # Coastal (Udupi, Dakshina/Uttara Kannada)
}

# typical season weather per district (used only when live weather unavailable)
ZONE_SEASON_WEATHER: Dict[int, Dict[str, Dict[str, float]]] = {
    1: {"Kharif": {"temperature": 26.5, "humidity": 70, "rainfall": 150},
        "Rabi":   {"temperature": 21.0, "humidity": 55, "rainfall": 25},
        "Summer": {"temperature": 32.0, "humidity": 40, "rainfall": 8}},
    2: {"Kharif": {"temperature": 27.0, "humidity": 65, "rainfall": 120},
        "Rabi":   {"temperature": 21.5, "humidity": 50, "rainfall": 20},
        "Summer": {"temperature": 33.0, "humidity": 35, "rainfall": 5}},
    3: {"Kharif": {"temperature": 27.5, "humidity": 60, "rainfall": 100},
        "Rabi":   {"temperature": 22.0, "humidity": 48, "rainfall": 15},
        "Summer": {"temperature": 34.0, "humidity": 33, "rainfall": 4}},
    4: {"Kharif": {"temperature": 26.0, "humidity": 65, "rainfall": 90},
        "Rabi":   {"temperature": 22.0, "humidity": 52, "rainfall": 15},
        "Summer": {"temperature": 32.5, "humidity": 38, "rainfall": 5}},
    5: {"Kharif": {"temperature": 25.5, "humidity": 68, "rainfall": 130},
        "Rabi":   {"temperature": 20.0, "humidity": 56, "rainfall": 20},
        "Summer": {"temperature": 32.0, "humidity": 42, "rainfall": 6}},
    6: {"Kharif": {"temperature": 25.0, "humidity": 70, "rainfall": 140},
        "Rabi":   {"temperature": 19.5, "humidity": 58, "rainfall": 22},
        "Summer": {"temperature": 31.5, "humidity": 44, "rainfall": 7}},
    7: {"Kharif": {"temperature": 24.0, "humidity": 72, "rainfall": 180},
        "Rabi":   {"temperature": 19.0, "humidity": 60, "rainfall": 30},
        "Summer": {"temperature": 30.0, "humidity": 48, "rainfall": 10}},
    8: {"Kharif": {"temperature": 25.5, "humidity": 70, "rainfall": 200},
        "Rabi":   {"temperature": 20.0, "humidity": 60, "rainfall": 30},
        "Summer": {"temperature": 31.0, "humidity": 45, "rainfall": 10}},
    9: {"Kharif": {"temperature": 22.0, "humidity": 80, "rainfall": 400},
        "Rabi":   {"temperature": 18.0, "humidity": 65, "rainfall": 60},
        "Summer": {"temperature": 28.0, "humidity": 55, "rainfall": 15}},
    10: {"Kharif": {"temperature": 26.0, "humidity": 85, "rainfall": 700},
         "Rabi":   {"temperature": 23.0, "humidity": 75, "rainfall": 80},
         "Summer": {"temperature": 29.0, "humidity": 70, "rainfall": 20}},
}


DISTRICT_ALIASES: Dict[str, str] = {
    "shimoga": "Shivamogga",
    "mysore": "Mysuru",
    "bellary": "Ballari",
    "belgaum": "Belagavi",
    "bijapur": "Vijayapura",
    "gulbarga": "Kalaburagi",
    "chikmagalur": "Chikkamagaluru",
    "chickmagalur": "Chikkamagaluru",
    "tumkur": "Tumakuru",
    "bangalore urban": "Bengaluru Urban",
    "bangalore rural": "Bengaluru Rural",
    "bangalore": "Bengaluru Urban",
    "bengaluru": "Bengaluru Urban",
    "coorg": "Kodagu",
    "madikeri": "Kodagu",
    "mangalore": "Dakshina Kannada",
    "karwar": "Uttara Kannada",
    "north canara": "Uttara Kannada",
    "south canara": "Dakshina Kannada",
}


def find_location(taluk_soil_df: pd.DataFrame,
                  taluk: Optional[str] = None,
                  district: Optional[str] = None) -> pd.Series:
    """Lookup a location row from karnataka_taluk_soil.csv with alias normalization."""
    df = taluk_soil_df

    # Normalize district alias if present
    if district:
        clean_dist = district.strip().lower()
        district = DISTRICT_ALIASES.get(clean_dist, district.strip())

    if taluk:
        clean_taluk = taluk.strip()
        norm_taluk = DISTRICT_ALIASES.get(clean_taluk.lower(), clean_taluk)

        # 1. Exact taluk match
        mask = df["taluk"].str.lower() == clean_taluk.lower()
        if not mask.any() and norm_taluk.lower() != clean_taluk.lower():
            mask = df["taluk"].str.lower() == norm_taluk.lower()

        # 2. Substring match on taluk
        if not mask.any():
            mask = df["taluk"].str.lower().str.contains(clean_taluk.lower(), na=False)
        if not mask.any() and norm_taluk.lower() != clean_taluk.lower():
            mask = df["taluk"].str.lower().str.contains(norm_taluk.lower(), na=False)

        # 3. If user entered district name as taluk (e.g. taluk="Shimoga"), match district
        if not mask.any():
            dist_cand = DISTRICT_ALIASES.get(clean_taluk.lower(), clean_taluk)
            mask = df["district"].str.lower() == dist_cand.lower()

        if mask.any():
            return df[mask].iloc[0]

        available = df["taluk"].tolist()
        raise ValueError(
            f"Taluk '{taluk}' not found. "
            f"Some valid taluks: {', '.join(available[:10])}"
        )

    # District search – return first taluk of that district
    mask = df["district"].str.lower() == (district or "").lower()
    if not mask.any():
        mask = df["district"].str.lower().str.contains((district or "").lower(), na=False)
    if not mask.any():
        available = df["district"].unique().tolist()
        raise ValueError(
            f"District '{district}' not found. "
            f"Available: {', '.join(sorted(available)[:15])}"
        )
    return df[mask].iloc[0]


def resolve_soil(loc: pd.Series,
                 N: Optional[float], P: Optional[float],
                 K: Optional[float], ph: Optional[float]
                 ) -> Tuple[Dict[str, float], str]:
    """
    Returns soil nutrient values and their source description.
    Priority: farmer-entered → zone medians.
    Calibrates Indian Soil Health Card (SHC) available kg/ha to crop requirement scale.
    """
    zone = int(loc.get("agro_zone_no", 4))
    defaults = ZONE_SOIL_MEDIANS.get(zone, ZONE_SOIL_MEDIANS[4])

    n_val = N if N is not None else defaults["N"]
    p_val = P if P is not None else defaults["P"]
    k_val = K if K is not None else defaults["K"]
    ph_val = ph if ph is not None else defaults["ph"]

    # Soft calibration for farmers entering SHC lab test numbers
    if K is not None and k_val > 100:
        k_val = round(20.0 + (min(k_val, 350.0) - 100.0) * (30.0 / 250.0), 1)
    if N is not None and n_val > 140:
        n_val = round(40.0 + (min(n_val, 400.0) - 140.0) * (60.0 / 260.0), 1)

    vals = {
        "N": n_val,
        "P": p_val,
        "K": k_val,
        "ph": ph_val,
    }
    provided = [k for k in ("N", "P", "K", "ph")
                if locals()[k] is not None]
    if len(provided) == 4:
        src = "Farmer-entered soil values"
    elif provided:
        src = f"Farmer-entered {', '.join(provided)}; remaining from zone {zone} medians"
    else:
        src = f"Agro-zone {zone} median values (no soil card data entered)"
    return vals, src


def resolve_weather(loc: pd.Series,
                    season: str,
                    weather_hist: pd.DataFrame,
                    temperature: Optional[float],
                    humidity: Optional[float],
                    rainfall: Optional[float]
                    ) -> Tuple[Dict[str, float], str]:
    """
    Returns seasonal weather averages and their source.
    Priority: farmer-entered → historical means from weather CSV → zone defaults.
    """
    if temperature is not None and humidity is not None and rainfall is not None:
        return (
            {"temperature": temperature, "humidity": humidity, "rainfall": rainfall},
            "Farmer-entered weather"
        )

    district = loc["district"]
    months = SEASON_MONTHS[season]
    dw = weather_hist[weather_hist["district"] == district].copy()
    if not dw.empty:
        dw = dw[dw["date"].dt.month.isin(months)]
        if not dw.empty:
            t_avg = ((dw["temp_min_c"] + dw["temp_max_c"]) / 2).mean()
            h_avg = dw["humidity_pct"].mean()
            years = dw["date"].dt.year.nunique()
            r_avg = dw["rainfall_mm"].sum() / max(years, 1) / len(months)
            result = {
                "temperature": round(float(t_avg), 1),
                "humidity": round(float(h_avg), 1),
                "rainfall": round(float(r_avg), 1),
            }
            return result, f"Historical {season} average for {district} (NASA POWER, 1991-2025)"

    # zone fallback
    zone = int(loc.get("agro_zone_no", 4))
    defaults = ZONE_SEASON_WEATHER.get(zone, ZONE_SEASON_WEATHER[4])
    return defaults[season], f"Agro-zone {zone} {season} typical values"
