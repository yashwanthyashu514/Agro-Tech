"""
Model loader with lazy-loading, thread-safe singleton pattern and version checking.
All heavy .pkl files are loaded once at startup and kept in memory.
"""
import logging
import threading
import warnings
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd

from app.config import (
    CROP_MASTER_CSV, CROP_MODEL_PATH, PERENNIAL_CSV,
    TALUK_SOIL_CSV, WEATHER_HISTORY_CSV, WEATHER_MODEL_PATH,
    YIELD_FEATURES_CSV, YIELD_MODEL_PATH, CROP_GROWTH_CSV,
    PERENNIAL_CROPS, SEASON_MONTHS, RAIN_DAY_MM,
)

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

_lock = threading.Lock()


class ModelRegistry:
    """Thread-safe container for all loaded models and reference dataframes."""

    _instance: Optional["ModelRegistry"] = None

    def __new__(cls) -> "ModelRegistry":
        with _lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._loaded = False
        return cls._instance

    def load(self) -> None:
        with _lock:
            if self._loaded:
                return
            logger.info("Loading all AI models …")
            self._load_crop_model()
            self._load_weather_model()
            self._load_yield_model()
            self._load_reference_data()
            self._loaded = True
            logger.info("✅  All models loaded and ready.")

    # ──────────────────────────────────────────────────────────────────────────
    # individual loaders
    # ──────────────────────────────────────────────────────────────────────────
    def _load_crop_model(self) -> None:
        path = Path(CROP_MODEL_PATH)
        if not path.exists():
            raise FileNotFoundError(f"Crop model not found: {path}. Run train_crop_model.py first.")
        bundle = joblib.load(path)
        self.crop_model       = bundle["model"]
        self.crop_encoder     = bundle["label_encoder"]
        self.crop_features    = bundle["features"]
        self.crop_ranges      = bundle["crop_ranges"]
        self.crop_model_name  = bundle.get("model_name", "Unknown")
        logger.info("Crop model: %s | classes=%d", self.crop_model_name,
                    len(self.crop_encoder.classes_))

    def _load_weather_model(self) -> None:
        path = Path(WEATHER_MODEL_PATH)
        if not path.exists():
            raise FileNotFoundError(
                f"Weather model not found: {path}. Run train_karnataka_weather_model.py first.")
        self.weather_bundle = joblib.load(path)
        logger.info("Weather model loaded | districts=%d",
                    len(self.weather_bundle["districts"]))

    def _load_yield_model(self) -> None:
        path = Path(YIELD_MODEL_PATH)
        if not path.exists():
            raise FileNotFoundError(f"Yield model not found: {path}. Run train_yield_model.py first.")
        bundle = joblib.load(path)
        self.yield_model      = bundle["model"]
        self.yield_features   = bundle["features"]
        self.yield_model_name = bundle.get("model_name", "Unknown")
        logger.info("Yield model: %s", self.yield_model_name)

    def _load_reference_data(self) -> None:
        self.taluk_soil    = pd.read_csv(TALUK_SOIL_CSV)
        self.crop_stages   = pd.read_csv(CROP_GROWTH_CSV)
        self.crop_master   = pd.read_csv(CROP_MASTER_CSV).set_index("crop")
        self.perennial_cal = pd.read_csv(PERENNIAL_CSV).set_index("crop") if Path(PERENNIAL_CSV).exists() else pd.DataFrame()
        self.yield_feats   = pd.read_csv(YIELD_FEATURES_CSV)
        self.weather_hist  = pd.read_csv(WEATHER_HISTORY_CSV, parse_dates=["date"])
        logger.info("Reference data loaded: %d taluks | %d yield rows | %s weather rows",
                    len(self.taluk_soil), len(self.yield_feats), len(self.weather_hist))


# module-level singleton
registry = ModelRegistry()


def get_registry() -> ModelRegistry:
    """Dependency-injection helper for FastAPI routes."""
    if not registry._loaded:
        registry.load()
    return registry
