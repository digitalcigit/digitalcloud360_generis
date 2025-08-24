"""Client API DigitalCloud360 pour intégration service-to-service"""

import httpx
from typing import Dict, Any, Optional
import structlog
from app.config.settings import settings

logger = structlog.get_logger()

class DigitalCloud360APIClient:
    """Client API DigitalCloud360 pour intégration service-to-service"""
    
    def __init__(self):
        self.base_url = settings.DIGITALCLOUD360_API_URL
        self.service_secret = settings.DIGITALCLOUD360_SERVICE_SECRET
        self.timeout = settings.DIGITALCLOUD360_TIMEOUT
        self.headers = {
            "Content-Type": "application/json",
            "X-Service-Secret": self.service_secret,
            "User-Agent": f"Genesis-AI/{settings.APP_VERSION}"
        }
    
    async def health_check(self) -> bool:
        """Vérifier connexion DigitalCloud360 API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self.headers
                )
                if response.status_code == 200:
                    logger.info("DigitalCloud360 API connection healthy")
                    return True
                else:
                    logger.warning("DigitalCloud360 API health check failed", status_code=response.status_code)
                    return False
        except Exception as e:
            logger.error("DigitalCloud360 API connection failed", error=str(e))
            return False
    
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer profil utilisateur DigitalCloud360"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/{user_id}/profile",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info("User profile retrieved successfully", user_id=user_id)
                    return response.json()
                elif response.status_code == 404:
                    logger.warning("User profile not found", user_id=user_id)
                    return None
                else:
                    logger.error("Failed to retrieve user profile", 
                               user_id=user_id, status_code=response.status_code)
                    return None
        except Exception as e:
            logger.error("Error retrieving user profile", user_id=user_id, error=str(e))
            return None
    
    async def create_website(self, business_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Créer site web depuis brief business"""
        try:
            async with httpx.AsyncClient(timeout=60) as client:  # Timeout plus long pour création site
                response = await client.post(
                    f"{self.base_url}/api/v1/websites",
                    headers=self.headers,
                    json=business_brief
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info("Website created successfully", 
                              website_id=result.get("id"), 
                              user_id=business_brief.get("user_id"))
                    return {
                        "success": True,
                        "website": result
                    }
                else:
                    logger.error("Failed to create website", 
                               status_code=response.status_code,
                               response_body=response.text)
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            logger.error("Error creating website", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_website(self, website_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Mettre à jour un site web existant"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    f"{self.base_url}/api/v1/websites/{website_id}",
                    headers=self.headers,
                    json=updates
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("Website updated successfully", website_id=website_id)
                    return {
                        "success": True,
                        "website": result
                    }
                else:
                    logger.error("Failed to update website", 
                               website_id=website_id,
                               status_code=response.status_code)
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}"
                    }
        except Exception as e:
            logger.error("Error updating website", website_id=website_id, error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_website_status(self, website_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer statut d'un site web"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/websites/{website_id}/status",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning("Website status not found", 
                                 website_id=website_id, 
                                 status_code=response.status_code)
                    return None
        except Exception as e:
            logger.error("Error getting website status", website_id=website_id, error=str(e))
            return None
    
    async def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Valider JWT token DigitalCloud360"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/validate",
                    headers=self.headers,
                    json={"token": token}
                )
                
                if response.status_code == 200:
                    logger.info("JWT token validated successfully")
                    return response.json()
                else:
                    logger.warning("JWT token validation failed", status_code=response.status_code)
                    return None
        except Exception as e:
            logger.error("Error validating JWT token", error=str(e))
            return None