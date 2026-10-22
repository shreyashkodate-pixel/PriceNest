"""
PriceNest — Valuation Feedback Endpoint Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_submit_valuation_feedback_success(client: AsyncClient):
    # 1. Generate prediction
    pred_resp = await client.post(
        "/api/v1/predict/price",
        json={
            "locality_name": "Aundh",
            "total_sqft": 950.0,
            "bhk": 2.0,
            "bathrooms": 2,
        },
    )
    assert pred_resp.status_code == 200
    pred_id = pred_resp.json()["data"]["prediction_id"]

    # 2. Submit feedback
    feedback_payload = {
        "feedback_type": "accurate",
        "reported_actual_price_inr": 8500000.0,
        "comments": "Very close to recent transaction in building B.",
    }
    fb_resp = await client.post(
        f"/api/v1/valuations/{pred_id}/feedback",
        json=feedback_payload,
    )
    assert fb_resp.status_code == 201
    body = fb_resp.json()
    assert body["success"] is True
    assert body["data"]["prediction_id"] == pred_id
    assert body["data"]["status"] == "recorded"


@pytest.mark.asyncio
async def test_submit_feedback_non_existent_prediction(client: AsyncClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    fb_resp = await client.post(
        f"/api/v1/valuations/{fake_id}/feedback",
        json={"feedback_type": "too_high"},
    )
    assert fb_resp.status_code == 404
    assert fb_resp.json()["error"]["code"] == "NOT_FOUND"
