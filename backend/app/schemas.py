"""
Pydantic v2 request / response schemas.
All monetary/numeric fields use strict typing and validators.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ── request schemas ────────────────────────────────────────────────────────────

class RecommendRequest(BaseModel):
    taluk: Optional[str] = None
    district: Optional[str] = None
    season: str = Field("Kharif", pattern="^(Kharif|Rabi|Summer)$")
    N: Optional[float] = Field(None, ge=0, le=200, description="Nitrogen kg/ha")
    P: Optional[float] = Field(None, ge=0, le=150, description="Phosphorus kg/ha")
    K: Optional[float] = Field(None, ge=0, le=150, description="Potassium kg/ha")
    ph: Optional[float] = Field(None, ge=3.0, le=10.0, description="Soil pH")
    temperature: Optional[float] = Field(None, ge=-5, le=55, description="°C avg season temp")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="% relative humidity")
    rainfall: Optional[float] = Field(None, ge=0, le=800, description="mm avg monthly rainfall")
    sow_date: Optional[str] = Field(None, description="YYYY-MM-DD")
    top_n: int = Field(5, ge=1, le=22)

    @model_validator(mode="after")
    def require_location(self) -> "RecommendRequest":
        if not self.taluk and not self.district:
            raise ValueError("Provide either 'taluk' or 'district'.")
        return self


class WeatherRequest(BaseModel):
    district: str
    days: int = Field(15, ge=1, le=60)


class GrowthRequest(BaseModel):
    crop: str
    sow_date: str = Field(..., description="YYYY-MM-DD")
    district: str


class YieldRequest(BaseModel):
    crop: str
    district: str
    season: str = Field(..., pattern="^(Kharif|Rabi|Summer)$")


# ── response schemas ───────────────────────────────────────────────────────────

class LocationInfo(BaseModel):
    taluk: str
    district: str
    agro_zone: str
    agro_zone_no: int
    dominant_soil: str
    secondary_soil: Optional[str]
    rainfall_range_mm: str


class SoilInfo(BaseModel):
    N: float
    P: float
    K: float
    ph: float
    source: str


class WeatherInfo(BaseModel):
    temperature: float
    humidity: float
    rainfall: float
    source: str


class CropReason(BaseModel):
    feature: str
    value: float
    typical_range: str
    status: str     # "OK" or "OUT"


class CropYield(BaseModel):
    predicted_t_ha: float
    district_avg_3yr_t_ha: Optional[float]
    based_on_year: Optional[int]


class CropRecommendation(BaseModel):
    rank: int
    crop: str
    suitability_score: float
    suitability_pct: float
    season: str
    duration_days: Optional[int]
    water_requirement: Optional[str]
    min_temp_c: Optional[float]
    max_temp_c: Optional[float]
    min_rainfall_mm: Optional[float]
    max_rainfall_mm: Optional[float]
    profitability: Optional[str] = None
    profit_estimate: Optional[str] = None
    ease_of_growth: Optional[str] = None
    soil_suitability: Optional[str] = None
    market_demand: Optional[str] = None
    reasons: List[CropReason]
    yield_prediction: Optional[CropYield]


class GrowthStage(BaseModel):
    stage: str
    start_date: str
    end_date: Optional[str]
    days_after_sowing: Optional[str]
    kc: Optional[float]
    water_need: Optional[str]
    critical_irrigation: Optional[str]
    weather_used: Optional[str]


class GrowthPlan(BaseModel):
    crop: str
    sow_date: str
    prediction_type: str
    total_duration_days: Optional[int]
    base_temp_c: Optional[float]
    stages: List[GrowthStage]


class WeatherDay(BaseModel):
    date: str
    days_ahead: int
    rain_probability_pct: float
    expected_rain_mm: float
    temp_max_c: Optional[float]
    temp_min_c: Optional[float]
    humidity_pct: Optional[float]
    source: str
    rain_risk: str           # "Low" / "Moderate" / "High"


class WeatherForecast(BaseModel):
    district: str
    forecast_from: str
    days: List[WeatherDay]
    summary: Dict[str, Any]


class RecommendResponse(BaseModel):
    request_id: str
    location: LocationInfo
    season: str
    soil: SoilInfo
    weather: WeatherInfo
    recommendations: List[CropRecommendation]
    growth_plan: Optional[GrowthPlan]
    weather_forecast: Optional[WeatherForecast]
    model_info: Dict[str, str]


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: bool
    districts_available: int
    crops_available: int
