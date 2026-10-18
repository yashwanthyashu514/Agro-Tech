"""
Crop Recommendation service — Agronomic Multi-Criteria Decision Engine.

Two-stage ranking:
  Stage 1: ML Random Forest classifier probabilities from soil nutrients (N, P, K, pH)
           and ambient weather (temperature, humidity, monthly rainfall).
  Stage 2: Agronomic Multi-Criteria Decision Analysis (MCDA) that incorporates:
           1. Season Compatibility: Strict season gating (e.g. Watermelon/Muskmelon
              in Summer only, Chickpea in Rabi only, Cotton/Rice in Kharif).
           2. 100-Day Weather & Climate Windows: Temperature tolerance, rainfall
              suitability, and humidity curve alignment.
           3. Soil Type Suitability: Matching dominant soil (Black clay, Red loam,
              Laterite, Coastal sandy) with crop-specific soil preferences.
           4. Economic Profitability: Net margin, MSP security, and market liquidity.
           5. Ease of Cultivation: Pest risk, drought tolerance, labor intensity,
              and mechanical harvesting suitability for smallholder farmers.

This produces accurate, realistic, district- and season-appropriate recommendations
and completely eliminates the uncalibrated "watermelon everywhere" bug.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.config import SEASON_SOW
from app.schemas import CropRecommendation, CropReason, CropYield

logger = logging.getLogger(__name__)

# ── ICAR / UAS Bangalore / UAS Dharwad Crop Metadata ────────────────────────
CROP_META: Dict[str, Dict[str, Any]] = {
    "maize": {
        "season": ["Kharif", "Rabi"],
        "water": "Medium (500–800 mm/yr)",
        "min_t": 18, "max_t": 35, "min_r": 50, "max_r": 150, "min_h": 45, "max_h": 80,
        "soils": ["Black", "Red loam", "Red sandy loam", "Sandy loam", "Clay loam"],
        "profit_rating": "High",
        "profit_estimate": "₹50,000 – ₹80,000 / ha",
        "profit_score": 8.0,
        "ease_of_growth": "Very Easy (Wide adaptability, drought resilient, mechanical harvest)",
        "ease_score": 9.0,
        "market_demand": "Very High feed & starch industrial demand (Davanagere hub)",
        "soil_suitability_desc": "Thrives on deep black, red loam, and well-drained soils",
    },
    "cotton": {
        "season": ["Kharif"],
        "water": "Medium-High (700–1000 mm/yr)",
        "min_t": 21, "max_t": 37, "min_r": 60, "max_r": 180, "min_h": 50, "max_h": 80,
        "soils": ["Black", "Deep black", "Black (shallow-medium)", "Clay"],
        "profit_rating": "Very High",
        "profit_estimate": "₹75,000 – ₹1,30,000 / ha",
        "profit_score": 9.0,
        "ease_of_growth": "Moderate (Requires bollworm pest management & weed control)",
        "ease_score": 5.5,
        "market_demand": "High domestic textile mills & CCI procurement",
        "soil_suitability_desc": "Ideal for deep black cotton soils of Northern/Central Karnataka",
    },
    "rice": {
        "season": ["Kharif"],
        "water": "High (1200–1800 mm/yr)",
        "min_t": 20, "max_t": 35, "min_r": 150, "max_r": 350, "min_h": 70, "max_h": 95,
        "soils": ["Clay", "Clay loam", "Alluvial", "Laterite", "Red lateritic"],
        "profit_rating": "High",
        "profit_estimate": "₹55,000 – ₹85,000 / ha",
        "profit_score": 7.5,
        "ease_of_growth": "Moderate (Requires continuous irrigation or high rainfall)",
        "ease_score": 6.0,
        "market_demand": "High MSP & State PDS procurement",
        "soil_suitability_desc": "Suited for clayey & alluvial soils with high water retention",
    },
    "pigeonpeas": {
        "season": ["Kharif"],
        "water": "Low-Medium (400–650 mm/yr)",
        "min_t": 18, "max_t": 35, "min_r": 50, "max_r": 160, "min_h": 40, "max_h": 75,
        "soils": ["Black", "Red loam", "Red sandy loam", "Sandy loam"],
        "profit_rating": "High",
        "profit_estimate": "₹55,000 – ₹90,000 / ha",
        "profit_score": 8.5,
        "ease_of_growth": "Easy (Deep taproot, drought hardy, excellent intercrop)",
        "ease_score": 8.0,
        "market_demand": "High demand in Gulbarga/Kalaburagi pulse belt (GI Tag)",
        "soil_suitability_desc": "Highly suited for well-drained medium black and red soils",
    },
    "chickpea": {
        "season": ["Rabi"],
        "water": "Low (300–450 mm/yr)",
        "min_t": 15, "max_t": 30, "min_r": 15, "max_r": 60, "min_h": 10, "max_h": 50,
        "soils": ["Black", "Deep black", "Black (shallow-medium)", "Clay loam"],
        "profit_rating": "High",
        "profit_estimate": "₹45,000 – ₹75,000 / ha",
        "profit_score": 8.0,
        "ease_of_growth": "Easy (Low water need, enriches soil nitrogen)",
        "ease_score": 8.5,
        "market_demand": "High MSP & national pulse demand",
        "soil_suitability_desc": "Prefers heavy black clay soils retaining residual moisture",
    },
    "mungbean": {
        "season": ["Kharif", "Summer"],
        "water": "Low (350–500 mm/yr)",
        "min_t": 25, "max_t": 38, "min_r": 30, "max_r": 80, "min_h": 55, "max_h": 85,
        "soils": ["Loam", "Red loam", "Sandy loam", "Light black"],
        "profit_rating": "Moderate to High",
        "profit_estimate": "₹35,000 – ₹60,000 / ha",
        "profit_score": 7.0,
        "ease_of_growth": "Very Easy (Short duration 65-day turnaround, restores soil)",
        "ease_score": 9.0,
        "market_demand": "Stable APMC demand for dal",
        "soil_suitability_desc": "Suitable for fertile loam and well-drained sandy loam",
    },
    "blackgram": {
        "season": ["Kharif"],
        "water": "Low (350–500 mm/yr)",
        "min_t": 25, "max_t": 35, "min_r": 40, "max_r": 100, "min_h": 60, "max_h": 80,
        "soils": ["Black", "Clay loam", "Red loam"],
        "profit_rating": "Moderate to High",
        "profit_estimate": "₹38,000 – ₹65,000 / ha",
        "profit_score": 7.0,
        "ease_of_growth": "Very Easy (Low input cost, minimal irrigation)",
        "ease_score": 8.5,
        "market_demand": "High culinary staple demand across South India",
        "soil_suitability_desc": "Thrives on black clay and medium loams",
    },
    "pomegranate": {
        "season": ["Kharif", "Rabi", "Summer"],
        "water": "Low-Medium (500–800 mm/yr)",
        "min_t": 25, "max_t": 38, "min_r": 30, "max_r": 120, "min_h": 45, "max_h": 75,
        "soils": ["Light black", "Sandy loam", "Red loam", "Black"],
        "profit_rating": "Very High",
        "profit_estimate": "₹1,40,000 – ₹3,00,000 / ha",
        "profit_score": 9.5,
        "ease_of_growth": "Moderate (Bacterial blight monitoring and pruning needed)",
        "ease_score": 6.0,
        "market_demand": "High domestic & export demand (Bhagwa variety)",
        "soil_suitability_desc": "Ideal for well-drained light black and red soils of dry belt",
    },
    "banana": {
        "season": ["Kharif", "Rabi", "Summer"],
        "water": "High (1200–2200 mm/yr)",
        "min_t": 20, "max_t": 35, "min_r": 80, "max_r": 300, "min_h": 70, "max_h": 90,
        "soils": ["Rich clay loam", "Alluvial", "Black", "Red loam"],
        "profit_rating": "Very High",
        "profit_estimate": "₹1,10,000 – ₹2,20,000 / ha",
        "profit_score": 9.0,
        "ease_of_growth": "Moderate (Requires heavy drip fertigation & bunch propping)",
        "ease_score": 6.5,
        "market_demand": "Massive urban consumption & year-round market liquidity",
        "soil_suitability_desc": "Prefers deep rich organic loams with high moisture retention",
    },
    "coffee": {
        "season": ["Kharif", "Rabi"],
        "water": "High (1500–2500 mm/yr)",
        "min_t": 15, "max_t": 28, "min_r": 150, "max_r": 500, "min_h": 70, "max_h": 95,
        "soils": ["Red lateritic", "Laterite", "Forest loam"],
        "profit_rating": "Very High",
        "profit_estimate": "₹1,20,000 – ₹2,50,000 / ha",
        "profit_score": 9.5,
        "ease_of_growth": "High Care (Shade tree canopy & plantation management)",
        "ease_score": 4.0,
        "market_demand": "High global export & domestic café demand (Malnad region)",
        "soil_suitability_desc": "Exclusively suited for laterite & forest soils of Western Ghats",
    },
    "coconut": {
        "season": ["Kharif", "Rabi", "Summer"],
        "water": "High (1500–2500 mm/yr)",
        "min_t": 20, "max_t": 35, "min_r": 100, "max_r": 500, "min_h": 70, "max_h": 95,
        "soils": ["Coastal sand", "Laterite", "Red loam", "Alluvial"],
        "profit_rating": "High",
        "profit_estimate": "₹80,000 – ₹1,60,000 / ha",
        "profit_score": 8.5,
        "ease_of_growth": "Easy to Moderate (Long term perennial, low daily effort)",
        "ease_score": 7.0,
        "market_demand": "Consistent year-round tender water & copra oil demand",
        "soil_suitability_desc": "Ideal for coastal sandy and well-drained laterite soils",
    },
    "grapes": {
        "season": ["Rabi", "Summer"],
        "water": "Medium (600–800 mm/yr)",
        "min_t": 15, "max_t": 40, "min_r": 20, "max_r": 120, "min_h": 45, "max_h": 75,
        "soils": ["Sandy loam", "Red sandy loam", "Black"],
        "profit_rating": "Very High",
        "profit_estimate": "₹2,00,000 – ₹4,50,000 / ha",
        "profit_score": 10.0,
        "ease_of_growth": "High Care (Trellis training, pruning, mildew spraying)",
        "ease_score": 4.0,
        "market_demand": "Very high table grape and winery demand (Vijayapura/Bengaluru)",
        "soil_suitability_desc": "Requires well-drained sandy loam or light black soil",
    },
    "mango": {
        "season": ["Kharif", "Summer"],
        "water": "Medium (600–1000 mm/yr)",
        "min_t": 24, "max_t": 42, "min_r": 50, "max_r": 200, "min_h": 40, "max_h": 70,
        "soils": ["Red loam", "Laterite", "Alluvial", "Red sandy loam"],
        "profit_rating": "Very High",
        "profit_estimate": "₹90,000 – ₹2,00,000 / ha",
        "profit_score": 9.0,
        "ease_of_growth": "Easy (Hardy perennial orchard once established)",
        "ease_score": 7.5,
        "market_demand": "Huge seasonal fresh fruit & pulp processing export",
        "soil_suitability_desc": "Thrives on deep red loamy and lateritic soils",
    },
    "watermelon": {
        "season": ["Summer"],
        "water": "Medium (400–600 mm/yr)",
        "min_t": 25, "max_t": 40, "min_r": 10, "max_r": 50, "min_h": 50, "max_h": 80,
        "soils": ["Sandy loam", "Alluvial", "Riverbed sandy"],
        "profit_rating": "High",
        "profit_estimate": "₹60,000 – ₹1,10,000 / ha",
        "profit_score": 7.5,
        "ease_of_growth": "Easy (Fast 85-day turnaround, low weed competition in dry summer)",
        "ease_score": 8.0,
        "market_demand": "Peak summer hydration fruit demand in all towns/cities",
        "soil_suitability_desc": "Strictly requires sandy loam / light soil (rots in waterlogged clay)",
    },
    "muskmelon": {
        "season": ["Summer"],
        "water": "Low-Medium (350–550 mm/yr)",
        "min_t": 22, "max_t": 38, "min_r": 10, "max_r": 40, "min_h": 50, "max_h": 80,
        "soils": ["Sandy loam", "Alluvial", "Light loam"],
        "profit_rating": "High",
        "profit_estimate": "₹55,000 – ₹95,000 / ha",
        "profit_score": 7.5,
        "ease_of_growth": "Easy (Short lifecycle, loves sunny dry weather)",
        "ease_score": 8.0,
        "market_demand": "Strong hot-season fruit market",
        "soil_suitability_desc": "Prefers light warm sandy loams with zero water stagnation",
    },
    "papaya": {
        "season": ["Kharif", "Rabi", "Summer"],
        "water": "Medium (1000–1500 mm/yr)",
        "min_t": 20, "max_t": 38, "min_r": 60, "max_r": 200, "min_h": 65, "max_h": 90,
        "soils": ["Sandy loam", "Red loam", "Alluvial"],
        "profit_rating": "Very High",
        "profit_estimate": "₹1,20,000 – ₹2,40,000 / ha",
        "profit_score": 9.0,
        "ease_of_growth": "Moderate (Susceptible to root rot if waterlogged)",
        "ease_score": 6.5,
        "market_demand": "Consistent year-round table fruit demand (Taiwan 786)",
        "soil_suitability_desc": "Requires well-drained fertile loam (avoid heavy clay)",
    },
    "orange": {
        "season": ["Kharif", "Rabi"],
        "water": "Medium (750–1000 mm/yr)",
        "min_t": 15, "max_t": 35, "min_r": 50, "max_r": 180, "min_h": 55, "max_h": 85,
        "soils": ["Sandy loam", "Red loam", "Laterite"],
        "profit_rating": "High",
        "profit_estimate": "₹85,000 – ₹1,80,000 / ha",
        "profit_score": 8.5,
        "ease_of_growth": "Moderate (Orchard disease control - citrus canker)",
        "ease_score": 6.0,
        "market_demand": "High table fruit & juice processing demand (Kodagu/Coorg Orange)",
        "soil_suitability_desc": "Best in slightly acidic, well-drained loams of sub-humid hills",
    },
    "mothbeans": {
        "season": ["Kharif", "Summer"],
        "water": "Very Low (200–350 mm/yr)",
        "min_t": 25, "max_t": 42, "min_r": 10, "max_r": 40, "min_h": 20, "max_h": 55,
        "soils": ["Sandy loam", "Dry sandy", "Red sandy loam"],
        "profit_rating": "Moderate",
        "profit_estimate": "₹28,000 – ₹45,000 / ha",
        "profit_score": 6.0,
        "ease_of_growth": "Extremely Easy (Survives severe arid drought where others fail)",
        "ease_score": 9.5,
        "market_demand": "Niche snacks & roasted pulse market",
        "soil_suitability_desc": "Excellent for shallow poor sandy soils in dry belts",
    },
    "lentil": {
        "season": ["Rabi"],
        "water": "Low (300–400 mm/yr)",
        "min_t": 15, "max_t": 25, "min_r": 10, "max_r": 50, "min_h": 45, "max_h": 70,
        "soils": ["Alluvial", "Clay loam", "Loam"],
        "profit_rating": "Moderate",
        "profit_estimate": "₹35,000 – ₹55,000 / ha",
        "profit_score": 6.5,
        "ease_of_growth": "Easy (Cool climate, minimal fertilizer)",
        "ease_score": 7.5,
        "market_demand": "Moderate Mandi trade",
        "soil_suitability_desc": "Best in light loams and alluvial soils",
    },
    "kidneybeans": {
        "season": ["Rabi"],
        "water": "Medium (400–600 mm/yr)",
        "min_t": 15, "max_t": 28, "min_r": 40, "max_r": 100, "min_h": 50, "max_h": 75,
        "soils": ["Rich loam", "Silt loam", "Red loam"],
        "profit_rating": "High",
        "profit_estimate": "₹60,000 – ₹95,000 / ha",
        "profit_score": 7.5,
        "ease_of_growth": "Moderate (Sensitive to water stagnation & high heat)",
        "ease_score": 6.0,
        "market_demand": "Premium retail consumer demand",
        "soil_suitability_desc": "Requires deep well-drained rich loamy soils",
    },
    "jute": {
        "season": ["Kharif"],
        "water": "High (1200–1500 mm/yr)",
        "min_t": 25, "max_t": 38, "min_r": 150, "max_r": 400, "min_h": 70, "max_h": 95,
        "soils": ["Alluvial", "Clay loam", "River basin"],
        "profit_rating": "Moderate",
        "profit_estimate": "₹40,000 – ₹65,000 / ha",
        "profit_score": 6.0,
        "ease_of_growth": "Difficult in dry zones (Requires flowing retting pools)",
        "ease_score": 4.5,
        "market_demand": "Jute mill packaging & sacking demand",
        "soil_suitability_desc": "Restricted to river basins with abundant retting water",
    },
    "apple": {
        "season": ["Rabi"],
        "water": "Medium (750–1000 mm/yr)",
        "min_t": 2, "max_t": 24, "min_r": 40, "max_r": 120, "min_h": 55, "max_h": 85,
        "soils": ["Loam", "Deep hill loam"],
        "profit_rating": "Very High",
        "profit_estimate": "₹2,50,000+ / ha (High altitude only)",
        "profit_score": 9.0,
        "ease_of_growth": "Unsuitable for Karnataka plains (Requires 800+ winter chilling hours <7°C)",
        "ease_score": 1.0,
        "market_demand": "High, but climatically unviable in southern tropical plains",
        "soil_suitability_desc": "Temperate hill slopes with winter chilling hours",
    },
}

FEATURE_LABELS = {
    "N": "Nitrogen (kg/ha)",
    "P": "Phosphorus (kg/ha)",
    "K": "Potassium (kg/ha)",
    "temperature": "Temperature (°C)",
    "humidity": "Humidity (%)",
    "ph": "Soil pH",
    "rainfall": "Monthly rainfall (mm)",
}


def _agronomic_multiplier(
    crop: str,
    weather: Dict[str, float],
    season: str,
    soil_type: Optional[str] = None,
) -> float:
    """
    Computes multi-criteria agronomic multiplier based on:
      1. Season gating
      2. 100-day weather alignment (temp, rainfall, humidity)
      3. Soil texture compatibility
      4. Profitability & Ease of Cultivation
    """
    meta = CROP_META.get(crop, {})
    if not meta:
        return 0.5

    mult = 1.0

    # ── 1. Season gating (strict) ─────────────────────────────────────────────
    valid_seasons = meta.get("season", [])
    if isinstance(valid_seasons, str):
        valid_seasons = [valid_seasons]
    if season not in valid_seasons and "Year-round" not in valid_seasons:
        # Heavily penalize out-of-season crops (e.g. Watermelon in Kharif/Rabi)
        mult *= 0.08

    # ── 2. Temperature compatibility (upcoming weather) ───────────────────────
    temp = weather.get("temperature", 25.0)
    t_min = meta.get("min_t", 0.0)
    t_max = meta.get("max_t", 50.0)
    if temp < t_min:
        deficit = (t_min - temp) / max(t_min, 1.0)
        mult *= max(0.2, 1.0 - deficit * 2.2)
    elif temp > t_max:
        excess = (temp - t_max) / max(t_max, 1.0)
        mult *= max(0.2, 1.0 - excess * 2.2)

    # ── 3. Monthly Rainfall compatibility (upcoming season water) ─────────────
    rain = weather.get("rainfall", 80.0)
    r_min = meta.get("min_r", 0.0)
    r_max = meta.get("max_r", 9999.0)
    if rain < r_min * 0.7:
        deficit = (r_min * 0.7 - rain) / max(r_min, 1.0)
        mult *= max(0.2, 1.0 - deficit * 1.6)
    elif rain > r_max * 1.3:
        excess = (rain - r_max * 1.3) / max(r_max, 1.0)
        mult *= max(0.25, 1.0 - excess * 1.3)

    # ── 4. Humidity compatibility ─────────────────────────────────────────────
    hum = weather.get("humidity", 65.0)
    h_min = meta.get("min_h", 0.0)
    h_max = meta.get("max_h", 100.0)
    if hum < h_min - 10:
        deficit = (h_min - 10 - hum) / max(h_min, 1.0)
        mult *= max(0.5, 1.0 - deficit * 1.5)
    elif hum > h_max + 10:
        excess = (hum - h_max - 10) / max(h_max, 1.0)
        mult *= max(0.5, 1.0 - excess * 1.5)

    # ── 5. Soil Suitability matching ──────────────────────────────────────────
    if soil_type:
        st_clean = soil_type.lower()
        pref_soils = [s.lower() for s in meta.get("soils", [])]
        matched = any(p in st_clean or st_clean in p for p in pref_soils)

        if matched:
            mult *= 1.18  # Strong boost for crops naturally matching this soil
        else:
            # Special soil penalizations for mismatched combinations
            if ("black" in st_clean or "clay" in st_clean) and crop in ("watermelon", "muskmelon"):
                mult *= 0.55  # Watermelons rot in poorly drained black clay
            elif "laterite" in st_clean and crop in ("coffee", "coconut"):
                mult *= 1.25  # Coffee thrives in laterite
            elif ("black" in st_clean) and crop in ("cotton", "chickpea", "maize"):
                mult *= 1.20  # Classic black cotton soil synergy

    # ── 6. Profit & Ease-to-grow Multipliers ─────────────────────────────────
    profit_score = meta.get("profit_score", 7.0)
    ease_score = meta.get("ease_score", 7.0)

    # High profit reward: up to +10%
    profit_mult = 0.88 + (profit_score / 10.0) * 0.18
    # Ease to grow reward: up to +8%
    ease_mult = 0.88 + (ease_score / 10.0) * 0.16

    mult *= (profit_mult * ease_mult)

    return max(0.01, min(1.35, mult))


def recommend_crops(
    model: Any,
    encoder: Any,
    features: List[str],
    crop_ranges: pd.DataFrame,
    soil: Dict[str, float],
    weather: Dict[str, float],
    crop_master: pd.DataFrame,
    yield_feats: pd.DataFrame,
    yield_model: Any,
    yield_features: List[str],
    district: str,
    season: str,
    top_n: int = 5,
    soil_type: Optional[str] = None,
) -> List[CropRecommendation]:
    """
    Hybrid multi-criteria crop ranking:
      Stage 1 – ML classifier probabilities (soil nutrients + ambient weather)
      Stage 2 – Agronomic MCDA re-ranking (season, 100-day weather, soil, profit, ease)
    Returns top_n crops ordered by agronomic score.
    """
    input_row = {**soil, **weather}
    X = pd.DataFrame([input_row])[features]

    # Stage 1: ML probabilities
    raw_proba = model.predict_proba(X)[0]

    # Stage 2: compute multi-criteria scores for all 22 crops
    all_crops = encoder.classes_
    hybrid_scores = []
    for idx, crop in enumerate(all_crops):
        ml_score = float(raw_proba[idx])
        agro_mult = _agronomic_multiplier(crop, weather, season, soil_type=soil_type)
        hybrid = ml_score * agro_mult
        hybrid_scores.append((idx, crop, ml_score, agro_mult, hybrid))

    # Sort descending by hybrid score
    hybrid_scores.sort(key=lambda x: x[4], reverse=True)
    selected = hybrid_scores[:top_n]

    # Normalize hybrid score relative to highest candidate
    max_hybrid = selected[0][4] if selected else 1.0

    recommendations: List[CropRecommendation] = []
    for rank, (i, crop, ml_score, agro_mult, hybrid) in enumerate(selected, start=1):
        norm_score = hybrid / max_hybrid if max_hybrid > 0 else hybrid

        # ── explanation reasons ───────────────────────────────────────────────
        reasons: List[CropReason] = []
        for feat in features:
            val = float(X[feat].iat[0])
            try:
                lo = float(crop_ranges.loc[crop, (feat, 0.05)])
                hi = float(crop_ranges.loc[crop, (feat, 0.95)])
                status = "OK" if lo <= val <= hi else "OUT"
                typical = f"{lo:.0f} – {hi:.0f}"
            except Exception:
                status = "OK"
                typical = "n/a"
            reasons.append(CropReason(
                feature=FEATURE_LABELS.get(feat, feat),
                value=round(val, 2),
                typical_range=typical,
                status=status,
            ))

        # ── crop metadata ─────────────────────────────────────────────────────
        meta = CROP_META.get(crop, {})
        duration_days: Optional[int] = None
        if crop in crop_master.index:
            try:
                duration_days = int(crop_master.loc[crop, "total_duration_days"])
            except Exception:
                pass

        # ── yield prediction ──────────────────────────────────────────────────
        yield_pred = _predict_yield(
            crop, district, season, yield_feats, yield_model, yield_features
        )

        recommendations.append(CropRecommendation(
            rank=rank,
            crop=crop,
            suitability_score=round(norm_score, 4),
            suitability_pct=round(norm_score * 100, 1),
            season=", ".join(meta.get("season", [season])) if isinstance(meta.get("season"), list) else meta.get("season", season),
            duration_days=duration_days,
            water_requirement=meta.get("water"),
            min_temp_c=meta.get("min_t"),
            max_temp_c=meta.get("max_t"),
            min_rainfall_mm=meta.get("min_r"),
            max_rainfall_mm=meta.get("max_r"),
            profitability=meta.get("profit_rating"),
            profit_estimate=meta.get("profit_estimate"),
            ease_of_growth=meta.get("ease_of_growth"),
            soil_suitability=meta.get("soil_suitability_desc"),
            market_demand=meta.get("market_demand"),
            reasons=reasons,
            yield_prediction=yield_pred,
        ))

    return recommendations


# ── Yield prediction (internal) ───────────────────────────────────────────────

_YIELD_CROP = {
    "rice": "Rice", "maize": "Maize", "chickpea": "Gram",
    "pigeonpeas": "Arhar/Tur", "mungbean": "Moong(Green Gram)",
    "blackgram": "Urad", "mothbeans": "Moth", "lentil": "Masoor",
    "cotton": "Cotton(lint)", "jute": "Jute", "banana": "Banana",
    "mango": "Mango", "grapes": "Grapes", "pomegranate": "Pome Granet",
    "watermelon": "Water Melon", "papaya": "Papaya", "coffee": "Coffee",
    "kidneybeans": "Rajmash Kholar", "coconut": "Coconut",
}
_APY_SEASON = {"Kharif": "Kharif", "Rabi": "Rabi", "Summer": "Summer"}


def _predict_yield(
    crop: str,
    district: str,
    season: str,
    yield_feats: pd.DataFrame,
    model: Any,
    features: List[str],
) -> Optional[CropYield]:
    apy = _YIELD_CROP.get(crop)
    if not apy:
        return None

    h = yield_feats[
        (yield_feats["district"] == district) &
        (yield_feats["crop"] == apy) &
        (yield_feats["season"] == _APY_SEASON[season])
    ].sort_values("crop_year")

    if len(h) < 2:
        # fallback: state-wide rows
        h = yield_feats[
            (yield_feats["crop"] == apy) &
            (yield_feats["season"] == _APY_SEASON[season])
        ].sort_values("crop_year")
        if len(h) < 2:
            return None

    last = h.iloc[-1]
    state_row = yield_feats[
        (yield_feats["crop"] == apy) &
        (yield_feats["season"] == _APY_SEASON[season]) &
        (yield_feats["crop_year"] == last["crop_year"])
    ]["yield_t_ha"].median()

    row = last.copy()
    row["yield_lag1"] = last["yield_t_ha"]
    row["yield_mean_prev3"] = h["yield_t_ha"].tail(3).mean()
    row["area_lag1"] = last["area_ha"]
    row["state_yield_lag1"] = state_row
    row["years_since_1997"] = int(last["crop_year"]) + 1 - 1997

    X = pd.DataFrame([row])
    for c in features:
        if c not in X.columns:
            X[c] = float("nan")
    try:
        p = float(np.expm1(model.predict(X[features])[0]))
        return CropYield(
            predicted_t_ha=round(p, 2),
            district_avg_3yr_t_ha=round(float(h["yield_t_ha"].tail(3).mean()), 2),
            based_on_year=int(last["crop_year"]),
        )
    except Exception as e:
        logger.warning("Yield prediction failed for %s: %s", crop, e)
        return None
