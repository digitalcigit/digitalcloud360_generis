import redis.asyncio as redis
import json
from typing import Dict, Any, Optional, List
import structlog
from app.config.settings import settings

logger = structlog.get_logger()

class RedisVirtualFileSystem:
    """Virtual File System Redis pour sessions coaching persistantes"""
    
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
    
    async def health_check(self) -> bool:
        """Vérifier connexion Redis"""
        try:
            await self.redis.ping()
            logger.info("Redis Virtual File System healthy")
            return True
        except Exception as e:
            logger.error("Redis connection failed", error=str(e))
            return False
    
    async def write_session(self, session_id: str, data: Dict[str, Any], ttl: int = 7200) -> bool:
        """Écrire session coaching (TTL 2h par défaut)"""
        try:
            await self.redis.set(f"session:{session_id}", json.dumps(data), ex=ttl)
            logger.info("Coaching session written to Redis", session_id=session_id)
            return True
        except Exception as e:
            logger.error("Failed to write session to Redis", session_id=session_id, error=str(e))
            return False
    
    async def read_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Lire session coaching"""
        try:
            session_data = await self.redis.get(f"session:{session_id}")
            if session_data:
                logger.info("Coaching session read from Redis", session_id=session_id)
                return json.loads(session_data)
            logger.warn("Coaching session not found in Redis", session_id=session_id)
            return None
        except Exception as e:
            logger.error("Failed to read session from Redis", session_id=session_id, error=str(e))
            return None
    
    async def list_user_sessions(self, user_id: int) -> List[str]:
        """Lister sessions utilisateur"""
        # This is a simplified version. A real implementation would need a different data structure.
        # For now, we will scan for keys, which is not recommended in production.
        try:
            session_keys = []
            async for key in self.redis.scan_iter(f"session:user:{user_id}:*"):
                session_keys.append(key.decode('utf-8'))
            logger.info(f"Found {len(session_keys)} sessions for user", user_id=user_id)
            return session_keys
        except Exception as e:
            logger.error("Failed to list user sessions from Redis", user_id=user_id, error=str(e))
            return []