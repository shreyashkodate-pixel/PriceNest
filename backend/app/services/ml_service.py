"""
PriceNest — Backend Machine Learning Service Adapter
Delegates directly to the decoupled ml.inference subsystem.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from ml.common.utils import format_inr_price, format_per_sqft
from ml.inference.services.prediction_service import prediction_service


class MLService:
    """Adapter bridging FastAPI backend to decoupled ml.inference subsystem."""

    _instance: Optional["MLService"] = None

    def __init__(self):
        self.delegate = prediction_service

    @classmethod
    def get_instance(cls) -> "MLService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def model_version(self) -> str:
        return self.delegate.model_version

    @property
    def algorithm(self) -> str:
        return self.delegate.algorithm

    def load_model(self, custom_path: Optional[Path] = None) -> None:
        self.delegate.load_model(custom_path)

    def is_ready(self) -> bool:
        return self.delegate.is_ready()

    def predict_price(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        return self.delegate.predict_price(raw_input)

    def _format_currency(self, pred_lakhs: float, per_sqft_inr: float) -> Tuple[str, str]:
        return format_inr_price(pred_lakhs), format_per_sqft(per_sqft_inr)


ml_service = MLService.get_instance()
