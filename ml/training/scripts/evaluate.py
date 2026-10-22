"""
PriceNest — Model Evaluation & Subgroup Residuals Analysis Script
Evaluates fitted pipeline performance across price tiers and localities (SRS FR-07).
"""

import json
import logging
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from ml.common.constants import ALL_FEATURES, DEFAULT_MODEL_FILENAME, TARGET_COLUMN
from ml.training.scripts.train import load_and_clean_data

logger = logging.getLogger("pricenest.ml.evaluate")


def evaluate_model(data_path: Path, artifact_path: Path) -> dict:
    """Evaluate fitted model on test split and compute subgroup residuals."""
    if not artifact_path.exists():
        raise FileNotFoundError(f"Model artifact not found: {artifact_path}")

    pipeline = joblib.load(artifact_path)
    X, y = load_and_clean_data(data_path)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    y_pred = pipeline.predict(X_test)
    residuals = y_test - y_pred

    overall_mae = mean_absolute_error(y_test, y_pred)
    overall_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    overall_r2 = r2_score(y_test, y_pred)

    eval_df = X_test.copy()
    eval_df["actual"] = y_test
    eval_df["predicted"] = y_pred
    eval_df["residual"] = residuals
    eval_df["abs_error"] = np.abs(residuals)

    bins = [0, 50, 100, 200, float("inf")]
    labels = ["<50L (Budget)", "50L-100L (Mid)", "100L-200L (Premium)", ">200L (Luxury)"]
    eval_df["tier"] = pd.cut(eval_df["actual"], bins=bins, labels=labels)

    tier_analysis = {}
    for tier, grp in eval_df.groupby("tier", observed=False):
        if len(grp) > 0:
            tier_analysis[str(tier)] = {
                "count": len(grp),
                "mae": round(float(grp["abs_error"].mean()), 2),
                "rmse": round(float(np.sqrt(np.mean(grp["residual"] ** 2))), 2),
                "bias": round(float(grp["residual"].mean()), 2),
            }

    report = {
        "overall": {
            "r2": round(overall_r2, 4),
            "mae_lakhs": round(overall_mae, 2),
            "rmse_lakhs": round(overall_rmse, 2),
        },
        "price_tiers": tier_analysis,
    }
    return report


if __name__ == "__main__":
    data_file = repo_root / "data" / "raw" / "pune_housing_raw.csv"
    artifact_file = repo_root / "ml" / "inference" / "artifacts" / DEFAULT_MODEL_FILENAME
    res = evaluate_model(data_file, artifact_file)
    print(json.dumps(res, indent=2))
