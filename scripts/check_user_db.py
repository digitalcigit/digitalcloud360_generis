import asyncio
from app.config.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def check_user():
    try:
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(User).filter(User.email == 'dcitest@digital.ci'))
            u = res.scalars().first()
            if u:
                print(f"USER_EXISTS|{u.id}|{u.email}")
            else:
                print("USER_NOT_FOUND")
    except Exception as e:
        print(f"ERROR|{e}")

if __name__ == "__main__":
    asyncio.run(check_user())
