import redis.asyncio as redis
import asyncio
import json

async def check_recent_sessions():
    client = redis.from_url("redis://redis:6379/0", decode_responses=True)
    
    # Scan for all sessions
    cursor = 0
    sessions = []
    while True:
        cursor, keys = await client.scan(cursor, match="session:*")
        for key in keys:
            val = await client.get(key)
            if val:
                data = json.loads(val)
                if data.get("user_id") == 2:
                    sessions.append({
                        "id": key.split(":")[1],
                        "status": data.get("status"),
                        "business": data.get("onboarding", {}).get("business_name")
                    })
        if cursor == 0:
            break
            
    print(f"SESSIONS_USER_2: {json.dumps(sessions)}")

if __name__ == "__main__":
    asyncio.run(check_recent_sessions())
