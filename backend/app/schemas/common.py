"""
PriceNest — Common Pydantic Response Envelopes & Pagination
"""

from datetime import datetime, timezone
from typing import Generic, List, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

T = TypeVar("T")


class MetaResponse(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    request_id: str = Field(default_factory=lambda: str(uuid4()))


class StandardResponse(BaseModel, Generic[T]):
    """Canonical PriceNest success envelope matching API contracts."""
    success: bool = True
    data: T
    meta: MetaResponse = Field(default_factory=MetaResponse)


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str
    type: Optional[str] = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: List[ErrorDetail] = Field(default_factory=list)


class StandardErrorResponse(BaseModel):
    """Canonical PriceNest error envelope matching API contracts."""
    success: bool = False
    error: ErrorBody
    meta: MetaResponse = Field(default_factory=MetaResponse)
