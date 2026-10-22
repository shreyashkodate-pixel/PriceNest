"""
PriceNest — Private History Isolation & Ownership Security Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_history_isolation(
    client: AsyncClient, test_user_a: dict, test_user_b: dict
):
    headers_a = {"Authorization": f"Bearer {test_user_a['token']}"}
    headers_b = {"Authorization": f"Bearer {test_user_b['token']}"}

    # 1. User A creates a prediction
    pred_payload = {
        "locality_name": "Baner",
        "total_sqft": 1050.0,
        "bhk": 2.0,
        "bathrooms": 2,
    }
    pred_resp = await client.post(
        "/api/v1/predict/price",
        json=pred_payload,
        headers=headers_a,
    )
    assert pred_resp.status_code == 200
    pred_id_a = pred_resp.json()["data"]["prediction_id"]

    # 2. User A retrieves history: must contain prediction A
    hist_a = await client.get("/api/v1/history", headers=headers_a)
    assert hist_a.status_code == 200
    items_a = hist_a.json()["data"]["items"]
    assert any(i["prediction_id"] == pred_id_a for i in items_a)

    # 3. User B retrieves history: must NOT contain prediction A
    hist_b = await client.get("/api/v1/history", headers=headers_b)
    assert hist_b.status_code == 200
    items_b = hist_b.json()["data"]["items"]
    assert not any(i["prediction_id"] == pred_id_a for i in items_b)

    # 4. User B attempts direct retrieval of User A's prediction ID: must receive 404 (ID enumeration protection)
    direct_resp = await client.get(
        f"/api/v1/history/{pred_id_a}",
        headers=headers_b,
    )
    assert direct_resp.status_code == 404
    assert direct_resp.json()["error"]["code"] == "NOT_FOUND"

    # 5. User A retrieves their own prediction detail: must receive 200
    own_detail = await client.get(
        f"/api/v1/history/{pred_id_a}",
        headers=headers_a,
    )
    assert own_detail.status_code == 200
    assert own_detail.json()["data"]["prediction_id"] == pred_id_a


@pytest.mark.asyncio
async def test_history_unauthenticated_access_rejected(client: AsyncClient):
    response = await client.get("/api/v1/history")
    assert response.status_code == 401
