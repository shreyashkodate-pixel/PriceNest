"""
PriceNest — Pune Micro-Market Localities Reference Model
"""
from __future__ import annotations

from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin


class Locality(Base, TimestampMixin):
    __tablename__ = "localities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    zone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    locality_type: Mapped[str] = mapped_column(
        String(32),
        default="Mid-Range",
        nullable=False,
    )
    pincode: Mapped[Optional[str]] = mapped_column(
        String(12),
        index=True,
        nullable=True,
    )
    latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    benchmark_price_per_sqft: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        nullable=False,
    )

    # Relationships
    predictions: Mapped[List["PredictionRequest"]] = relationship(
        "PredictionRequest",
        back_populates="locality",
    )
