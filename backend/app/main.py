"""
AgroTech FastAPI Application – production-ready entry point.

Start with:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
import sys
from pathlib import Path
from typing import AsyncGenerator

# Ensure root workspace is in sys.path so 'plugin' can be loaded
_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import (
    API_PREFIX, CORS_ORIGINS, DEBUG, PROJECT_NAME
)
from app.model_loader import registry
from app.routers.recommend import router as recommend_router
from app.routers.others import (
    growth_router, location_router, weather_router,
)
from app.schemas import HealthResponse

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── lifespan: load models once on startup ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    logger.info("🌱  AgroTech API starting …")
    t0 = time.time()
    registry.load()
    logger.info("✅  Startup complete in %.1f s", time.time() - t0)
    yield
    logger.info("🛑  AgroTech API shutting down.")


# ── app ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=PROJECT_NAME,
    version="1.0.0",
    description=(
        "AI-based agriculture decision support system for Karnataka. "
        "Provides crop recommendations, weather forecasting, growth stage "
        "prediction, and yield estimation."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── request timing middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    t0 = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(time.time() - t0) * 1000:.1f}"
    return response


# ── routers ───────────────────────────────────────────────────────────────────
app.include_router(recommend_router, prefix=API_PREFIX)
app.include_router(weather_router,   prefix=API_PREFIX)
app.include_router(growth_router,    prefix=API_PREFIX)
app.include_router(location_router,  prefix=API_PREFIX)

# ── dynamic plugins ───────────────────────────────────────────────────────────
try:
    from plugin.loader import load_plugins
    load_plugins(app)
except Exception as e:
    logger.warning("Could not load dynamic plugins: %s", e)


# ── health check ──────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    if not registry._loaded:
        registry.load()
    loaded = registry._loaded
    return HealthResponse(
        status="healthy" if loaded else "loading",
        version="1.0.0",
        models_loaded=loaded,
        districts_available=len(registry.weather_bundle["districts"]) if loaded else 0,
        crops_available=len(registry.crop_encoder.classes_) if loaded else 0,
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api": API_PREFIX,
    }


# ── global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please check server logs."},
    )


# ── dev runner ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    from app.config import HOST, PORT
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=DEBUG, workers=1)
