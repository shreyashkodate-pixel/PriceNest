"""
PriceNest — Pune Micro-Market Localities Pydantic Schemas
"""

from typing import List, Optional

from pydantic import BaseModel


class LocalityItemData(BaseModel):
    id: str
    name: str
    slug: str
    zone: str
    locality_type: str
    pincode: Optional[str] = None
    benchmark_price_per_sqft: Optional[float] = None
    is_active: bool = True


class LocalityListResponseData(BaseModel):
    total: int
    items: List[LocalityItemData]
