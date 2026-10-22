"""
PriceNest — Machine Learning Service & Model Pipeline Tests
"""

import pytest
from backend.app.services.ml_service import ml_service


def test_ml_service_is_ready():
    assert ml_service.is_ready() is True
    assert ml_service.algorithm == "HistGradientBoostingRegressor"
    assert ml_service.model_version == "v1.0.0"


def test_ml_service_prediction_output_structure():
    inputs = {
        "total_sqft": 1050.0,
        "bhk": 2.0,
        "bathrooms": 2,
        "locality_name": "Baner",
        "property_type": "Apartment",
        "furnishing": "semi_furnished",
    }
    result = ml_service.predict_price(inputs)

    assert "predicted_price_inr" in result
    assert result["predicted_price_inr"] > 0
    assert "predicted_price_lakhs" in result
    assert result["predicted_price_lakhs"] > 0

    # Verify relationship between INR and Lakhs
    assert abs((result["predicted_price_inr"] / 100_000.0) - result["predicted_price_lakhs"]) < 0.01

    # Verify price range bounds
    price_range = result["price_range"]
    assert price_range["min_inr"] <= result["predicted_price_inr"]
    assert price_range["max_inr"] >= result["predicted_price_inr"]
    assert "formatted_range" in price_range

    # Verify per sqft rate
    expected_rate = round(result["predicted_price_inr"] / 1050.0, 2)
    assert abs(result["per_sqft_rate_inr"] - expected_rate) < 1.0

    # Verify disclaimer is present
    assert "disclaimer" in result
    assert "exploratory dataset" in result["disclaimer"]


def test_ml_service_deterministic_inference():
    """Verify that identical inputs produce identical predictions (reproducibility)."""
    inputs = {
        "total_sqft": 1200.0,
        "bhk": 3.0,
        "bathrooms": 3,
        "locality_name": "Kothrud",
    }
    pred_1 = ml_service.predict_price(inputs)
    pred_2 = ml_service.predict_price(inputs)

    assert pred_1["predicted_price_inr"] == pred_2["predicted_price_inr"]
    assert pred_1["price_range"] == pred_2["price_range"]


def test_ml_service_currency_formatting():
    # Test sub-crore formatting
    fmt_lakh, _ = ml_service._format_currency(75.50, 6000.0)
    assert fmt_lakh == "₹75.50 Lakh"

    # Test crore formatting
    fmt_cr, _ = ml_service._format_currency(185.20, 12000.0)
    assert fmt_cr == "₹1.85 Cr"
