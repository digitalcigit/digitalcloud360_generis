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
    
    async def write_session(self, user_id: int, brief_id: str, data: Dict[str, Any], ttl: int = 7200) -> bool:
        """
        Écrire session coaching (TTL 2h par défaut)
        
        Args:
            user_id: ID utilisateur propriétaire
            brief_id: ID unique du business brief
            data: Données session à persister
            ttl: Time-to-live en secondes (default 2h)
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            key = f"{self.session_prefix}:{user_id}:{brief_id}"
            serialized_data = json.dumps(data, default=str)
            await self.redis.set(key, serialized_data, ex=ttl)
            logger.info(
                "Session written to Redis",
                user_id=user_id,
                brief_id=brief_id,
                ttl=ttl
            )
            return True
        except Exception as e:
            logger.error(
                "Failed to write session to Redis",
                user_id=user_id,
                brief_id=brief_id,
                error=str(e)
            )
            return False
    
    async def read_session(self, user_id: int, brief_id: str) -> Optional[Dict[str, Any]]:
        """
        Lire session coaching
        
        Args:
            user_id: ID utilisateur propriétaire
            brief_id: ID unique du business brief
            
        Returns:
            Dict des données session ou None si non trouvé
        """
        try:
            key = f"{self.session_prefix}:{user_id}:{brief_id}"
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(
                "Failed to read session from Redis",
                user_id=user_id,
                brief_id=brief_id,
                error=str(e)
            )
            return None
    
    async def list_user_sessions(self, user_id: int) -> List[str]:
        """
        Lister sessions utilisateur
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            Liste des brief_ids pour cet utilisateur
        """
        try:
            pattern = f"{self.session_prefix}:{user_id}:*"
            brief_ids = []
            async for key in self.redis.scan_iter(match=pattern):
                # Extraire brief_id depuis clé genesis:session:{user_id}:{brief_id}
                key_parts = key.decode().split(":")
                if len(key_parts) >= 4:
                    brief_id = key_parts[3]
                    brief_ids.append(brief_id)
            logger.info("User sessions listed", user_id=user_id, count=len(brief_ids))
            return brief_ids
        except Exception as e:
            logger.error("Failed to list user sessions", user_id=user_id, error=str(e))
            return []
    
    async def delete_session(self, user_id: int, brief_id: str) -> bool:
        """
        Supprimer session coaching
        
        Args:
            user_id: ID utilisateur propriétaire
            brief_id: ID unique du business brief
            
        Returns:
            bool: True si supprimé, False sinon
        """
        try:
            key = f"{self.session_prefix}:{user_id}:{brief_id}"
            result = await self.redis.delete(key)
            logger.info(
                "Session deleted from Redis",
                user_id=user_id,
                brief_id=brief_id,
                deleted=bool(result)
            )
            return bool(result)
        except Exception as e:
            logger.error(
                "Failed to delete session from Redis",
                user_id=user_id,
                brief_id=brief_id,
                error=str(e)
            )
            return False
    
    async def extend_session_ttl(self, user_id: int, brief_id: str, ttl: int = 7200) -> bool:
        """
        Étendre TTL d'une session
        
        Args:
            user_id: ID utilisateur propriétaire
            brief_id: ID unique du business brief
            ttl: Nouveau time-to-live en secondes
            
        Returns:
            bool: True si TTL mis à jour, False sinon
        """
        try:
            key = f"{self.session_prefix}:{user_id}:{brief_id}"
            result = await self.redis.expire(key, ttl)
            logger.info(
                "Session TTL extended",
                user_id=user_id,
                brief_id=brief_id,
                ttl=ttl
            )
            return bool(result)
        except Exception as e:
            logger.error(
                "Failed to extend session TTL",
                user_id=user_id,
                brief_id=brief_id,
                error=str(e)
            )
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

    async def read_file(self, file_path: str) -> Optional[str]:
        """
        Lecture générique fichier/clé Redis
        
        Args:
            file_path: Clé Redis complète
            
        Returns:
            Contenu (str) ou None
        """
        try:
            data = await self.redis.get(file_path)
            if data:
                return data
            return None
        except Exception as e:
            logger.error("Failed to read file from Redis", key=file_path, error=str(e))
            return None

    async def write_file(self, file_path: str, content: str, ttl: int = None) -> bool:
        """
        Écriture générique fichier/clé Redis
        
        Args:
            file_path: Clé Redis complète
            content: Contenu à écrire (str)
            ttl: TTL en secondes (optionnel)
            
        Returns:
            bool: True si succès
        """
        try:
            if ttl:
                await self.redis.set(file_path, content, ex=ttl)
            else:
                await self.redis.set(file_path, content)
            return True
        except Exception as e:
            logger.error("Failed to write file to Redis", key=file_path, error=str(e))
            return False