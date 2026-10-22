"""
PriceNest — Property Price Prediction API Endpoint Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_predict_price_valid_payload(client: AsyncClient):
    payload = {
        "locality_name": "Baner",
        "total_sqft": 1050.0,
        "bhk": 2.0,
        "bathrooms": 2,
        "balconies": 1,
        "property_type": "Apartment",
        "furnishing": "semi_furnished",
    }
    response = await client.post("/api/v1/predict/price", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "data" in body
    data = body["data"]

    assert "prediction_id" in data
    assert data["predicted_price_inr"] > 0
    assert "formatted_price" in data
    assert "price_range" in data
    assert "min_inr" in data["price_range"]
    assert "max_inr" in data["price_range"]
    assert data["per_sqft_rate_inr"] > 0
    assert "model_metadata" in data
    assert data["model_metadata"]["algorithm"] == "HistGradientBoostingRegressor"
    assert "disclaimer" in data
    assert "exploratory dataset" in data["disclaimer"]


@pytest.mark.asyncio
async def test_predict_price_alias_endpoint(client: AsyncClient):
    payload = {
        "locality_name": "Wakad",
        "total_sqft": 850.0,
        "bhk": 2.0,
        "bathrooms": 2,
    }
    response = await client.post("/api/v1/predictions", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_predict_price_rejects_area_below_minimum(client: AsyncClient):
    payload = {
        "locality_name": "Baner",
        "total_sqft": 150.0,  # Below 200 sq.ft. minimum threshold
        "bhk": 1.0,
        "bathrooms": 1,
    }
    response = await client.post("/api/v1/predict/price", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_predict_price_rejects_non_physical_bhk_area(client: AsyncClient):
    payload = {
        "locality_name": "Kothrud",
        "total_sqft": 350.0,  # 350 sqft is non-physical for 4 BHK (fails total_sqft >= bhk * 150)
        "bhk": 4.0,
        "bathrooms": 3,
    }
    response = await client.post("/api/v1/predict/price", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert any("non-physical" in d["issue"] for d in body["error"]["details"])


@pytest.mark.asyncio
async def test_predict_price_rejects_floor_exceeding_total(client: AsyncClient):
    payload = {
        "locality_name": "Hinjewadi",
        "total_sqft": 900.0,
        "bhk": 2.0,
        "bathrooms": 2,
        "floor_number": 15,
        "total_floors": 10,  # Floor 15 in 10-floor building
    }
    response = await client.post("/api/v1/predict/price", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert any("Floor number" in d["issue"] for d in body["error"]["details"])


@pytest.mark.asyncio
async def test_predict_price_with_authenticated_user(client: AsyncClient, test_user_a: dict):
    payload = {
        "locality_name": "Baner",
        "total_sqft": 1100.0,
        "bhk": 2.0,
        "bathrooms": 2,
    }
    headers = {"Authorization": f"Bearer {test_user_a['token']}"}
    response = await client.post("/api/v1/predict/price", json=payload, headers=headers)
    assert response.status_code == 200

    pred_id = response.json()["data"]["prediction_id"]

    # Verify prediction now appears in user A's private history
    history_resp = await client.get("/api/v1/history", headers=headers)
    assert history_resp.status_code == 200
    items = history_resp.json()["data"]["items"]
    assert any(item["prediction_id"] == pred_id for item in items)
