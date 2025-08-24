"""Redis Virtual File System pour sessions coaching persistantes"""

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
        self.session_prefix = "genesis:session"
        self.user_prefix = "genesis:user"
    
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
            key = f"{self.session_prefix}:{session_id}"
            serialized_data = json.dumps(data, default=str)
            await self.redis.set(key, serialized_data, ex=ttl)
            logger.info("Session written to Redis", session_id=session_id, ttl=ttl)
            return True
        except Exception as e:
            logger.error("Failed to write session to Redis", session_id=session_id, error=str(e))
            return False
    
    async def read_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Lire session coaching"""
        try:
            key = f"{self.session_prefix}:{session_id}"
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("Failed to read session from Redis", session_id=session_id, error=str(e))
            return None
    
    async def list_user_sessions(self, user_id: int) -> List[str]:
        """Lister sessions utilisateur"""
        try:
            pattern = f"{self.session_prefix}:*"
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                # Récupérer la session et vérifier si elle appartient à l'utilisateur
                session_data = await self.read_session(key.decode().split(":")[-1])
                if session_data and session_data.get("user_id") == user_id:
                    keys.append(key.decode().split(":")[-1])
            return keys
        except Exception as e:
            logger.error("Failed to list user sessions", user_id=user_id, error=str(e))
            return []
    
    async def delete_session(self, session_id: str) -> bool:
        """Supprimer session coaching"""
        try:
            key = f"{self.session_prefix}:{session_id}"
            result = await self.redis.delete(key)
            logger.info("Session deleted from Redis", session_id=session_id, deleted=bool(result))
            return bool(result)
        except Exception as e:
            logger.error("Failed to delete session from Redis", session_id=session_id, error=str(e))
            return False
    
    async def extend_session_ttl(self, session_id: str, ttl: int = 7200) -> bool:
        """Étendre TTL d'une session"""
        try:
            key = f"{self.session_prefix}:{session_id}"
            result = await self.redis.expire(key, ttl)
            logger.info("Session TTL extended", session_id=session_id, ttl=ttl)
            return bool(result)
        except Exception as e:
            logger.error("Failed to extend session TTL", session_id=session_id, error=str(e))
            return False
    
    async def write_user_state(self, user_id: int, state: Dict[str, Any], ttl: int = 86400) -> bool:
        """Écrire état utilisateur (TTL 24h par défaut)"""
        try:
            key = f"{self.user_prefix}:{user_id}"
            serialized_state = json.dumps(state, default=str)
            await self.redis.set(key, serialized_state, ex=ttl)
            logger.info("User state written to Redis", user_id=user_id, ttl=ttl)
            return True
        except Exception as e:
            logger.error("Failed to write user state to Redis", user_id=user_id, error=str(e))
            return False
    
    async def read_user_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Lire état utilisateur"""
        try:
            key = f"{self.user_prefix}:{user_id}"
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("Failed to read user state from Redis", user_id=user_id, error=str(e))
            return None
    
    async def close(self):
        """Fermer connexion Redis"""
        try:
            await self.redis.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error("Error closing Redis connection", error=str(e))