"""
PriceNest — Pune Localities API Endpoint Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_localities(client: AsyncClient):
    response = await client.get("/api/v1/localities")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["total"] > 0
    assert len(data["items"]) > 0

    first_item = data["items"][0]
    assert "name" in first_item
    assert "slug" in first_item
    assert "zone" in first_item
    assert "locality_type" in first_item


@pytest.mark.asyncio
async def test_search_localities_by_query(client: AsyncClient):
    response = await client.get("/api/v1/localities?query=Baner")
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) >= 1
    assert any(item["name"] == "Baner" for item in items)


@pytest.mark.asyncio
async def test_filter_localities_by_zone(client: AsyncClient):
    response = await client.get("/api/v1/localities?zone=West%20Pune")
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) > 0
    assert all(item["zone"] == "West Pune" for item in items)
