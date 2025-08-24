"""Pytest configuration for DOCKER environment testing."""

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

# Configuration pour environnement DOCKER
# PostgreSQL accessible depuis le conteneur via test-db:5432
TEST_DATABASE_URL_DOCKER = "postgresql+asyncpg://test_user:test_password@test-db:5432/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_engine_docker():
    """Create a test SQLAlchemy engine using PostgreSQL DOCKER."""
    engine = create_async_engine(TEST_DATABASE_URL_DOCKER, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session_docker(test_engine_docker) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope for each test function - DOCKER."""
    TestingSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine_docker,
        expire_on_commit=False
    )
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def client_docker(db_session_docker: AsyncSession, test_engine_docker) -> AsyncGenerator[AsyncClient, None]:
    """Create a new httpx.AsyncClient for testing in DOCKER environment."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session_docker

    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        # Client configuration optimisée pour environnement Docker
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
def test_password_docker() -> str:
    return "testpassword"

@pytest.fixture(scope="function")
async def test_user_docker(db_session_docker: AsyncSession, test_password_docker: str) -> User:
    """Create a test user in the database - DOCKER."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash(test_password_docker),
        name="Test User Docker",
    )
    db_session_docker.add(user)
    await db_session_docker.commit()
    await db_session_docker.refresh(user)
    return user

@pytest.fixture(scope="function")
async def auth_headers_docker(client_docker: AsyncClient, test_user_docker: User, test_password_docker: str) -> dict:
    """Fixture to get authentication headers for a test user - DOCKER."""
    login_data = {
        "username": test_user_docker.email,
        "password": test_password_docker
    }
    response = await client_docker.post("/api/v1/auth/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Configuration d'environnement pour DOCKER
@pytest.fixture(scope="session")
def test_env_docker():
    """Configure environment variables for DOCKER testing."""
    original_env = os.environ.copy()
    
    # Configuration spécifique DOCKER
    os.environ.update({
        "TESTING_MODE": "true",
        "ENVIRONMENT": "testing_docker",
        "TEST_DATABASE_URL": TEST_DATABASE_URL_DOCKER,
        "DATABASE_URL": "postgresql+asyncpg://genesis_user:your_secure_password_here@postgres:5432/genesis_db",
        "REDIS_URL": "redis://redis:6379/0",
        "DIGITALCLOUD360_API_URL": "https://api-dev.digitalcloud360.com",
        "STRICT_HEALTH_CHECKS": "false",
        "VALIDATE_EXTERNAL_APIS": "false"
    })
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)