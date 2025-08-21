import redis.asyncio as redis
import structlog
from app.config.settings import settings

logger = structlog.get_logger()

async def get_redis_client():
    """Returns a Redis client."""
    try:
        redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        if await redis_client.ping():
            logger.info("Successfully connected to Redis.")
            return redis_client
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return None