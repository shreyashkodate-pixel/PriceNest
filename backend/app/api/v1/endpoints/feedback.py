"""
PriceNest — Valuation Feedback Endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.feedback import (
    ValuationFeedbackRequest,
    ValuationFeedbackResponseData,
)
from backend.app.services.feedback_service import feedback_service

router = APIRouter(prefix="/valuations", tags=["Valuation Feedback"])


@router.post(
    "/{prediction_id}/feedback",
    response_model=StandardResponse[ValuationFeedbackResponseData],
    status_code=status.HTTP_201_CREATED,
    summary="Submit user feedback or ground-truth pricing for a prediction",
)
async def submit_feedback(
    prediction_id: str,
    payload: ValuationFeedbackRequest,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ValuationFeedbackResponseData]:
    result = await feedback_service.submit_feedback(db, prediction_id, payload)
    return StandardResponse(data=result)
