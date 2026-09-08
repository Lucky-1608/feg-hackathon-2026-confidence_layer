"""Database connection management.

Provides async engine and session factory for PostgreSQL.
The database is used for persistence/audit, NOT for the critical decision path.
"""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from confidence.config import DatabaseConfig


def create_async_db_engine(config: DatabaseConfig) -> AsyncEngine:
    """Create an async SQLAlchemy engine for PostgreSQL."""
    return create_async_engine(
        config.url,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        echo=False,
    )


def create_sync_db_engine(config: DatabaseConfig) -> Engine:
    """Create a sync SQLAlchemy engine (for migrations and testing)."""
    return create_engine(config.url_sync, echo=False)


def create_async_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory."""
    return async_sessionmaker(engine, expire_on_commit=False)


def create_sync_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a sync session factory (for testing)."""
    return sessionmaker(bind=engine, expire_on_commit=False)
