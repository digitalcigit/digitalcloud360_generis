import httpx
from typing import Dict, Any, Optional
import structlog
from app.config.settings import settings
import asyncio

logger = structlog.get_logger()

class DigitalCloud360APIClient:
    """Client API DigitalCloud360 pour intégration service-to-service"""
    
    def __init__(self, timeout=30, max_retries=3):
        self.base_url = settings.DIGITALCLOUD360_API_URL
        self.service_secret = settings.DIGITALCLOUD360_SERVICE_SECRET
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def health_check(self) -> bool:
        """Vérifier connexion DigitalCloud360 API avec retry logic"""
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    headers = {"X-Service-Secret": self.service_secret}
                    response = await client.get(f"{self.base_url}/health", headers=headers, timeout=self.timeout)
                    response.raise_for_status()
                    logger.info("DigitalCloud360 API is healthy")
                    return True
            except httpx.RequestError as e:
                logger.warning(
                    "DigitalCloud360 API health check failed", 
                    attempt=attempt + 1, 
                    max_retries=self.max_retries, 
                    error=str(e)
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("DigitalCloud360 API is unhealthy after multiple retries")
                    return False
        return False

    async def create_website(self, business_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Créer site web depuis brief business"""
        async with httpx.AsyncClient() as client:
            headers = {"X-Service-Secret": self.service_secret, "Content-Type": "application/json"}
            try:
                response = await client.post(
                    f"{self.base_url}/v1/websites", 
                    json=business_brief, 
                    headers=headers, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                logger.info("Successfully created website on DigitalCloud360", business_brief=business_brief)
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "Failed to create website on DigitalCloud360",
                    status_code=e.response.status_code,
                    response_text=e.response.text,
                    business_brief=business_brief
                )
                raise

    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer profil utilisateur DigitalCloud360"""
        async with httpx.AsyncClient() as client:
            headers = {"X-Service-Secret": self.service_secret}
            try:
                response = await client.get(f"{self.base_url}/v1/users/{user_id}", headers=headers, timeout=self.timeout)
                response.raise_for_status()
                logger.info("Successfully retrieved user profile from DigitalCloud360", user_id=user_id)
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.warn("User not found on DigitalCloud360", user_id=user_id)
                    return None
                logger.error(
                    "Failed to get user profile from DigitalCloud360",
                    status_code=e.response.status_code,
                    user_id=user_id
                )
                raise