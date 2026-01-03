import redis.asyncio as redis
import asyncio
import json

async def verify_site_ownership():
    client = redis.from_url("redis://redis:6379/0", decode_responses=True)
    session_id = "a9fa5f04-8143-4521-aefd-27be89e02872"
    
    # Check session data
    session_json = await client.get(f"session:{session_id}")
    if session_json:
        session_data = json.loads(session_json)
        print(f"SESSION_USER_ID: {session_data.get('user_id')} (Type: {type(session_data.get('user_id'))})")
    else:
        print("SESSION_NOT_FOUND")
        
    # Check site data
    site_json = await client.get(f"site:{session_id}")
    if site_json:
        print("SITE_DATA_FOUND: True")
    else:
        print("SITE_DATA_NOT_FOUND")

if __name__ == "__main__":
    asyncio.run(verify_site_ownership())
