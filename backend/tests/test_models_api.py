"""
PriceNest — Model Registry & Governance Endpoint Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_active_model_metadata(client: AsyncClient):
    response = await client.get("/api/v1/models/active")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]

    assert data["version"] == "v1.0.0"
    assert data["algorithm"] == "HistGradientBoostingRegressor"
    assert "offline_metrics" in data
    assert "r2_score" in data["offline_metrics"]
    assert "mae_inr_lakhs" in data["offline_metrics"]
    assert "features_used" in data
    assert len(data["features_used"]) == 14
