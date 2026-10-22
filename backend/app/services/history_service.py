"""
PriceNest — Private Prediction History & Audit Logging Service
Enforces strict owner-only access boundaries for persisted valuations.
"""

from typing import Any, Dict, Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import NotFoundError
from backend.app.models.prediction import PredictionRequest
from backend.app.schemas.history import (
    HistoryDetailData,
    HistoryItemData,
    HistoryListResponseData,
)


class HistoryService:
    """Manages prediction audit persistence and private history access."""

    async def record_prediction(
        self,
        db: AsyncSession,
        session_id: str,
        user_id: Optional[str],
        locality_id: Optional[str],
        locality_name_raw: str,
        total_sqft: float,
        bhk: float,
        bathrooms: int,
        balconies: Optional[int],
        input_features: Dict[str, Any],
        prediction_result: Dict[str, Any],
        client_ip_hash: Optional[str] = None,
    ) -> str:
        """Persist prediction request audit entry. Returns generated prediction_id."""
        prediction_id = str(uuid4())
        record = PredictionRequest(
            id=prediction_id,
            session_id=session_id,
            user_id=user_id,
            locality_id=locality_id,
            locality_name_raw=locality_name_raw,
            total_sqft=total_sqft,
            bhk=bhk,
            bathrooms=bathrooms,
            balconies=balconies,
            input_features=input_features,
            predicted_price_inr=prediction_result["predicted_price_inr"],
            predicted_range_min_inr=prediction_result["price_range"]["min_inr"],
            predicted_range_max_inr=prediction_result["price_range"]["max_inr"],
            per_sqft_rate_inr=prediction_result["per_sqft_rate_inr"],
            model_version=prediction_result["model_metadata"]["version"],
            latency_ms=prediction_result["model_metadata"]["latency_ms"],
            client_ip_hash=client_ip_hash,
        )
        db.add(record)
        await db.flush()
        return prediction_id

    async def get_user_history(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> HistoryListResponseData:
        """Retrieve paginated prediction records owned strictly by the authenticated caller."""
        count_stmt = (
            select(func.count(PredictionRequest.id))
            .where(PredictionRequest.user_id == user_id)
        )
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(PredictionRequest)
            .where(PredictionRequest.user_id == user_id)
            .order_by(PredictionRequest.created_at.desc())
            .offset(offset)
            .limit(min(limit, 100))
        )
        result = await db.execute(stmt)
        items = result.scalars().all()

        formatted_items = []
        for item in items:
            pred_lakhs = item.predicted_price_inr / 100_000.0
            if pred_lakhs >= 100.0:
                fmt_price = f"₹{pred_lakhs/100:.2f} Cr"
            else:
                fmt_price = f"₹{pred_lakhs:.2f} Lakh"

            formatted_items.append(
                HistoryItemData(
                    prediction_id=item.id,
                    locality_name=item.locality_name_raw,
                    total_sqft=item.total_sqft,
                    bhk=item.bhk,
                    predicted_price_inr=item.predicted_price_inr,
                    formatted_price=fmt_price,
                    model_version=item.model_version,
                    created_at=item.created_at.isoformat(),
                )
            )

        return HistoryListResponseData(
            total=total,
            items=formatted_items,
        )

    async def get_user_prediction_detail(
        self,
        db: AsyncSession,
        user_id: str,
        prediction_id: str,
    ) -> HistoryDetailData:
        """
        Retrieve snapshot details for one prediction.
        Enforces strict ownership authorization: returns 404 if record is missing or owned by another user.
        """
        stmt = (
            select(PredictionRequest)
            .where(PredictionRequest.id == prediction_id)
        )
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()

        if not item or item.user_id != user_id:
            # Prevents prediction ID enumeration
            raise NotFoundError(f"Prediction record '{prediction_id}' was not found.")

        pred_lakhs = item.predicted_price_inr / 100_000.0
        if pred_lakhs >= 100.0:
            fmt_price = f"₹{pred_lakhs/100:.2f} Cr"
        else:
            fmt_price = f"₹{pred_lakhs:.2f} Lakh"

        return HistoryDetailData(
            prediction_id=item.id,
            locality_name=item.locality_name_raw,
            input_features=item.input_features,
            predicted_price_inr=item.predicted_price_inr,
            formatted_price=fmt_price,
            per_sqft_rate_inr=item.per_sqft_rate_inr,
            model_version=item.model_version,
            created_at=item.created_at.isoformat(),
        )


history_service = HistoryService()
