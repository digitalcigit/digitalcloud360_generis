"""Tests for Semantic Memory System"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.memory.vector_store import VectorStore
from app.models.embedding import UserEmbedding
from app.models.user import User

@pytest.fixture
def mock_openai():
    with patch("app.core.memory.vector_store.AsyncOpenAI") as mock:
        client = AsyncMock()
        mock.return_value = client
        
        # Mock embeddings.create response
        response = MagicMock()
        response.data = [MagicMock(embedding=[0.1] * 1536)]
        client.embeddings.create.return_value = response
        
        yield client

@pytest.fixture
def vector_store(mock_openai):
    return VectorStore()

@pytest.mark.asyncio
async def test_embed_text(vector_store):
    """Test text embedding generation"""
    embedding = await vector_store.embed_text("test text")
    
    assert len(embedding) == 1536
    assert embedding[0] == 0.1
    vector_store.openai.embeddings.create.assert_called_once()

@pytest.mark.asyncio
async def test_store_embedding(vector_store, db_session: AsyncSession):
    """Test storing embedding in database"""
    # Create test user
    user = User(
        email="test@memory.com",
        name="Test User",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Store embedding
    embedding = await vector_store.store_embedding(
        db=db_session,
        user_id=user.id,
        brief_id="brief_123",
        text="This is a test brief",
        embedding_type="brief",
        metadata={"sector": "tech"}
    )
    
    assert embedding.id is not None
    assert embedding.user_id == user.id
    assert embedding.brief_id == "brief_123"
    assert embedding.embedding_type == "brief"
    assert len(embedding.embedding) == 1536

@pytest.mark.asyncio
async def test_search_similar(vector_store, db_session: AsyncSession):
    """Test similarity search"""
    # Create test user
    user = User(
        email="search@memory.com",
        name="Search User",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Store some embeddings
    await vector_store.store_embedding(
        db=db_session,
        user_id=user.id,
        brief_id="brief_1",
        text="Restaurant italian pizza",
        embedding_type="brief"
    )
    
    await vector_store.store_embedding(
        db=db_session,
        user_id=user.id,
        brief_id="brief_2",
        text="Tech startup ai",
        embedding_type="brief"
    )
    
    # Mock search response (since we can't do real semantic search with mock embeddings)
    # The actual search relies on pgvector in the DB
    
    results = await vector_store.search_similar(
        db=db_session,
        query_text="pizza place",
        user_id=user.id,
        limit=5
    )
    
    # In a real vector DB with real embeddings, "pizza place" would be closer to "Restaurant italian pizza"
    # With mock embeddings (all 0.1), distance is 0, so they are identical.
    assert len(results) >= 2
    assert results[0]["user_id"] == user.id

@pytest.mark.asyncio
async def test_delete_user_embeddings(vector_store, db_session: AsyncSession):
    """Test deleting user embeddings"""
    # Create test user
    user = User(
        email="delete@memory.com",
        name="Delete User",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Store embedding
    await vector_store.store_embedding(
        db=db_session,
        user_id=user.id,
        brief_id="brief_1",
        text="To be deleted",
        embedding_type="brief"
    )
    
    # Delete
    count = await vector_store.delete_user_embeddings(db_session, user.id)
    assert count == 1
    
    # Verify empty
    results = await vector_store.search_similar(
        db=db_session,
        query_text="anything",
        user_id=user.id
    )
    assert len(results) == 0
