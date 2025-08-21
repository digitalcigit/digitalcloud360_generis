"""Pytest configuration for the Genesis AI Service tests."""

import os
import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from asgi_lifespan import LifespanManager

from app.main import app
from app.config.settings import settings, Settings
from app.config.database import get_db, Base
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create a new SQLAlchemy engine for the test session."""
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable not set for testing")
    return create_async_engine(test_db_url, echo=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_database(engine):
    """Set up the test database, creating and dropping tables for the session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope for each test function."""
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a new httpx.AsyncClient for testing the FastAPI app."""

    def get_settings_override() -> Settings:
        return Settings(
            TESTING_MODE=True, 
            DATABASE_URL=os.getenv("TEST_DATABASE_URL"),
            ENVIRONMENT="testing"
        )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[Settings] = get_settings_override

    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
            yield async_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
