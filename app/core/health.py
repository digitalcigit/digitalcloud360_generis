"""Module de health checks pour toutes les intégrations Genesis AI"""

import asyncio
from typing import Dict, Any, Tuple
import structlog
from app.config.settings import settings
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.core.integrations.digitalcloud360 import DigitalCloud360APIClient
from app.core.integrations.tavily import TavilyClient

logger = structlog.get_logger()

class HealthChecker:
    """Gestionnaire de health checks pour toutes les intégrations"""
    
    def __init__(self):
        self.redis_fs = RedisVirtualFileSystem()
        self.dc360_client = DigitalCloud360APIClient()
        self.tavily_client = TavilyClient()
    
    async def check_redis_integration(self) -> Tuple[bool, Dict[str, Any]]:
        """Health check Redis Virtual File System"""
        try:
            is_healthy = await self.redis_fs.health_check()
            
            if is_healthy:
                # Test écriture/lecture pour validation complète
                test_data = {"test": "health_check", "timestamp": "now"}
                await self.redis_fs.write_session("health_check_test", test_data, ttl=60)
                read_data = await self.redis_fs.read_session("health_check_test")
                await self.redis_fs.delete_session("health_check_test")
                
                return True, {
                    "status": "healthy",
                    "connection": "ok",
                    "read_write": "ok" if read_data else "failed",
                    "url": settings.REDIS_URL
                }
            else:
                return False, {
                    "status": "unhealthy",
                    "connection": "failed",
                    "url": settings.REDIS_URL
                }
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False, {
                "status": "error",
                "error": str(e),
                "url": settings.REDIS_URL
            }
    
    async def check_digitalcloud360_integration(self) -> Tuple[bool, Dict[str, Any]]:
        """Health check DigitalCloud360 API"""
        try:
            if not settings.VALIDATE_EXTERNAL_APIS:
                return True, {
                    "status": "skipped",
                    "reason": "VALIDATE_EXTERNAL_APIS=false",
                    "url": self.dc360_client.base_url
                }
            
            is_healthy = await self.dc360_client.health_check()
            
            return is_healthy, {
                "status": "healthy" if is_healthy else "unhealthy",
                "connection": "ok" if is_healthy else "failed",
                "url": self.dc360_client.base_url,
                "timeout": self.dc360_client.timeout
            }
        except Exception as e:
            logger.error("DigitalCloud360 health check failed", error=str(e))
            return False, {
                "status": "error",
                "error": str(e),
                "url": self.dc360_client.base_url
            }
    
    async def check_tavily_integration(self) -> Tuple[bool, Dict[str, Any]]:
        """Health check Tavily Research API"""
        try:
            if not settings.VALIDATE_EXTERNAL_APIS:
                return True, {
                    "status": "skipped",
                    "reason": "VALIDATE_EXTERNAL_APIS=false",
                    "api_key_configured": bool(settings.TAVILY_API_KEY != "your-tavily-key")
                }
            
            is_healthy = await self.tavily_client.health_check()
            
            return is_healthy, {
                "status": "healthy" if is_healthy else "unhealthy",
                "connection": "ok" if is_healthy else "failed",
                "api_key_configured": bool(settings.TAVILY_API_KEY != "your-tavily-key"),
                "base_url": settings.TAVILY_BASE_URL
            }
        except Exception as e:
            logger.error("Tavily health check failed", error=str(e))
            return False, {
                "status": "error",
                "error": str(e),
                "api_key_configured": bool(settings.TAVILY_API_KEY != "your-tavily-key")
            }
    
    async def check_ai_services(self) -> Dict[str, Dict[str, Any]]:
        """Health check services IA (OpenAI, Anthropic, LogoAI)"""
        services = {
            "openai": {
                "status": "configured" if settings.OPENAI_API_KEY != "your-openai-key" else "not_configured",
                "api_key_configured": settings.OPENAI_API_KEY != "your-openai-key"
            },
            "anthropic": {
                "status": "configured" if settings.ANTHROPIC_API_KEY != "your-anthropic-key" else "not_configured",
                "api_key_configured": settings.ANTHROPIC_API_KEY != "your-anthropic-key"
            },
            "logoai": {
                "status": "configured" if settings.LOGOAI_API_KEY != "your-logoai-key" else "not_configured",
                "api_key_configured": settings.LOGOAI_API_KEY != "your-logoai-key",
                "base_url": settings.LOGOAI_BASE_URL
            }
        }
        
        return services
    
    async def check_all_integrations(self) -> Dict[str, Any]:
        """Health check complet de toutes les intégrations"""
        logger.info("Starting comprehensive health check...")
        
        # Exécuter tous les checks en parallèle
        redis_task = self.check_redis_integration()
        dc360_task = self.check_digitalcloud360_integration() 
        tavily_task = self.check_tavily_integration()
        
        # Attendre tous les résultats
        redis_healthy, redis_info = await redis_task
        dc360_healthy, dc360_info = await dc360_task
        tavily_healthy, tavily_info = await tavily_task
        
        # Check services IA (synchrone car juste vérification config)
        ai_services = await self.check_ai_services()
        
        # Calculer état global
        critical_services = [redis_healthy]  # Redis est critique
        optional_services = [dc360_healthy, tavily_healthy]  # APIs externes optionnelles
        
        overall_healthy = all(critical_services) and (
            not settings.STRICT_HEALTH_CHECKS or all(optional_services)
        )
        
        result = {
            "overall_status": "healthy" if overall_healthy else "degraded",
            "strict_mode": settings.STRICT_HEALTH_CHECKS,
            "validate_external_apis": settings.VALIDATE_EXTERNAL_APIS,
            "integrations": {
                "redis": redis_info,
                "digitalcloud360": dc360_info,
                "tavily": tavily_info
            },
            "ai_services": ai_services,
            "summary": {
                "total_checks": 3,
                "healthy_checks": sum([redis_healthy, dc360_healthy, tavily_healthy]),
                "critical_services_healthy": all(critical_services),
                "optional_services_healthy": all(optional_services)
            }
        }
        
        logger.info(
            "Health check completed",
            overall_status=result["overall_status"],
            critical_healthy=all(critical_services),
            optional_healthy=all(optional_services)
        )
        
        return result

# Instance globale pour l'application
health_checker = HealthChecker()