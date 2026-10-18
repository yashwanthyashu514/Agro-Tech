"""
Crop Growth Stage prediction service.
Uses the Growing-Degree-Day (GDD) heat-unit model from Module 4.
Supports both annual and perennial crops.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.config import DATA_DIR, PERENNIAL_CROPS
from app.schemas import GrowthPlan, GrowthStage

logger = logging.getLogger(__name__)

# Add original module dir to path
_GROWTH_MODULE_DIR = DATA_DIR / "4_crop_growth"
if str(_GROWTH_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(_GROWTH_MODULE_DIR))

T_UPPER = 35.0


def predict_growth_plan(
    crop: str,
    sow_date: str,
    district: str,
    crop_stages: pd.DataFrame,
    crop_master: pd.DataFrame,
    perennial_cal: pd.DataFrame,
    weather_hist: pd.DataFrame,
) -> GrowthPlan:
    """
    Predict growth stages using GDD model when weather is available,
    or typical-duration fallback otherwise.
    """
    crop_lower = crop.lower()

    # ── perennial crops ───────────────────────────────────────────────────────
    if crop_lower in PERENNIAL_CROPS:
        return _perennial_plan(crop_lower, sow_date, perennial_cal, crop_master)

    # ── annual crop: GDD model if weather available ───────────────────────────
    dw = weather_hist[weather_hist["district"] == district].copy()
    if not dw.empty and crop_lower in crop_master.index:
        try:
            return _gdd_plan(crop_lower, sow_date, dw, crop_stages, crop_master)
        except Exception as e:
            logger.warning("GDD model failed for %s: %s — falling back to typical durations", crop, e)

    # ── fallback: typical days ────────────────────────────────────────────────
    return _typical_plan(crop_lower, sow_date, crop_stages, crop_master)


def _gdd_plan(
    crop: str,
    sow_date: str,
    dw: pd.DataFrame,
    crop_stages: pd.DataFrame,
    crop_master: pd.DataFrame,
) -> GrowthPlan:
    """GDD-based growth prediction using historical district weather."""
    info = crop_master.loc[crop]
    cs = crop_stages[crop_stages["crop"] == crop].sort_values("stage_no")
    tbase = float(info["base_temp_c"])

    dw = dw.copy()
    dw["date"] = pd.to_datetime(dw["date"])
    dw["tavg"] = (dw["temp_min_c"] + dw["temp_max_c"]) / 2
    dw = dw.dropna(subset=["tavg"])
    dw["doy"] = dw["date"].dt.dayofyear.clip(upper=365)
    clim = dw.groupby("doy")["tavg"].mean().reindex(range(1, 366)).interpolate().bfill().ffill()

    actual = dw.set_index("date")["tavg"]

    # calibrate GDD targets on typical sowing date in average year
    typical = pd.Timestamp(f"2001-{info['typical_sowing_date']}")
    horizon = int(cs["end_day"].max()) + 1
    cal_dates = pd.date_range(typical, periods=horizon)
    doys = cal_dates.dayofyear.to_numpy().clip(max=365)
    cum_ref = np.cumsum(np.maximum(0, np.minimum(clim.loc[doys].values, T_UPPER) - tbase))
    targets = [(r.growth_stage, cum_ref[min(int(r.end_day), horizon - 1)]) for r in cs.itertuples()]

    # accumulate GDD from actual sow date
    sow = pd.Timestamp(sow_date)
    pred_dates = pd.date_range(sow, periods=horizon * 2)
    t = actual.reindex(pred_dates)
    from_clim = t.isna()
    t[from_clim] = clim.loc[pred_dates[from_clim].dayofyear.to_numpy().clip(max=365)].values
    cum = np.cumsum(np.maximum(0, np.minimum(t.values, T_UPPER) - tbase))

    stages: List[GrowthStage] = []
    start = sow
    for (name, target), r in zip(targets, cs.itertuples()):
        idx = int(np.searchsorted(cum, target))
        if idx >= len(pred_dates):
            stages.append(GrowthStage(
                stage=name, start_date=str(start.date()), end_date=None,
                days_after_sowing=None, kc=None,
                water_need="not reached – too cold", critical_irrigation=None,
                weather_used="actual/climatology",
            ))
            break
        end = pred_dates[idx]
        weather_used = "climatology" if from_clim.values[idx] else "actual historical"
        stages.append(GrowthStage(
            stage=name,
            start_date=str(start.date()),
            end_date=str(end.date()),
            days_after_sowing=f"{(start - sow).days}–{(end - sow).days}",
            kc=round(float(r.kc), 2) if hasattr(r, "kc") else None,
            water_need=str(r.water_need) if hasattr(r, "water_need") else None,
            critical_irrigation=str(r.critical_irrigation) if hasattr(r, "critical_irrigation") else None,
            weather_used=weather_used,
        ))
        start = end + pd.Timedelta(days=1)

    return GrowthPlan(
        crop=crop,
        sow_date=sow_date,
        prediction_type="GDD heat-unit model",
        total_duration_days=int(info["total_duration_days"]),
        base_temp_c=float(tbase),
        stages=stages,
    )


def _typical_plan(
    crop: str,
    sow_date: str,
    crop_stages: pd.DataFrame,
    crop_master: pd.DataFrame,
) -> GrowthPlan:
    """Fallback: use median-duration stage table from crop_growth_stages.csv."""
    cs = crop_stages[crop_stages["crop"] == crop].sort_values("stage_no")
    if cs.empty:
        return GrowthPlan(
            crop=crop, sow_date=sow_date,
            prediction_type="no data", total_duration_days=None,
            base_temp_c=None, stages=[]
        )
    s0 = pd.Timestamp(sow_date)
    stages = []
    for r in cs.itertuples():
        start = s0 + pd.Timedelta(days=int(r.start_day))
        end   = s0 + pd.Timedelta(days=int(r.end_day))
        stages.append(GrowthStage(
            stage=r.growth_stage,
            start_date=str(start.date()),
            end_date=str(end.date()),
            days_after_sowing=f"{r.start_day}–{r.end_day}",
            kc=round(float(r.kc), 2) if hasattr(r, "kc") else None,
            water_need=str(r.water_need) if hasattr(r, "water_need") else None,
            critical_irrigation=str(r.critical_irrigation) if hasattr(r, "critical_irrigation") else None,
            weather_used="typical duration (no weather data)",
        ))
    duration = int(crop_master.loc[crop, "total_duration_days"]) if crop in crop_master.index else None
    return GrowthPlan(
        crop=crop, sow_date=sow_date,
        prediction_type="typical-duration table",
        total_duration_days=duration,
        base_temp_c=float(crop_master.loc[crop, "base_temp_c"]) if crop in crop_master.index else None,
        stages=stages,
    )


def _perennial_plan(
    crop: str,
    sow_date: str,
    perennial_cal: pd.DataFrame,
    crop_master: pd.DataFrame,
) -> GrowthPlan:
    """Return the perennial crop calendar as stages."""
    stages = []
    if not perennial_cal.empty and crop in perennial_cal.index:
        row = perennial_cal.loc[crop]
        for col in perennial_cal.columns:
            if str(row[col]) not in ("", "nan", "None"):
                stages.append(GrowthStage(
                    stage=col, start_date=sow_date,
                    end_date=None, days_after_sowing=None,
                    kc=None, water_need=str(row[col]),
                    critical_irrigation=None, weather_used="perennial calendar",
                ))
    return GrowthPlan(
        crop=crop, sow_date=sow_date,
        prediction_type="perennial crop calendar",
        total_duration_days=None, base_temp_c=None, stages=stages,
    )
