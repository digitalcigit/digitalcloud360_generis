"""Pytest configuration and fixtures for Genesis AI Service tests"""

import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
# Override the database URL for testing before importing other modules
settings.DATABASE_URL = "sqlite+aiosqlite:///./test.db"

from app.main import app
from app.config.database import Base, get_db, engine

# Create test session factory
TestingSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()

@pytest.fixture
async def authenticated_client(client: TestClient, db_session: AsyncSession) -> TestClient:
    """Create an authenticated test client with mock user."""
    # Override dependency to provide test database session
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Mock authentication for tests
    def mock_auth():
        return {"user_id": 1, "email": "test@example.com"}
    
    # Override auth dependencies here when implemented
    
    yield client
    
    # Clean up overrides
    app.dependency_overrides.clear()

@pytest.fixture
def mock_user_data():
    """Mock user data for testing."""
    return {
        "user_id": 1,
        "email": "entrepreneur@example.com",
        "name": "Test Entrepreneur",
        "business_sector": "restaurant",
        "language": "fr",
        "location": "Dakar, Sénégal"
    }

@pytest.fixture
def mock_coaching_session():
    """Mock coaching session data for testing."""
    return {
        "session_id": "test-session-123",
        "user_id": 1,
        "current_step": "vision",
        "status": "in_progress",
        "conversation_history": [
            {
                "role": "assistant",
                "content": "Bonjour ! Je suis Genesis, votre coach IA personnel..."
            }
        ]
    }

@pytest.fixture
def mock_business_brief():
    """Mock business brief data for testing."""
    return {
        "brief_id": "brief-123",
        "user_id": 1,
        "session_id": "test-session-123",
        "vision": "Créer le meilleur restaurant de cuisine sénégalaise à Dakar",
        "mission": "Offrir une expérience culinaire authentique et moderne",
        "target_audience": "Jeunes professionnels et familles sénégalaises",
        "differentiation": "Fusion tradition-modernité avec service rapide",
        "offer": "Plats traditionnels revisités, livraison 30min"
    }
