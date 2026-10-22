"""
PriceNest — Saved Valuations (User Bookmarks) Model
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class SavedValuation(Base):
    __tablename__ = "saved_valuations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    prediction_request_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("prediction_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    custom_title: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="saved_valuations",
    )
    prediction: Mapped["PredictionRequest"] = relationship(
        "PredictionRequest",
        back_populates="saved_valuations",
    )
