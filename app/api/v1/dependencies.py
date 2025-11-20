from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.models.user import User
from app.config.database import get_db

from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.core.integrations.digitalcloud360 import DigitalCloud360APIClient
from app.core.integrations.tavily import TavilyClient
from app.core.quota import QuotaManager
from app.config.settings import settings
import redis.asyncio as redis


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = decode_access_token(token)
    if not token_data or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await db.get(User, token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_orchestrator() -> LangGraphOrchestrator:
    """
    Dependency function to get the LangGraphOrchestrator instance.
    This allows for easier mocking in tests.
    """
    return LangGraphOrchestrator()

def get_redis_vfs() -> RedisVirtualFileSystem:
    """FastAPI dependency to get an instance of the RedisVirtualFileSystem."""
    return RedisVirtualFileSystem()

def get_digitalcloud360_client() -> DigitalCloud360APIClient:
    """FastAPI dependency to get an instance of the DigitalCloud360APIClient."""
    return DigitalCloud360APIClient()

def get_tavily_client() -> TavilyClient:
    """FastAPI dependency to get an instance of the TavilyClient."""
    return TavilyClient()

def get_redis_client() -> redis.Redis:
    """Dependency function to get the Redis client instance."""
    return redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_quota_manager() -> QuotaManager:
    """FastAPI dependency to get an instance of the QuotaManager."""
    return QuotaManager()