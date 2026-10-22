"""
PriceNest — Private User Prediction History Endpoints
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.history import (
    HistoryDetailData,
    HistoryListResponseData,
)
from backend.app.services.auth_service import get_current_user
from backend.app.services.history_service import history_service

router = APIRouter(prefix="/history", tags=["Prediction History"])


@router.get(
    "",
    response_model=StandardResponse[HistoryListResponseData],
    status_code=status.HTTP_200_OK,
    summary="Retrieve paginated prediction history for authenticated user",
)
async def get_history(
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[HistoryListResponseData]:
    history_data = await history_service.get_user_history(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return StandardResponse(data=history_data)


@router.get(
    "/{prediction_id}",
    response_model=StandardResponse[HistoryDetailData],
    status_code=status.HTTP_200_OK,
    summary="Retrieve details of a saved prediction",
)
async def get_prediction_detail(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[HistoryDetailData]:
    detail = await history_service.get_user_prediction_detail(
        db=db,
        user_id=current_user.id,
        prediction_id=prediction_id,
    )
    return StandardResponse(data=detail)
