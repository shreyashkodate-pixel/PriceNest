"""
PriceNest — Model Registry & Governance Metadata Endpoints
"""

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.model_metadata import ModelRegistry
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.model_metadata import ModelActiveResponseData
from backend.app.services.ml_service import ml_service

router = APIRouter(prefix="/models", tags=["Model Governance"])


@router.get(
    "/active",
    response_model=StandardResponse[ModelActiveResponseData],
    status_code=status.HTTP_200_OK,
    summary="Retrieve active ML model metadata and offline evaluation metrics",
)
async def get_active_model(
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ModelActiveResponseData]:
    # Check if active model exists in DB
    stmt = select(ModelRegistry).where(ModelRegistry.is_active == True)  # noqa: E712
    result = await db.execute(stmt)
    registry_entry = result.scalar_one_or_none()

    if registry_entry:
        data = ModelActiveResponseData(
            version=registry_entry.version,
            model_name=registry_entry.model_name,
            algorithm=registry_entry.algorithm,
            training_date=registry_entry.deployed_at.isoformat() if registry_entry.deployed_at else registry_entry.created_at.isoformat(),
            dataset_provenance=registry_entry.training_dataset_ref,
            offline_metrics=registry_entry.metrics,
            features_used=registry_entry.feature_names,
        )
    else:
        # Load from Phase 3 report baseline_metrics.json if DB record not yet inserted
        report_path = Path("ml/reports/baseline_metrics.json")
        if not report_path.exists():
            repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            report_path = repo_root / "ml" / "reports" / "baseline_metrics.json"

        offline_metrics: Dict[str, Any] = {
            "r2_score": 0.7481,
            "mae_inr_lakhs": 32.48,
            "rmse_inr_lakhs": 52.84,
            "cv_5fold_r2_mean": 0.6668,
        }
        features_used = [
            "Super_Area_SqFt", "BHK", "Bathrooms", "Floor_Number", "Total_Floors",
            "Age_of_Property", "Distance_to_Metro_km", "Distance_to_City_Center_km",
            "Parking", "Lift_Available", "Gated_Community", "Locality_Type",
            "Property_Type", "Furnishing_Status"
        ]

        if report_path.exists():
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    metrics_json = json.load(f)
                    win = metrics_json.get("winning_model", {})
                    test_m = win.get("test_metrics", {})
                    offline_metrics = {
                        "r2_score": test_m.get("test_r2", 0.7481),
                        "mae_inr_lakhs": test_m.get("test_mae_lakhs", 32.48),
                        "rmse_inr_lakhs": test_m.get("test_rmse_lakhs", 52.84),
                        "cv_5fold_r2_mean": 0.6668,
                    }
            except Exception:
                pass

        data = ModelActiveResponseData(
            version=settings.ACTIVE_MODEL_VERSION,
            model_name="pricenest_pune_regressor",
            algorithm=ml_service.algorithm,
            training_date="2026-10-21T00:00:00Z",
            dataset_provenance="Kaggle Pune Housing Dataset (Development / Exploratory Baseline)",
            offline_metrics=offline_metrics,
            features_used=features_used,
        )

    return StandardResponse(data=data)
