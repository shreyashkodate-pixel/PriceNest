"""
PriceNest — Valuation Query Audit Ledger & Private Prediction History Model
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class PredictionRequest(Base):
    __tablename__ = "prediction_requests"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    locality_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("localities.id", ondelete="SET NULL"),
        nullable=True,
    )
    locality_name_raw: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    total_sqft: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    bhk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    bathrooms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    balconies: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    input_features: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    predicted_price_inr: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    predicted_range_min_inr: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    predicted_range_max_inr: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    per_sqft_rate_inr: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    model_version: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
    )
    latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    client_ip_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="predictions",
    )
    locality: Mapped[Optional["Locality"]] = relationship(
        "Locality",
        back_populates="predictions",
    )
    feedback: Mapped[Optional["ValuationFeedback"]] = relationship(
        "ValuationFeedback",
        uselist=False,
        back_populates="prediction",
        cascade="all, delete-orphan",
    )
    saved_valuations: Mapped[List["SavedValuation"]] = relationship(
        "SavedValuation",
        back_populates="prediction",
        cascade="all, delete-orphan",
    )
