import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def test_connection():
    """Tests the connection to the PostgreSQL database."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in environment variables.")
        return

    print(f"Attempting to connect to the database at {db_url}...")

    try:
        engine = create_async_engine(db_url)
        async with engine.connect() as connection:
            print("Successfully connected to the database.")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())