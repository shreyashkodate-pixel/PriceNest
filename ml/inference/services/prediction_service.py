"""
PriceNest — ML Prediction Service (Main Inference Entrypoint)
Orchestrates feature preparation, estimator prediction, currency conversion,
subgroup uncertainty ranges, and synthetic data disclaimers.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from ml.common.constants import (
    DEFAULT_MODEL_VERSION,
    DISCLAIMER_NOTICE,
)
from ml.common.utils import (
    calculate_price_range,
    convert_lakhs_to_inr,
    format_inr_price,
    format_per_sqft,
    normalize_furnishing,
    normalize_locality_tier,
    normalize_property_type,
)
from ml.inference.model.loader import model_loader
from ml.inference.model.predictor import predictor


class PredictionService:
    """Service providing high-level property price valuation and explanation."""

    def __init__(self, loader=model_loader, pred=predictor):
        self.loader = loader
        self.predictor = pred
        self.model_version = DEFAULT_MODEL_VERSION
        self.algorithm = "HistGradientBoostingRegressor"

    def is_ready(self) -> bool:
        """Check if underlying model pipeline is loaded and ready for serving."""
        return self.loader.is_loaded()

    def load_model(self, custom_path: Optional[Path] = None) -> None:
        """Trigger loading of model artifact."""
        self.loader.load(custom_path)

    def predict_price(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute property price estimation from raw input dictionary.
        Returns valuation breakdown in INR Lakhs and Crores with empirical ranges.
        """
        if not self.is_ready():
            try:
                self.load_model()
            except Exception:
                pass

        feature_dict = self.prepare_features(raw_input)
        df_input = pd.DataFrame([feature_dict])

        pred_lakhs, latency_ms = self.predictor.predict(df_input)

        # Base calculations
        price_inr = convert_lakhs_to_inr(pred_lakhs)
        super_area = feature_dict["Super_Area_SqFt"]
        per_sqft_rate_inr = round(price_inr / super_area, 2) if super_area > 0 else 0.0

        formatted_price = format_inr_price(pred_lakhs)
        formatted_per_sqft = format_per_sqft(per_sqft_rate_inr)
        range_min_inr, range_max_inr, formatted_range = calculate_price_range(pred_lakhs)

        return {
            "predicted_price_inr": price_inr,
            "predicted_price_lakhs": round(pred_lakhs, 2),
            "formatted_price": formatted_price,
            "price_range": {
                "min_inr": range_min_inr,
                "max_inr": range_max_inr,
                "formatted_range": formatted_range,
            },
            "per_sqft_rate_inr": per_sqft_rate_inr,
            "formatted_per_sqft_rate": formatted_per_sqft,
            "model_metadata": {
                "version": self.model_version,
                "algorithm": self.algorithm,
                "latency_ms": latency_ms,
            },
            "features_used": feature_dict,
            "disclaimer": DISCLAIMER_NOTICE,
        }

    def prepare_features(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw request parameters to the exact 14 features expected by the pipeline."""
        area = raw_input.get("total_sqft") or raw_input.get("super_area_sqft") or 1000.0
        bhk = float(raw_input.get("bhk", 2.0))
        bathrooms = int(raw_input.get("bathrooms", 2))
        floor_number = int(raw_input.get("floor_number", 2))
        total_floors = int(raw_input.get("total_floors", 10))
        age = float(raw_input.get("age_of_property", 3.0))
        dist_metro = float(raw_input.get("distance_to_metro_km", 2.5))
        dist_center = float(raw_input.get("distance_to_city_center_km") or raw_input.get("distance_to_city_Center_km", 8.0))
        parking = int(raw_input.get("parking", 1))
        lift = 1 if raw_input.get("lift_available", True) else 0
        gated = 1 if raw_input.get("gated_community", True) else 0

        loc_type = normalize_locality_tier(raw_input.get("locality_type") or raw_input.get("locality_name"))
        prop_type = normalize_property_type(raw_input.get("property_type"))
        furnishing = normalize_furnishing(raw_input.get("furnishing_status") or raw_input.get("furnishing"))

        return {
            "Super_Area_SqFt": float(area),
            "BHK": float(bhk),
            "Bathrooms": int(bathrooms),
            "Floor_Number": int(floor_number),
            "Total_Floors": int(total_floors),
            "Age_of_Property": float(age),
            "Distance_to_Metro_km": float(dist_metro),
            "Distance_to_City_Center_km": float(dist_center),
            "Parking": int(parking),
            "Lift_Available": int(lift),
            "Gated_Community": int(gated),
            "Locality_Type": loc_type,
            "Property_Type": prop_type,
            "Furnishing_Status": furnishing,
        }


prediction_service = PredictionService()
