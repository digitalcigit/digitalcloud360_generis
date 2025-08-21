import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

from sqlalchemy import text

@pytest.mark.asyncio
async def test_database_connection():
    """
    Tests the basic connectivity to the test database.
    """
    test_db_url = os.getenv("TEST_DATABASE_URL")
    assert test_db_url, "TEST_DATABASE_URL environment variable not set"

    engine = create_async_engine(test_db_url, echo=True)
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        assert True
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")