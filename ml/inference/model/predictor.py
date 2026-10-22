"""
PriceNest — Model Predictor (Inference Subsystem)
Executes in-process model inference and enforces finite physical boundaries.
"""

import time
from typing import Tuple

import pandas as pd

from ml.common.constants import ALL_FEATURES
from ml.inference.model.loader import model_loader


class Predictor:
    """Handles raw estimator execution on verified feature DataFrames."""

    def __init__(self, loader=model_loader):
        self.loader = loader

    def predict(self, feature_df: pd.DataFrame) -> Tuple[float, float]:
        """
        Execute prediction on prepared DataFrame.
        Returns tuple of (predicted_price_lakhs, latency_ms).
        """
        pipeline = self.loader.get_pipeline()

        # Validate column presence
        missing_cols = [c for c in ALL_FEATURES if c not in feature_df.columns]
        if missing_cols:
            raise ValueError(f"Input DataFrame is missing required features: {missing_cols}")

        start_time = time.perf_counter()
        raw_pred = pipeline.predict(feature_df)[0]
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        pred_lakhs = float(raw_pred)
        # Enforce non-negative physical floor
        pred_lakhs = max(1.0, pred_lakhs)

        return pred_lakhs, latency_ms


predictor = Predictor()
