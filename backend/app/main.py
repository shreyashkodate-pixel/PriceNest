"""
PriceNest — FastAPI Application Entrypoint
Initializes lifespan events, CORS middleware, centralized exception handling,
and REST routing for Pune residential real-estate price prediction.
"""

import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.api.v1.endpoints import health
from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.core.database import async_engine, check_db_connection
from backend.app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    starlette_http_exception_handler,
    validation_exception_handler,
)
from backend.app.core.logging import logger
from backend.app.models.base import Base
from backend.app.services.ml_service import ml_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Loads ML model into memory and verifies database readiness at startup.
    """
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode...")

    # 1. Load ML Model Pipeline
    try:
        ml_service.load_model()
    except Exception as e:
        logger.error(f"Model initialization failed: {e}. Inference will return 503 until resolved.")

    # 2. Check Database Connection & ensure schemas for local SQLite dev if active
    if "sqlite" in settings.DATABASE_URL:
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("SQLite local development tables verified.")
        except Exception as e:
            logger.warning(f"Could not initialize local tables: {e}")

    db_ready = await check_db_connection()
    if db_ready:
        logger.info("Database connection established successfully.")
    else:
        logger.warning("Database is currently unreachable; health/ready will report degraded.")

    yield

    # Shutdown logic
    logger.info(f"Shutting down {settings.APP_NAME}...")
    await async_engine.dispose()
    logger.info("Database engine connections closed.")


app = FastAPI(
    title="PriceNest API",
    version="1.0.0",
    description=(
        "Production-ready, data-driven residential real-estate price prediction REST API "
        "for Pune, Maharashtra, India. Features verified scikit-learn ML inference, "
        "authenticated user histories, and micro-market locality benchmarks."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


@app.middleware("http")
async def correlation_and_timing_middleware(request: Request, call_next):
    """Assigns unique correlation request ID and tracks endpoint processing duration."""
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id

    start_time = time.perf_counter()
    response: Response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000.0

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# Centralized Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Health and Probes
app.include_router(health.router)

# Versioned REST API Router (/api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    """Root metadata endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "market": "Pune, Maharashtra, India",
        "documentation": "/docs",
        "health": "/health/live",
        "api_v1": settings.API_V1_STR,
    }
