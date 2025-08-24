"""Pytest configuration for the Genesis AI Service tests - Multi-environment profile."""

# Import du gestionnaire de profils multi-environnements
# Sélectionne automatiquement conftest_local.py ou conftest_docker.py
# selon l'environnement détecté (local vs Docker)

from tests.conftest_profile import *

# Les fixtures sont automatiquement importées selon le profil:
# - LOCAL: conftest_local.py (PostgreSQL localhost:5433)
# - DOCKER: conftest_docker.py (PostgreSQL test-db:5432)

# Pour forcer un profil spécifique, utiliser:
# export TEST_PROFILE=local  # ou docker
# pytest tests/

# Informations sur le profil actuel disponibles via TEST_PROFILE_INFO

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

# Force test database URL - PostgreSQL Docker
# Utilise localhost:5433 quand on exécute depuis l'hôte, test-db:5432 depuis le conteneur
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"  # localhost:5433 pour tests locaux
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_engine():
    """Create a test SQLAlchemy engine using SQLite."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope for each test function."""
    TestingSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
        expire_on_commit=False
    )
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession, test_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create a new httpx.AsyncClient for testing the FastAPI app."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        # Simple client configuration for tests
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
def test_password() -> str:
    return "testpassword"



@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession, test_password: str) -> User:
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash(test_password),
        name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient, test_user: User, test_password: str) -> dict:
    """Fixture to get authentication headers for a test user."""
    login_data = {
        "username": test_user.email,
        "password": test_password
    }
    response = await client.post("/api/v1/auth/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
