import redis.asyncio as redis
import asyncio
import json

async def check_redis():
    client = redis.from_url("redis://localhost:6382/0", decode_responses=True)
    session_id = "a9fa5f04-8143-4521-aefd-27be89e02872"
    
    val = await client.get(f"session:{session_id}")
    if val:
        print(f"SESSION_DATA: {val}")
    else:
        print("SESSION_NOT_FOUND")
        
    site_val = await client.get(f"site:{session_id}")
    if site_val:
        print(f"SITE_DATA_EXISTS: True")
    else:
        print("SITE_DATA_NOT_FOUND")

if __name__ == "__main__":
    asyncio.run(check_redis())
