"""
PriceNest — Health & Readiness Probes
Endpoints for container orchestrators, load balancers, and monitoring.
"""

from typing import Any, Dict

from fastapi import APIRouter, Response, status

from backend.app.core.database import check_db_connection
from backend.app.services.ml_service import ml_service

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health/live", summary="Liveness Probe")
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes / Render liveness probe.
    Confirms server process is running and accepting event loop tasks.
    Does NOT depend on external systems.
    """
    return {"status": "healthy"}


@router.get("/health/ready", summary="Readiness Probe")
async def readiness_probe(response: Response) -> Dict[str, Any]:
    """
    Kubernetes / Render readiness probe.
    Verifies that database connection is healthy and the ML model is loaded.
    """
    db_ok = await check_db_connection()
    ml_ok = ml_service.is_ready()

    is_ready = db_ok and ml_ok
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "degraded",
        "database": "connected" if db_ok else "unavailable",
        "model_engine": "available" if ml_ok else "unavailable",
    }


@router.get("/health", include_in_schema=False)
async def health_alias(response: Response) -> Dict[str, Any]:
    """Root alias for legacy or default container health checks."""
    return await readiness_probe(response)
