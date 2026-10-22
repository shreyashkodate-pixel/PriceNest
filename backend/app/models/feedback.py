"""
PriceNest — Valuation Feedback & Ground Truth Model
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class ValuationFeedback(Base):
    __tablename__ = "valuation_feedback"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    prediction_request_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("prediction_requests.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    feedback_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    reported_actual_price_inr: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    comments: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    prediction: Mapped["PredictionRequest"] = relationship(
        "PredictionRequest",
        back_populates="feedback",
    )
