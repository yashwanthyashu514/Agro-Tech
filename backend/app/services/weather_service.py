"""
Weather prediction service.
Wraps the existing XGBoost-based multi-horizon forecaster for Karnataka.

The core forecasting logic is imported directly from the original
train_karnataka_weather_model.py to avoid duplication.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.config import DATA_DIR, RAIN_DAY_MM
from app.schemas import WeatherDay, WeatherForecast

logger = logging.getLogger(__name__)

# Add the original module folder to sys.path so we can import forecast()
_WEATHER_MODULE_DIR = DATA_DIR / "3_weather_prediction"
if str(_WEATHER_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(_WEATHER_MODULE_DIR))


def _import_forecast():
    try:
        from train_karnataka_weather_model import forecast, features_one, pred_reg  # type: ignore[import]  # noqa: E402
        return forecast, features_one, pred_reg
    except ImportError as e:
        logger.error("Cannot import weather forecast module: %s", e)
        raise


def _risk_label(prob: float) -> str:
    if prob >= 65:
        return "High"
    elif prob >= 35:
        return "Moderate"
    return "Low"


def get_weather_forecast(
    bundle: Dict[str, Any],
    weather_hist: pd.DataFrame,
    district: str,
    days: int = 15,
) -> WeatherForecast:
    """
    Generate a N-day weather forecast for a Karnataka district.
    Uses ML models for days 1-7 and climatology for days 8+.
    """
    # normalise district name
    available = list(bundle["districts"].index)
    district_norm = district
    if district not in available:
        matches = [d for d in available if d.lower() == district.lower()]
        if not matches:
            matches = [d for d in available if district.lower() in d.lower()]
        if not matches:
            raise ValueError(
                f"District '{district}' not in weather model. "
                f"Available: {', '.join(sorted(available))}"
            )
        district_norm = matches[0]

    try:
        hist = weather_hist
        if "date" in hist.columns:
            hist = hist.set_index("date")
        if not isinstance(hist.index, pd.DatetimeIndex):
            hist.index = pd.to_datetime(hist.index)
        forecast, _, _ = _import_forecast()
        fc_df = forecast(bundle, hist, district_norm, days=days)
    except Exception as e:
        logger.warning("ML forecast failed for %s: %s — using climatology fallback", district, e)
        fc_df = _climatology_fallback(bundle, district_norm, days)

    days_out: List[WeatherDay] = []
    for _, row in fc_df.iterrows():
        rain_prob = float(row.get("rain_probability_pct", 0))
        days_out.append(WeatherDay(
            date=str(row["date"]),
            days_ahead=int(row["days_ahead"]),
            rain_probability_pct=round(rain_prob, 1),
            expected_rain_mm=round(float(row.get("expected_rain_mm", 0)), 1),
            temp_max_c=_safe_float(row.get("temp_max_c")),
            temp_min_c=_safe_float(row.get("temp_min_c")),
            humidity_pct=_safe_float(row.get("humidity_pct")),
            source=str(row.get("source", "climatology")),
            rain_risk=_risk_label(rain_prob),
        ))

    # summary statistics
    rain_probs = [d.rain_probability_pct for d in days_out]
    rain_mms   = [d.expected_rain_mm for d in days_out]
    summary = {
        "avg_rain_probability_pct": round(float(np.mean(rain_probs)), 1),
        "total_expected_rain_mm":   round(float(np.sum(rain_mms)), 1),
        "max_rain_mm":              round(float(np.max(rain_mms)), 1),
        "rainy_days_forecast":      int(sum(1 for p in rain_probs if p >= 35)),
        "avg_temp_max_c": round(float(np.nanmean([d.temp_max_c for d in days_out if d.temp_max_c])), 1),
        "irrigation_advisory": _irrigation_advisory(rain_probs, rain_mms),
    }

    return WeatherForecast(
        district=district_norm,
        forecast_from=str(days_out[0].date) if days_out else "unknown",
        days=days_out,
        summary=summary,
    )


def _safe_float(val: Any) -> Optional[float]:
    try:
        return round(float(val), 1) if val is not None and not (isinstance(val, float) and np.isnan(val)) else None
    except Exception:
        return None


def _irrigation_advisory(probs: List[float], mms: List[float]) -> str:
    next7_rain = sum(mms[:7])
    next7_prob = sum(1 for p in probs[:7] if p >= 50)
    if next7_rain >= 80 or next7_prob >= 4:
        return "Good rainfall expected — irrigation likely NOT needed for the next 7 days."
    elif next7_rain >= 40 or next7_prob >= 2:
        return "Moderate rainfall expected — monitor crop stress; light irrigation may be needed."
    else:
        return "Dry spell likely — plan for irrigation within the next 7 days."


def _climatology_fallback(bundle: Dict, district: str, days: int) -> pd.DataFrame:
    """Use stored climatology when the ML model fails."""
    clim = bundle["climatology"].get(district)
    if clim is None:
        raise ValueError(f"No climatology data for district {district}")

    today = pd.Timestamp.today()
    rows = []
    for h in range(1, days + 1):
        d = today + pd.Timedelta(days=h)
        doy = min(d.dayofyear, 365)
        rows.append({
            "district": district,
            "date": d.date(),
            "days_ahead": h,
            "rain_probability_pct": round(100 * float(clim["rain_prob"][doy]), 1),
            "expected_rain_mm": round(float(clim.get("rainfall_mm", pd.Series([0]))[doy]), 1),
            "temp_max_c": round(float(clim["temp_max_c"][doy]), 1) if "temp_max_c" in clim else None,
            "temp_min_c": round(float(clim["temp_min_c"][doy]), 1) if "temp_min_c" in clim else None,
            "humidity_pct": round(float(clim["humidity_pct"][doy]), 1) if "humidity_pct" in clim else None,
            "source": "long-term average (fallback)",
        })
    return pd.DataFrame(rows)


def get_seasonal_weather_summary(
    bundle: Dict,
    weather_hist: pd.DataFrame,
    district: str,
    season: str,
    months: List[int],
) -> Dict[str, Any]:
    """Get historical seasonal weather stats for a district."""
    dw = weather_hist[weather_hist["district"] == district].copy()
    if dw.empty:
        return {}
    dw = dw[dw["date"].dt.month.isin(months)]
    if dw.empty:
        return {}
    return {
        "avg_temp_max_c": round(float(dw["temp_max_c"].mean()), 1),
        "avg_temp_min_c": round(float(dw["temp_min_c"].mean()), 1),
        "avg_humidity_pct": round(float(dw["humidity_pct"].mean()), 1),
        "total_season_rain_mm": round(float(dw["rainfall_mm"].sum() / max(dw["date"].dt.year.nunique(), 1)), 1),
        "avg_rainy_days": round(float((dw["rainfall_mm"] >= RAIN_DAY_MM).sum() / max(dw["date"].dt.year.nunique(), 1)), 0),
        "years_of_data": int(dw["date"].dt.year.nunique()),
    }
