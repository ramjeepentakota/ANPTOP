"""
ANPTOP Backend - Database Session Management
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.db.base import Base

# Get database URL
_database_url = settings.DATABASE_URL

# For testing, allow override via environment variable
import os
if os.environ.get("TEST_DB_URL"):
    _database_url = os.environ.get("TEST_DB_URL")

# Determine if using SQLite (doesn't support pool settings)
_is_sqlite = "sqlite" in _database_url

if _is_sqlite:
    # SQLite doesn't support pool_size and max_overflow
    engine = create_async_engine(
        _database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
else:
    # PostgreSQL supports pool settings
    engine = create_async_engine(
        _database_url,
        echo=settings.DEBUG,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
    )

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Drop all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_db_session() -> AsyncSession:
    """Get a database session directly."""
    async with async_session_factory() as session:
        return session
