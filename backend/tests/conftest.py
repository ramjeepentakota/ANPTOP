"""
ANPTOP Backend - Pytest Configuration
"""

import pytest
import asyncio
import sys
import os
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

# Set test database URL before any imports
os.environ["TEST_DB_URL"] = "sqlite+aiosqlite:///:memory:"

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path setup and env vars
from main import app
from app.db.session import get_db
from app.db.base import Base
from app.core.security import get_current_user
from app.models.user import User


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# Create test engine with SQLite
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

test_session_factory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture
async def db_session():
    """Create a test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with test_session_factory() as session:
        yield session
        await session.rollback()
    
    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    return User(
        id=1,
        email="test@anptop.com",
        username="testuser",
        hashed_password="test_hash",
        role=User.Role.TESTER,
        is_active=True,
    )


@pytest.fixture
async def admin_user(db_session):
    """Create an admin test user."""
    return User(
        id=2,
        email="admin@anptop.com",
        username="admin",
        hashed_password="admin_hash",
        role=User.Role.ADMIN,
        is_active=True,
    )


@pytest.fixture
async def auth_headers(test_user):
    """Create authentication headers for test user."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_auth_headers(admin_user):
    """Create authentication headers for admin user."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}
