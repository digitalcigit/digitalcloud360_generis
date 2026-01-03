import httpx
import asyncio

async def get_token():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                "http://localhost:8002/api/v1/auth/token",
                data={"username": "dcitest@digital.ci", "password": "DiGiT@l2025"}
            )
            if resp.status_code == 200:
                print(resp.json().get("access_token"))
            else:
                print(f"ERROR: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    asyncio.run(get_token())
