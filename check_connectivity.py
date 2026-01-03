
import asyncio
import os
import socket
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from redis.asyncio import Redis

# Get env vars
DB_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://test_user:test_password@test-db:5432/test_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

print(f"Checking connectivity...")
print(f"DB_URL: {DB_URL}")
print(f"REDIS_URL: {REDIS_URL}")

async def check_db():
    try:
        engine = create_async_engine(DB_URL)
        async with engine.connect() as conn:
            await conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def check_redis():
    try:
        r = Redis.from_url(REDIS_URL)
        await r.ping()
        await r.close()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

async def main():
    db_ok = await check_db()
    redis_ok = await check_redis()
    
    if not (db_ok and redis_ok):
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
