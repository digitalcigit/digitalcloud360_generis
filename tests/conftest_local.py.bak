"""Pytest configuration for LOCAL environment testing."""

import os
import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from asgi_lifespan import LifespanManager

from app.main import app
from app.config.settings import settings, Settings
from app.config.database import get_db
from app.models.base import Base
from app.models.user import User
from app.core.security import get_password_hash

# Configuration pour environnement LOCAL
# PostgreSQL Docker accessible depuis l'hôte via localhost:5433
TEST_DATABASE_URL_LOCAL = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_engine_local():
    """Create a test SQLAlchemy engine using PostgreSQL LOCAL."""
    engine = create_async_engine(TEST_DATABASE_URL_LOCAL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session_local(test_engine_local) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope for each test function - LOCAL."""
    TestingSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine_local,
        expire_on_commit=False
    )
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def client_local(db_session_local: AsyncSession, test_engine_local) -> AsyncGenerator[AsyncClient, None]:
    """Create a new httpx.AsyncClient for testing in LOCAL environment."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session_local

    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        # Client configuration optimisée pour environnement local
        transport = ASGITransport(app=app)
        client_config = {
            "transport": transport,
            "base_url": "http://testserver"
        }
        async with AsyncClient(**client_config) as async_client:
            yield async_client
    finally:
        # Clean up overrides
        app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_password_local() -> str:
    return "testpassword"

@pytest.fixture(scope="function")
async def test_user_local(db_session_local: AsyncSession, test_password_local: str) -> User:
    """Create a test user in the database - LOCAL."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash(test_password_local),
        name="Test User Local",
    )
    db_session_local.add(user)
    await db_session_local.commit()
    await db_session_local.refresh(user)
    return user

@pytest.fixture(scope="function")
async def auth_headers_local(client_local: AsyncClient, test_user_local: User, test_password_local: str) -> dict:
    """Fixture to get authentication headers for a test user - LOCAL."""
    login_data = {
        "username": test_user_local.email,
        "password": test_password_local
    }
    response = await client_local.post("/api/v1/auth/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Configuration d'environnement pour LOCAL
@pytest.fixture(scope="session")
def test_env_local():
    """Configure environment variables for LOCAL testing."""
    original_env = os.environ.copy()
    
    # Configuration spécifique LOCAL
    os.environ.update({
        "TESTING_MODE": "true",
        "ENVIRONMENT": "testing_local",
        "TEST_DATABASE_URL": TEST_DATABASE_URL_LOCAL,
        "REDIS_URL": "redis://localhost:6382/0",
        "DIGITALCLOUD360_API_URL": "https://api-dev.digitalcloud360.com",
        "STRICT_HEALTH_CHECKS": "false",
        "VALIDATE_EXTERNAL_APIS": "false"
    })
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)