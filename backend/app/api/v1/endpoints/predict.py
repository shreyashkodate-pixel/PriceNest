"""
PriceNest — Property Valuation Prediction Endpoint
"""

import hashlib
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.prediction import (
    ModelMetadataResponse,
    PredictionData,
    PredictionRequestSchema,
    PriceRange,
)
from backend.app.services.auth_service import get_optional_current_user
from backend.app.services.history_service import history_service
from backend.app.services.locality_service import locality_service
from backend.app.services.ml_service import ml_service

router = APIRouter(tags=["Property Valuation"])


def hash_client_ip(ip: Optional[str]) -> Optional[str]:
    """Create anonymized SHA-256 hash of client IP for audit privacy."""
    if not ip:
        return None
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()[:32]


async def process_prediction(
    payload: PredictionRequestSchema,
    request: Request,
    db: AsyncSession,
    current_user: Optional[User],
    x_session_id: Optional[str],
) -> StandardResponse[PredictionData]:
    # Resolve locality record if available
    locality = await locality_service.get_by_name(db, payload.locality_name)
    locality_id = locality.id if locality else payload.locality_id
    locality_tier = locality.locality_type if locality else payload.locality_type

    # Prepare inputs for ML Service
    raw_inputs = payload.model_dump()
    if locality_tier:
        raw_inputs["locality_type"] = locality_tier

    # Execute ML Inference
    result = ml_service.predict_price(raw_inputs)

    # Anonymize client IP
    client_ip = request.client.host if request.client else None
    ip_hash = hash_client_ip(client_ip)
    session_id = x_session_id or str(uuid4())
    user_id = current_user.id if current_user else None

    # Persist immutable prediction request audit entry
    prediction_id = await history_service.record_prediction(
        db=db,
        session_id=session_id,
        user_id=user_id,
        locality_id=locality_id,
        locality_name_raw=payload.locality_name,
        total_sqft=payload.total_sqft,
        bhk=payload.bhk,
        bathrooms=payload.bathrooms,
        balconies=payload.balconies,
        input_features=raw_inputs,
        prediction_result=result,
        client_ip_hash=ip_hash,
    )

    data = PredictionData(
        prediction_id=prediction_id,
        predicted_price_inr=result["predicted_price_inr"],
        predicted_price_lakhs=result["predicted_price_lakhs"],
        formatted_price=result["formatted_price"],
        price_range=PriceRange(
            min_inr=result["price_range"]["min_inr"],
            max_inr=result["price_range"]["max_inr"],
            formatted_range=result["price_range"]["formatted_range"],
        ),
        per_sqft_rate_inr=result["per_sqft_rate_inr"],
        formatted_per_sqft_rate=result["formatted_per_sqft_rate"],
        confidence_score=0.85,
        model_metadata=ModelMetadataResponse(
            version=result["model_metadata"]["version"],
            algorithm=result["model_metadata"]["algorithm"],
            latency_ms=result["model_metadata"]["latency_ms"],
        ),
        disclaimer=result["disclaimer"],
    )

    return StandardResponse(data=data)


@router.post(
    "/predict/price",
    response_model=StandardResponse[PredictionData],
    status_code=status.HTTP_200_OK,
    summary="Predict Pune residential property price",
)
async def predict_price(
    payload: PredictionRequestSchema,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    x_session_id: Optional[str] = Header(None),
) -> StandardResponse[PredictionData]:
    return await process_prediction(payload, request, db, current_user, x_session_id)


@router.post(
    "/predictions",
    response_model=StandardResponse[PredictionData],
    status_code=status.HTTP_200_OK,
    summary="Predict property price (API specification alias)",
    include_in_schema=False,
)
async def predict_price_alias(
    payload: PredictionRequestSchema,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    x_session_id: Optional[str] = Header(None),
) -> StandardResponse[PredictionData]:
    return await process_prediction(payload, request, db, current_user, x_session_id)
