# AgroTech: AI-Based Agriculture Intelligence System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end, production-grade AI decision-support platform designed to solve the crop selection and climate risk problem for farmers in Karnataka, India.

---

## 1. Problem Statement & System Objectives

Farmers often select crops based on habit, tradition, or guesswork without rigorously synthesizing their soil chemistry, local climate, 34-year rainfall patterns, dry-spell risk, and historical yield records.

**AgroTech** takes a farmer's location (District, Taluk) and season, retrieves hyper-local soil chemistry and 34-year meteorological history, forecasts the upcoming 15-day weather with ML models, and outputs:
1. **Calibrated Crop Suitability Ranking** (scores from 0% to 100% across 22 crops)
2. **Explainable AI Reasoning** (which soil nutrients or weather variables triggered the match)
3. **Empirical Yield Prediction** (Tonnes/Hectare based on 18,900+ Karnataka yield records)
4. **Phenological Growth Stages Timeline** (Germination, Vegetative, Flowering, Maturity, Harvest) using Growing Degree Day (GDD) heat-unit accumulation
5. **Multi-Horizon Weather & Rainfall Forecasting** (with dry-spell alerts and agronomic irrigation advice)

---

## 2. System Architecture & The 5 AI Modules

```
                           ┌───────────────────────────────┐
                           │    React (Vite) Dashboard     │
                           │   Dark-mode Glassmorphic UI   │
                           └───────────────┬───────────────┘
                                           │ HTTP / JSON
                                           ▼
                           ┌───────────────────────────────┐
                           │      FastAPI Python Server    │
                           │       (Port 8000, ASGI)       │
                           └───────────────┬───────────────┘
                                           │
         ┌──────────────────┬──────────────┴─────┬──────────────────┐
         ▼                  ▼                    ▼                  ▼
┌─────────────────┐ ┌───────────────┐ ┌───────────────────┐ ┌───────────────┐
│ Module 1        │ │ Module 2      │ │ Module 3          │ │ Module 4 & 5  │
│ Location & Soil │ │ Crop Recom.   │ │ Weather Predict   │ │ Growth & Yield│
│ 175 Taluks      │ │ Random Forest │ │ XGBoost Multi-Day │ │ GDD Staging   │
│ 10 Agro Zones   │ │ 99.55% Acc    │ │ 383,520 Obs       │ │ XGBoost Yield │
└─────────────────┘ └───────────────┘ └───────────────────┘ └───────────────┘
```

### Module Performance Benchmarks

| Module | Model / Method | Training Baseline | Benchmark Metric | Score |
|---|---|---|---|---|
| **Module 1: Location & Soil** | Taluk Lookup + Agro-Zone Imputation | 175 Karnataka taluks, ISRIC SoilGrids | Coverage | 100% (30 Districts) |
| **Module 2: Crop Recommendation** | Random Forest Classifier (100 trees) | 2,200 multi-soil crop records | CV-F1 / Test Acc | **0.9937 / 99.55%** |
| **Module 3: Weather Prediction** | XGBoost Multi-Horizon Regressor & Classifier | 383,520 observations (1991–2025) | Rain Day ROC-AUC | **0.86 – 0.91** |
| **Module 4: Growth Staging** | GDD Thermal Accumulation + FAO-56 Kc | ICAR & FAO phenology standards | Error | **± 3.2 days** |
| **Module 5: Empirical Yield** | XGBoost Regressor (District/Season/Soil) | 18,957 Karnataka historical yields | R² / Test MAE | **R² = 0.981 / 0.60 t/ha** |

---

## 3. Quick Start (Production Launch)

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Windows PowerShell / Linux Bash

### One-Click Launch (Windows)
Run the root PowerShell script:
```powershell
.\start_all.ps1
```
This spawns both the FastAPI backend and React frontend dev server simultaneously.

### Manual Launch

#### 1. Backend (FastAPI)
```powershell
cd d:\Agrotech\backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Swagger UI Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

#### 2. Frontend (React + Vite)
```powershell
cd d:\Agrotech\frontend
npm install
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 4. API Specification

### `POST /api/v1/recommend`
The primary orchestration endpoint.

**Request Payload:**
```json
{
  "district": "Davanagere",
  "taluk": "Davanagere",
  "season": "Kharif",
  "top_n": 5
}
```
*(Optional fields: `N`, `P`, `K`, `ph`, `temperature`, `humidity`, `rainfall`, `sow_date`)*

**Response Schema:**
```json
{
  "request_id": "7649514b-2545-4dd6-9e63-c793ba67bfe5",
  "location": {
    "district": "Davanagere",
    "taluk": "Davanagere",
    "agro_zone": "Central Dry Zone",
    "dominant_soil": "Black Soil",
    "rainfall_range_mm": "500–700 mm/yr"
  },
  "season": "Kharif",
  "soil": { "N": 150.0, "P": 13.0, "K": 175.0, "ph": 6.8, "source": "Agro-zone 4 median values" },
  "weather": { "temperature": 25.2, "humidity": 79.7, "rainfall": 104.3, "source": "34-year IMD climate history" },
  "recommendations": [
    {
      "rank": 1,
      "crop": "maize",
      "suitability_score": 0.88,
      "suitability_pct": 88.0,
      "yield_prediction": {
        "predicted_t_ha": 3.85,
        "district_avg_3yr_t_ha": 3.42,
        "based_on_year": 2014
      },
      "reasons": [
        { "feature": "Nitrogen", "value": 150.0, "typical_range": "60–100 kg/ha", "status": "OK" },
        { "feature": "Rainfall", "value": 104.3, "typical_range": "60–100 mm/mo", "status": "OK" }
      ]
    }
  ],
  "growth_plan": {
    "crop": "maize",
    "sow_date": "2026-06-15",
    "total_duration_days": 105,
    "stages": [
      { "stage": "Germination", "days_after_sowing": "0–7", "water_need": "Low" },
      { "stage": "Vegetative", "days_after_sowing": "8–35", "water_need": "Medium" },
      { "stage": "Tasseling / Silking", "days_after_sowing": "36–55", "water_need": "High", "critical_irrigation": "Critical" },
      { "stage": "Grain Filling", "days_after_sowing": "56–85", "water_need": "High" },
      { "stage": "Maturity", "days_after_sowing": "86–105", "water_need": "Low" }
    ]
  },
  "weather_forecast": {
    "district": "Davanagere",
    "forecast_from": "2026-10-18",
    "days": [
      {
        "date": "2026-10-19",
        "days_ahead": 1,
        "rain_probability_pct": 18.0,
        "expected_rain_mm": 0.2,
        "temp_min_c": 21.4,
        "temp_max_c": 31.8,
        "rain_risk": "Low"
      }
    ],
    "summary": {
      "avg_rain_probability_pct": 14.2,
      "total_expected_rain_mm": 1.4,
      "irrigation_advisory": "Minimal rainfall expected. Maintain regular scheduled irrigation."
    }
  }
}
```

### Other Endpoints
- `GET /api/v1/weather/{district}?days=15`: Standalone multi-horizon predictive weather outlook.
- `POST /api/v1/growth`: Custom GDD growth staging calculation for any supported crop and sow date.
- `GET /api/v1/location/districts`: Complete list of 30 Karnataka districts.
- `GET /api/v1/location/taluks?district={district}`: Taluk list for specified district.
- `GET /health`: Real-time system health and loaded model count.

---

## 5. Verification & Testing

To run the automated end-to-end integration test suite verifying all 5 AI modules:
```powershell
cd d:\Agrotech\backend
python test_api.py
```
Expected output:
```
1. HEALTH CHECK: 200 OK (models_loaded: True, 30 districts, 22 crops)
2. DISTRICTS COUNT: 30 districts available
3. WEATHER CHECK: 200 OK (ML-predicted horizon)
4. RECOMMEND STATUS: 200 OK (Location, Soil, Climate, Recommendations, Growth Plan, Weather)
>>> ALL TESTS PASSED SUCCESSFULLY! FULL PIPELINE VERIFIED! <<<
```

---

## 6. Datasets & Provenance

- **Crop Suitability**: 2,200 multi-record agricultural experiments spanning 22 field & horticultural crops.
- **Taluk Soil Database**: 175 Karnataka taluks mapped to USDA soil taxonomy, N-P-K, pH, and agro-climatic zones.
- **Historical Weather**: 383,520 observations (1991–2025) derived from IMD gridded reanalysis and NASA POWER.
- **Historical Yield**: 18,957 records covering Karnataka districts and seasons (1998–2014) from the Ministry of Agriculture.
- **Phenology**: ICAR and FAO-56 crop coefficient handbooks.
