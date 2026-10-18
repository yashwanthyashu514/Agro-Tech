"""
AgroTech – Central configuration
Reads from environment variables / .env file via python-dotenv.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent  # d:/Agrotech/backend
_cand1 = BASE_DIR.parent / "AgroTech_All_5_Modules"
_cand2 = _cand1 / "AgroTech_All_5_Modules"
DATA_DIR = _cand2 if (_cand2 / "1_location_soil").exists() else _cand1
MODELS_DIR = BASE_DIR / "models_store"

# ── model file paths (prefer freshly-retrained models_store, fallback to original) ──
_ORIG_CROP    = DATA_DIR / "2_crop_recommendation" / "models" / "crop_model.pkl"
_ORIG_WEATHER = DATA_DIR / "3_weather_prediction" / "models" / "weather_model_karnataka.pkl"
_ORIG_YIELD   = DATA_DIR / "5_yield_prediction" / "yield_model.pkl"

CROP_MODEL_PATH    = MODELS_DIR / "crop_model.pkl"    if (MODELS_DIR / "crop_model.pkl").exists()    else _ORIG_CROP
WEATHER_MODEL_PATH = MODELS_DIR / "weather_model_karnataka.pkl" if (MODELS_DIR / "weather_model_karnataka.pkl").exists() else _ORIG_WEATHER
YIELD_MODEL_PATH   = MODELS_DIR / "yield_model.pkl"   if (MODELS_DIR / "yield_model.pkl").exists()   else _ORIG_YIELD

# ── reference CSV paths ────────────────────────────────────────────────────────
TALUK_SOIL_CSV       = DATA_DIR / "1_location_soil" / "karnataka_taluk_soil.csv"
CROP_GROWTH_CSV      = DATA_DIR / "4_crop_growth" / "crop_growth_stages.csv"
CROP_MASTER_CSV      = DATA_DIR / "4_crop_growth" / "crop_growth_master.csv"
PERENNIAL_CSV        = DATA_DIR / "4_crop_growth" / "perennial_crop_calendar.csv"
YIELD_FEATURES_CSV   = DATA_DIR / "5_yield_prediction" / "yield_karnataka_features.csv"
WEATHER_HISTORY_CSV  = DATA_DIR / "3_weather_prediction" / "weather_karnataka_districts.csv"
DISTRICT_PROFILE_CSV = DATA_DIR / "1_location_soil" / "karnataka_district_profile.csv"

# ── API settings ───────────────────────────────────────────────────────────────
API_VERSION  = "v1"
API_PREFIX   = f"/api/{API_VERSION}"
PROJECT_NAME = "AgroTech AI Agriculture Intelligence System"
DEBUG        = os.getenv("DEBUG", "false").lower() == "true"
HOST         = os.getenv("HOST", "0.0.0.0")
PORT         = int(os.getenv("PORT", 8000))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ── caching ────────────────────────────────────────────────────────────────────
MODEL_CACHE_TTL  = int(os.getenv("MODEL_CACHE_TTL", 0))   # 0 = never expire
WEATHER_CACHE_TTL = int(os.getenv("WEATHER_CACHE_TTL", 3600))  # 1 hour

# ── season / domain constants ─────────────────────────────────────────────────
SEASON_MONTHS = {"Kharif": [6, 7, 8, 9], "Rabi": [10, 11, 12, 1], "Summer": [2, 3, 4, 5]}
SEASON_SOW    = {"Kharif": "06-20", "Rabi": "10-20", "Summer": "02-01"}

YIELD_CROP_MAP = {
    "rice": "Rice", "maize": "Maize", "chickpea": "Gram",
    "pigeonpeas": "Arhar/Tur", "mungbean": "Moong(Green Gram)",
    "blackgram": "Urad", "mothbeans": "Moth", "lentil": "Masoor",
    "cotton": "Cotton(lint)", "jute": "Jute", "banana": "Banana",
    "mango": "Mango", "grapes": "Grapes", "pomegranate": "Pome Granet",
    "watermelon": "Water Melon", "papaya": "Papaya", "coffee": "Coffee",
    "kidneybeans": "Rajmash Kholar", "coconut": "Coconut",
    "orange": "Orange", "apple": "Apple", "muskmelon": "Musk Melon",
}

PERENNIAL_CROPS = {"mango", "coconut", "coffee", "grapes", "pomegranate", "orange", "apple"}

RAIN_DAY_MM = 2.5
