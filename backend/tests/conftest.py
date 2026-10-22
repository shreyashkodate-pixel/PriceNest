"""
PriceNest — Pytest Test Configuration & Async Fixtures
Configures an isolated in-memory/file async SQLite database and ASGI test client.
"""

import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure repo root and backend root are on sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
backend_dir = repo_root / "backend"
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Configure test environment variables before importing app
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "False"
TEST_DB_PATH = Path("./test_pricenest_suite.db").resolve()
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ["SYNC_DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["SECRET_KEY"] = "test-secret-key-for-pricenest-backend-testing-purposes-only"

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.main import app
from backend.app.models.base import Base
from backend.app.models.user import User
from backend.app.services.auth_service import auth_service
from backend.app.services.ml_service import ml_service

test_engine = create_async_engine(
    f"sqlite+aiosqlite:///{TEST_DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)
test_session_factory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_test_database():
    """Create all database tables for the test session and clean up after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Ensure model is loaded once for test suite
    ml_service.load_model()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated database session per test with automatic rollback/cleanup."""
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an asynchronous HTTP client configured against the FastAPI ASGI app."""
    async def override_get_db():
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user_a(client: AsyncClient) -> Dict[str, str]:
    """Register and authenticate test user A."""
    from uuid import uuid4
    email = f"user_a_{uuid4().hex[:8]}@example.com"
    password = "Password123!"
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "User Alpha"},
    )
    assert resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]
    user_id = resp.json()["data"]["user_id"]
    return {"email": email, "token": token, "user_id": user_id}


@pytest_asyncio.fixture
async def test_user_b(client: AsyncClient) -> Dict[str, str]:
    """Register and authenticate test user B for isolation testing."""
    from uuid import uuid4
    email = f"user_b_{uuid4().hex[:8]}@example.com"
    password = "Password123!"
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "User Beta"},
    )
    assert resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]
    user_id = resp.json()["data"]["user_id"]
    return {"email": email, "token": token, "user_id": user_id}

