"""
PriceNest — ML Training Entrypoint (Training Subsystem)
Offline reproducible model training pipeline adhering to SRS FR-07.
"""

import json
import logging
import os
import sys
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent.parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from ml.common.constants import (
    ALL_FEATURES,
    DEFAULT_MODEL_FILENAME,
    MIN_SUPER_AREA_SQFT,
    TARGET_COLUMN,
)
from ml.pipeline.pipeline import build_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pricenest.ml.train")


def load_and_clean_data(csv_path: Path) -> tuple[pd.DataFrame, np.ndarray]:
    """Load raw dataset, filter to clean Pune records, and extract features and target."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Training dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path)
    # Filter strictly to Pune
    pune_df = df[df["City"] == "Pune"].copy()
    # Filter physical area anomalies
    clean_df = pune_df[pune_df["Super_Area_SqFt"] >= MIN_SUPER_AREA_SQFT].copy()

    X = clean_df[ALL_FEATURES]
    y = clean_df[TARGET_COLUMN].values
    logger.info(f"Loaded {len(clean_df):,} clean Pune records from {csv_path.name}")
    return X, y


def train_model(
    raw_data_path: Path,
    output_artifact_path: Path,
    report_json_path: Path,
) -> dict:
    """Execute reproducible training and export winning model artifact."""
    X, y = load_and_clean_data(raw_data_path)

    # 80/20 train/test split with random_state=42
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    pipeline = build_pipeline()
    logger.info("Fitting scikit-learn Pipeline (ColumnTransformer + HistGradientBoostingRegressor)...")
    pipeline.fit(X_train, y_train)

    # Holdout evaluation
    y_pred = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = r2_score(y_test, y_pred)

    logger.info(f"Holdout Test Results: R²={r2:.4f} | MAE=₹{mae:.2f}L | RMSE=₹{rmse:.2f}L")

    # Serialize to output destination
    output_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_artifact_path)
    logger.info(f"Exported artifact to: {output_artifact_path}")

    # Generate metrics report
    metrics = {
        "test_r2": round(r2, 4),
        "test_mae_lakhs": round(mae, 2),
        "test_rmse_lakhs": round(rmse, 2),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }
    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics}, f, indent=2)

    return metrics


if __name__ == "__main__":
    data_file = repo_root / "data" / "raw" / "pune_housing_raw.csv"
    artifact_file = repo_root / "ml" / "inference" / "artifacts" / DEFAULT_MODEL_FILENAME
    report_file = repo_root / "ml" / "reports" / "baseline_metrics.json"
    train_model(data_file, artifact_file, report_file)
