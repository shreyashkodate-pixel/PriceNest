"""
PriceNest — Private Prediction History Pydantic Schemas
"""

from typing import Any, Dict, List

from pydantic import BaseModel


class HistoryItemData(BaseModel):
    prediction_id: str
    locality_name: str
    total_sqft: float
    bhk: float
    predicted_price_inr: float
    formatted_price: str
    model_version: str
    created_at: str


class HistoryListResponseData(BaseModel):
    total: int
    items: List[HistoryItemData]


class HistoryDetailData(BaseModel):
    prediction_id: str
    locality_name: str
    input_features: Dict[str, Any]
    predicted_price_inr: float
    formatted_price: str
    per_sqft_rate_inr: float
    model_version: str
    created_at: str
