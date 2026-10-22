"""
PriceNest — Model Registry & Governance Schemas
"""

from typing import Any, Dict, List

from pydantic import BaseModel


class ModelActiveResponseData(BaseModel):
    version: str
    model_name: str
    algorithm: str
    training_date: str
    dataset_provenance: str
    offline_metrics: Dict[str, Any]
    features_used: List[str]
