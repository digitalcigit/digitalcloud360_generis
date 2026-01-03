import asyncio
from app.config.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select
import json

async def debug_ownership():
    try:
        async with AsyncSessionLocal() as db:
            # 1. Get user ID for dcitest@digital.ci
            res = await db.execute(select(User).filter(User.email == 'dcitest@digital.ci'))
            u = res.scalars().first()
            if u:
                print(f"DB_USER_ID:{u.id}")
            else:
                print("DB_USER_NOT_FOUND")
                return

    except Exception as e:
        print(f"DB_ERROR:{e}")

if __name__ == "__main__":
    asyncio.run(debug_ownership())
