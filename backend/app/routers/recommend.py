"""
/api/v1/recommend  — core recommendation endpoint
"""
from __future__ import annotations

import logging
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import SEASON_MONTHS, SEASON_SOW
from app.model_loader import ModelRegistry, get_registry
from app.schemas import (
    RecommendRequest, RecommendResponse,
    LocationInfo, SoilInfo, WeatherInfo,
)
from app.services.crop_service import recommend_crops
from app.services.growth_service import predict_growth_plan
from app.services.location_service import find_location, resolve_soil, resolve_weather
from app.services.weather_service import get_weather_forecast

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommend", tags=["Recommendation"])


@router.post("", response_model=RecommendResponse, status_code=status.HTTP_200_OK)
async def get_recommendation(
    req: RecommendRequest,
    reg: ModelRegistry = Depends(get_registry),
) -> RecommendResponse:
    """
    Main prediction endpoint.
    Accepts location, optional soil values and optional weather.
    Returns ranked crop recommendations, growth plan and 15-day weather.
    """
    try:
        # ── 1. Resolve location ───────────────────────────────────────────────
        loc = find_location(reg.taluk_soil, req.taluk, req.district)
        location_info = LocationInfo(
            taluk=str(loc["taluk"]),
            district=str(loc["district"]),
            agro_zone=str(loc["agro_zone"]),
            agro_zone_no=int(loc["agro_zone_no"]),
            dominant_soil=str(loc["dominant_soil"]),
            secondary_soil=str(loc["secondary_soil"]) if loc.get("secondary_soil") else None,
            rainfall_range_mm=f"{int(loc['zone_rainfall_min_mm'])}–{int(loc['zone_rainfall_max_mm'])} mm/yr",
        )

        # ── 2. Resolve soil ───────────────────────────────────────────────────
        soil_vals, soil_src = resolve_soil(loc, req.N, req.P, req.K, req.ph)
        soil_info = SoilInfo(**soil_vals, source=soil_src)

        # ── 3. Resolve weather ────────────────────────────────────────────────
        wx_vals, wx_src = resolve_weather(
            loc, req.season, reg.weather_hist,
            req.temperature, req.humidity, req.rainfall,
        )
        weather_info = WeatherInfo(**wx_vals, source=wx_src)

        # ── 4. Crop recommendations ───────────────────────────────────────────
        recommendations = recommend_crops(
            model=reg.crop_model,
            encoder=reg.crop_encoder,
            features=reg.crop_features,
            crop_ranges=reg.crop_ranges,
            soil=soil_vals,
            weather=wx_vals,
            crop_master=reg.crop_master,
            yield_feats=reg.yield_feats,
            yield_model=reg.yield_model,
            yield_features=reg.yield_features,
            district=location_info.district,
            season=req.season,
            top_n=req.top_n,
            soil_type=location_info.dominant_soil,
        )

        # ── 5. Growth plan for top crop ───────────────────────────────────────
        top_crop = recommendations[0].crop if recommendations else None
        sow_date = req.sow_date or f"{date.today().year}-{SEASON_SOW[req.season]}"
        growth_plan = None
        if top_crop:
            growth_plan = predict_growth_plan(
                crop=top_crop,
                sow_date=sow_date,
                district=location_info.district,
                crop_stages=reg.crop_stages,
                crop_master=reg.crop_master,
                perennial_cal=reg.perennial_cal,
                weather_hist=reg.weather_hist,
            )

        # ── 6. 15-day weather forecast ────────────────────────────────────────
        weather_forecast = None
        try:
            weather_forecast = get_weather_forecast(
                bundle=reg.weather_bundle,
                weather_hist=reg.weather_hist,
                district=location_info.district,
                days=15,
            )
        except Exception as e:
            logger.warning("Weather forecast unavailable: %s", e)

        return RecommendResponse(
            request_id=str(uuid.uuid4()),
            location=location_info,
            season=req.season,
            soil=soil_info,
            weather=weather_info,
            recommendations=recommendations,
            growth_plan=growth_plan,
            weather_forecast=weather_forecast,
            model_info={
                "crop_model": reg.crop_model_name,
                "yield_model": reg.yield_model_name,
                "weather_model": "XGBoost multi-horizon",
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.exception("Recommendation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal AI error: {str(e)}",
        )
