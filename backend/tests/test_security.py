"""
PriceNest — API Security, Error Handling & Secret Zero Tests
"""

from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
import jwt

from backend.app.core.config import settings
from backend.app.core.security import create_access_token


@pytest.mark.asyncio
async def test_tampered_jwt_token_rejected(client: AsyncClient):
    token = create_access_token(subject="some-user-id")
    tampered_token = token[:-5] + "aaaaa"
    headers = {"Authorization": f"Bearer {tampered_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_expired_jwt_token_rejected(client: AsyncClient):
    past_time = datetime.now(timezone.utc) - timedelta(hours=2)
    payload = {
        "sub": "user-123",
        "iat": int((past_time - timedelta(hours=1)).timestamp()),
        "exp": int(past_time.timestamp()),
        "iss": "pricenest-auth",
    }
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    headers = {"Authorization": f"Bearer {expired_token}"}

    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    assert "expired" in response.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_sql_injection_attempt_in_locality_search(client: AsyncClient):
    malicious_query = "' OR '1'='1"
    response = await client.get(f"/api/v1/localities?query={malicious_query}")
    assert response.status_code == 200
    # Parameterized query should safely search for literal string and return 0 matches
    assert response.json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_no_stack_trace_in_error_responses(client: AsyncClient):
    response = await client.get("/api/v1/history/non-existent-uuid-12345")
    assert response.status_code in [401, 404]
    text = response.text
    assert "Traceback" not in text
    assert "File \"" not in text
    assert "line " not in text.lower()
