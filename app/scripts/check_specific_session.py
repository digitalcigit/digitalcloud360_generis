import redis.asyncio as redis
import asyncio
import json

async def check_session():
    client = redis.from_url("redis://redis:6379/0", decode_responses=True)
    session_id = "9dbd044e-d23c-4c0f-ad89-8f323077bc25"
    
    val = await client.get(f"session:{session_id}")
    if val:
        print(f"SESSION_DATA: {val}")
    else:
        print(f"SESSION {session_id} NOT FOUND")
        
    site_val = await client.get(f"site:{session_id}")
    if site_val:
        print(f"SITE_DATA_EXISTS: True")
    else:
        print(f"SITE_DATA_NOT_FOUND")

if __name__ == "__main__":
    asyncio.run(check_session())
