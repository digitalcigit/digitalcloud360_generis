import redis.asyncio as redis
import asyncio
import json

async def inspect_site_images():
    client = redis.from_url("redis://redis:6379/0", decode_responses=True)
    # Session ID from previous context/logs
    session_id = "9dbd044e-d23c-4c0f-ad89-8f323077bc25"
    
    site_json = await client.get(f"site:{session_id}")
    if site_json:
        site_data = json.loads(site_json)
        print("--- SITE IMAGES DATA ---")
        print(f"Hero Image: {site_data.get('hero_image')}")
        print(f"Service Images: {site_data.get('service_images')}")
        print(f"Feature Images: {site_data.get('feature_images')}")
        print(f"Logo URL: {site_data.get('logo_url')}")
        print("------------------------")
    else:
        print("SITE_DATA_NOT_FOUND")

if __name__ == "__main__":
    asyncio.run(inspect_site_images())
