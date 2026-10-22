"""
PriceNest — Application Configuration Management
Pydantic v2 BaseSettings loading from environment variables.
"""

from pathlib import Path
from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core Application Metadata
    APP_NAME: str = "PriceNest-Backend"
    APP_ENV: str = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_STR: str = "/api/v1"

    # CORS Whitelist
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./pricenest_dev.db",
        description="Async SQLAlchemy database connection URL (asyncpg or aiosqlite)",
    )
    SYNC_DATABASE_URL: str = Field(
        default="sqlite:///./pricenest_dev.db",
        description="Synchronous database connection URL for Alembic migrations",
    )
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 1800

    # Machine Learning Model Configuration
    MODEL_ARTIFACTS_DIR: str = Field(
        default="ml/models",
        description="Directory containing serialized joblib artifacts",
    )
    ACTIVE_MODEL_VERSION: str = "v1.0.0"
    ACTIVE_MODEL_FILENAME: str = "pricenest_pune_model_v1.0.0_exp.joblib"

    # Security & Authentication
    SECRET_KEY: str = Field(
        default="pricenest-dev-insecure-secret-key-32-chars-minimum-replace-in-prod",
        description="Cryptographic secret key for signing JWT tokens",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    @property
    def resolved_model_path(self) -> Path:
        """Resolve the absolute path to the active machine learning model artifact."""
        # 1. Check relative to current working directory
        direct_path = Path(self.MODEL_ARTIFACTS_DIR) / self.ACTIVE_MODEL_FILENAME
        if direct_path.exists():
            return direct_path.resolve()

        # 2. Check relative to repo root (looking up from backend)
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        root_path = repo_root / "ml" / "models" / self.ACTIVE_MODEL_FILENAME
        if root_path.exists():
            return root_path.resolve()

        # 3. Fallback to direct path
        return direct_path.resolve()


settings = Settings()
