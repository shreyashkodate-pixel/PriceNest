"""
PriceNest — User Account & Credentials Model
"""
from __future__ import annotations

from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    predictions: Mapped[List["PredictionRequest"]] = relationship(
        "PredictionRequest",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    saved_valuations: Mapped[List["SavedValuation"]] = relationship(
        "SavedValuation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
