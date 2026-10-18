"""
Weather, Growth and Yield standalone routers.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.model_loader import ModelRegistry, get_registry
from app.schemas import (
    GrowthPlan, GrowthRequest,
    WeatherForecast, WeatherRequest,
    YieldRequest,
)
from app.services.growth_service import predict_growth_plan
from app.services.weather_service import get_weather_forecast

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Weather router
# ──────────────────────────────────────────────────────────────────────────────
weather_router = APIRouter(prefix="/weather", tags=["Weather"])


@weather_router.get("/{district}", response_model=WeatherForecast)
async def get_district_weather(
    district: str,
    days: int = 15,
    reg: ModelRegistry = Depends(get_registry),
) -> WeatherForecast:
    """15-day weather forecast for a Karnataka district."""
    if not 1 <= days <= 60:
        raise HTTPException(status_code=422, detail="days must be between 1 and 60")
    try:
        return get_weather_forecast(
            bundle=reg.weather_bundle,
            weather_hist=reg.weather_hist,
            district=district,
            days=days,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Weather forecast error")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Growth router
# ──────────────────────────────────────────────────────────────────────────────
growth_router = APIRouter(prefix="/growth", tags=["Crop Growth"])


@growth_router.post("", response_model=GrowthPlan)
async def get_growth_plan(
    req: GrowthRequest,
    reg: ModelRegistry = Depends(get_registry),
) -> GrowthPlan:
    """Predict crop growth stages using GDD heat-unit model."""
    try:
        return predict_growth_plan(
            crop=req.crop.lower(),
            sow_date=req.sow_date,
            district=req.district,
            crop_stages=reg.crop_stages,
            crop_master=reg.crop_master,
            perennial_cal=reg.perennial_cal,
            weather_hist=reg.weather_hist,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Location helpers router
# ──────────────────────────────────────────────────────────────────────────────
location_router = APIRouter(prefix="/location", tags=["Location"])


@location_router.get("/taluks")
async def list_taluks(
    district: str | None = None,
    reg: ModelRegistry = Depends(get_registry),
):
    """List all Karnataka taluks (optionally filter by district)."""
    df = reg.taluk_soil
    if district:
        df = df[df["district"].str.lower() == district.lower()]
    return {
        "total": len(df),
        "taluks": df[["taluk", "district", "agro_zone", "dominant_soil"]].to_dict("records"),
    }


@location_router.get("/districts")
async def list_districts(reg: ModelRegistry = Depends(get_registry)):
    """List all Karnataka districts available in the system."""
    districts = sorted(reg.taluk_soil["district"].unique().tolist())
    return {"total": len(districts), "districts": districts}


@location_router.get("/crops")
async def list_crops(reg: ModelRegistry = Depends(get_registry)):
    """List all crops supported by the recommendation model."""
    crops = sorted(reg.crop_encoder.classes_.tolist())
    return {"total": len(crops), "crops": crops}
