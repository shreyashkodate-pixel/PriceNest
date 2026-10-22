"""
PriceNest — ML Decoupled Subsystem Tests
Validates ml.common, ml.pipeline, and ml.inference modules directly.
"""

from ml.common.constants import ALL_FEATURES, CATEGORICAL_FEATURES, NUMERIC_FEATURES
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
from ml.inference.services.prediction_service import prediction_service
from ml.pipeline.pipeline import build_pipeline, build_preprocessor


def test_constants_and_schemas():
    assert len(NUMERIC_FEATURES) == 11
    assert len(CATEGORICAL_FEATURES) == 3
    assert len(ALL_FEATURES) == 14
    assert ALL_FEATURES == NUMERIC_FEATURES + CATEGORICAL_FEATURES


def test_utils_formatting():
    assert convert_lakhs_to_inr(50.0) == 5000000.0
    assert format_inr_price(45.5) == "₹45.50 Lakh"
    assert format_inr_price(150.0) == "₹1.50 Cr"
    assert format_per_sqft(8000.0) == "₹8,000 / sq.ft."


def test_utils_normalizations():
    assert normalize_locality_tier("Baner") == "Premium"
    assert normalize_locality_tier("Wagholi") == "Affordable"
    assert normalize_locality_tier("RandomPlace") == "Mid-Range"

    assert normalize_property_type("villa") == "Villa"
    assert normalize_property_type("apartment") == "Apartment"
    assert normalize_property_type("house") == "Independent House"

    assert normalize_furnishing("furnished") == "Furnished"
    assert normalize_furnishing("unfurnished") == "Unfurnished"
    assert normalize_furnishing("semi_furnished") == "Semi-Furnished"


def test_utils_calculate_price_range():
    min_inr, max_inr, fmt_range = calculate_price_range(75.0)
    assert min_inr < 7500000.0 < max_inr
    assert "–" in fmt_range


def test_pipeline_builders():
    preprocessor = build_preprocessor()
    assert preprocessor is not None

    pipeline = build_pipeline()
    assert "preprocessor" in pipeline.named_steps
    assert "regressor" in pipeline.named_steps


def test_decoupled_prediction_service():
    assert model_loader.is_loaded() is True

    result = prediction_service.predict_price({
        "locality_name": "Baner",
        "total_sqft": 1050.0,
        "bhk": 2.0,
        "bathrooms": 2,
    })

    assert result["predicted_price_inr"] > 0
    assert "₹" in result["formatted_price"]
    assert "price_range" in result
    assert "exploratory dataset" in result["disclaimer"]
