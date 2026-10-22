"""
PriceNest — Valuation Feedback & Ground Truth Collection Service
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import NotFoundError
from backend.app.models.feedback import ValuationFeedback
from backend.app.models.prediction import PredictionRequest
from backend.app.schemas.feedback import (
    ValuationFeedbackRequest,
    ValuationFeedbackResponseData,
)


class FeedbackService:
    """Manages ground-truth validation and user feedback records."""

    async def submit_feedback(
        self,
        db: AsyncSession,
        prediction_id: str,
        payload: ValuationFeedbackRequest,
    ) -> ValuationFeedbackResponseData:
        # Verify prediction exists
        pred_stmt = select(PredictionRequest).where(PredictionRequest.id == prediction_id)
        pred = (await db.execute(pred_stmt)).scalar_one_or_none()
        if not pred:
            raise NotFoundError(f"Prediction '{prediction_id}' does not exist.")

        # Check if feedback already submitted for this prediction
        fb_stmt = select(ValuationFeedback).where(ValuationFeedback.prediction_request_id == prediction_id)
        existing = (await db.execute(fb_stmt)).scalar_one_or_none()

        if existing:
            existing.feedback_type = payload.feedback_type
            existing.reported_actual_price_inr = payload.reported_actual_price_inr
            existing.comments = payload.comments
            feedback_id = existing.id
        else:
            feedback = ValuationFeedback(
                prediction_request_id=prediction_id,
                feedback_type=payload.feedback_type,
                reported_actual_price_inr=payload.reported_actual_price_inr,
                comments=payload.comments,
            )
            db.add(feedback)
            await db.flush()
            feedback_id = feedback.id

        return ValuationFeedbackResponseData(
            feedback_id=feedback_id,
            prediction_id=prediction_id,
            status="recorded",
        )


feedback_service = FeedbackService()
