"""
PriceNest — Alembic Environment Script
Configures migration runtime, connects to target database, and points to model metadata.
"""

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import all models to register them on Base.metadata
import backend.app.models  # noqa: F401
from backend.app.core.config import settings
from backend.app.models.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_database_url() -> str:
    """Resolve synchronous database connection URL for Alembic migrations."""
    raw_url = os.environ.get("SYNC_DATABASE_URL") or settings.SYNC_DATABASE_URL
    if not raw_url:
        raw_url = os.environ.get("DATABASE_URL") or settings.DATABASE_URL

    # Strip async drivers for Alembic's sync engine
    sync_url = raw_url.replace("postgresql+asyncpg://", "postgresql://")
    sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite://")
    return sync_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_sync_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_sync_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
