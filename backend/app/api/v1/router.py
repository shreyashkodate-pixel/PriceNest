"""
PriceNest — Root API v1 Router Definition
Aggregates all domain endpoints under the /api/v1 prefix.
"""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    auth,
    feedback,
    history,
    localities,
    models,
    predict,
)

api_router = APIRouter()

api_router.include_router(predict.router)
api_router.include_router(auth.router)
api_router.include_router(history.router)
api_router.include_router(localities.router)
api_router.include_router(feedback.router)
api_router.include_router(models.router)
