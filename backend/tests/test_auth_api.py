"""
PriceNest — User Authentication & Account Security Tests
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User


@pytest.mark.asyncio
async def test_user_registration_success(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "email": "unique_user@example.com",
        "password": "StrongPassword123!",
        "full_name": "Radhika Sharma",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "unique_user@example.com"
    assert body["data"]["full_name"] == "Radhika Sharma"

    # Verify password was hashed and not saved in plaintext
    stmt = select(User).where(User.email == "unique_user@example.com")
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.hashed_password != "StrongPassword123!"
    assert user.hashed_password.startswith("$2b$") or user.hashed_password.startswith("$2a$")


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(client: AsyncClient):
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
    }
    resp1 = await client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 409
    body = resp2.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_CONFLICT"


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient):
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login_test@example.com", "password": "MySecretPassword123!"},
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login_test@example.com", "password": "MySecretPassword123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["expires_in"] == 86400


@pytest.mark.asyncio
async def test_user_login_invalid_credentials(client: AsyncClient):
    # Invalid password
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login_test@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"

    # Non-existent email
    response_unknown = await client.post(
        "/api/v1/auth/login",
        json={"email": "non_existent@example.com", "password": "AnyPassword123!"},
    )
    assert response_unknown.status_code == 401


@pytest.mark.asyncio
async def test_auth_me_profile_access(client: AsyncClient, test_user_a: dict):
    headers = {"Authorization": f"Bearer {test_user_a['token']}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["email"] == test_user_a["email"]
    assert body["data"]["user_id"] == test_user_a["user_id"]


@pytest.mark.asyncio
async def test_auth_me_rejects_missing_or_invalid_token(client: AsyncClient):
    # Missing token
    resp_missing = await client.get("/api/v1/auth/me")
    assert resp_missing.status_code == 401

    # Malformed token
    resp_malformed = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )
    assert resp_malformed.status_code == 401
