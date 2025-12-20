import structlog
import hashlib
import json
from typing import Optional, Dict, Any
from app.core.providers.dalle import DALLEImageProvider
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.config.settings import settings
from app.utils.exceptions import AgentException

logger = structlog.get_logger(__name__)

class LogoAgent:
    """
    Agent spécialisé dans la création de logos via DALL-E 3.
    
    Features:
    - Génération logos professionnels via DALL-E 3
    - Cache Redis (TTL 24h) pour éviter regénérations
    - Fallback gracieux si DALL-E échoue
    - Adaptation style par industrie
    """
    
    # Logo placeholder si DALL-E échoue
    FALLBACK_LOGO_URL = "https://placehold.co/400x400/3B82F6/FFFFFF/png?text=Logo"
    
    def __init__(self):
        self.dalle_provider = DALLEImageProvider(
            api_key=settings.OPENAI_API_KEY,
            model="dall-e-3"
        )
        self.redis_fs = RedisVirtualFileSystem(
            redis_url=settings.REDIS_URL,
            db_index=settings.REDIS_GENESIS_AI_DB
        )
        logger.info("LogoAgent initialized with DALL-E 3")

    async def run(
        self,
        company_name: str,
        industry: str,
        style: str = "modern",
        company_slogan: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Génère un logo pour l'entreprise via DALL-E 3.

        Args:
            company_name: Le nom de l'entreprise.
            industry: Secteur d'activité (e-commerce, restaurant, etc.).
            style: Style visuel (modern, minimalist, elegant, bold).
            company_slogan: Le slogan de l'entreprise (optionnel).
            use_cache: Utiliser le cache Redis (défaut: True).

        Returns:
            Dict contenant:
                - logo_url: URL du logo généré (ou placeholder)
                - logo_data: Base64 du logo (si disponible)
                - metadata: Métadonnées génération
                - cached: Booléen indiquant si provient du cache
        """
        try:
            # 1. Vérifier cache Redis
            cache_key = self._generate_cache_key(company_name, industry, style)
            
            if use_cache:
                cached_logo = await self._get_cached_logo(cache_key)
                if cached_logo:
                    logger.info("Logo retrieved from cache", company_name=company_name)
                    return {
                        **cached_logo,
                        "cached": True
                    }
            
            # 2. Adapter le style selon l'industrie
            adapted_style = self._adapt_style_for_industry(industry, style)
            
            logger.info(
                "Generating logo with DALL-E 3",
                company_name=company_name,
                industry=industry,
                style=adapted_style
            )
            
            # 3. Générer logo via DALL-E 3
            logo_result = await self.dalle_provider.generate_logo(
                business_name=company_name,
                industry=industry,
                style=adapted_style,
                quality="hd",
                size="1024x1024"
            )
            
            # 4. Enrichir avec métadonnées agent
            enriched_result = {
                "logo_url": logo_result.get("image_url"),
                "logo_data": logo_result.get("image_data"),
                "metadata": {
                    **logo_result.get("metadata", {}),
                    "agent": "LogoAgent",
                    "company_name": company_name,
                    "industry": industry,
                    "style_requested": style,
                    "style_applied": adapted_style,
                    "prompt_used": logo_result.get("prompt_used")
                },
                "cached": False
            }
            
            # 5. Stocker dans cache Redis (TTL 24h)
            if use_cache:
                await self._cache_logo(cache_key, enriched_result)
            
            logger.info(
                "Logo generated successfully",
                logo_url=enriched_result["logo_url"],
                cached=False
            )
            
            return enriched_result

        except Exception as e:
            logger.error(
                "Error during DALL-E logo generation, using fallback",
                error=str(e),
                company_name=company_name
            )
            
            # Fallback: retourner placeholder
            return self._get_fallback_logo(
                company_name=company_name,
                industry=industry,
                error=str(e)
            )
    
    def _generate_cache_key(self, company_name: str, industry: str, style: str) -> str:
        """
        Génère clé cache unique basée sur les paramètres.
        
        Format: logo:{hash_md5}
        """
        cache_input = f"{company_name.lower()}:{industry.lower()}:{style.lower()}"
        hash_value = hashlib.md5(cache_input.encode()).hexdigest()
        return f"logo:{hash_value}"
    
    async def _get_cached_logo(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Récupère logo depuis cache Redis.
        """
        try:
            cached_data = await self.redis_fs.read_file(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning("Cache read failed", error=str(e))
        return None
    
    async def _cache_logo(self, cache_key: str, logo_data: Dict[str, Any]) -> None:
        """
        Stocke logo dans cache Redis avec TTL 24h.
        """
        try:
            await self.redis_fs.write_file(
                file_path=cache_key,
                content=json.dumps(logo_data),
                ttl=86400  # 24 heures
            )
            logger.debug("Logo cached", cache_key=cache_key)
        except Exception as e:
            logger.warning("Cache write failed", error=str(e))
    
    def _adapt_style_for_industry(self, industry: str, base_style: str) -> str:
        """
        Adapte le style de logo selon l'industrie.
        
        Mappings intelligents:
        - Tech/Software → modern, tech
        - Restaurant/Food → elegant, traditional
        - Fashion/Beauty → elegant, creative
        - Finance/Legal → traditional, bold
        """
        industry_lower = industry.lower()
        
        # Mappings industrie → style recommandé
        industry_style_map = {
            "technology": "tech",
            "software": "tech",
            "saas": "modern",
            "e-commerce": "modern",
            "restaurant": "elegant",
            "food": "elegant",
            "cafe": "minimalist",
            "fashion": "elegant",
            "beauty": "elegant",
            "finance": "traditional",
            "legal": "traditional",
            "consulting": "bold",
            "marketing": "creative",
            "design": "creative",
            "health": "minimalist",
            "education": "traditional"
        }
        
        # Chercher match dans industry
        for key, recommended_style in industry_style_map.items():
            if key in industry_lower:
                logger.debug(
                    "Style adapted for industry",
                    industry=industry,
                    base_style=base_style,
                    adapted_style=recommended_style
                )
                return recommended_style
        
        # Sinon garder le style demandé
        return base_style
    
    def _get_fallback_logo(
        self,
        company_name: str,
        industry: str,
        error: str
    ) -> Dict[str, Any]:
        """
        Retourne logo placeholder si DALL-E échoue.
        """
        return {
            "logo_url": self.FALLBACK_LOGO_URL,
            "logo_data": None,
            "metadata": {
                "agent": "LogoAgent",
                "company_name": company_name,
                "industry": industry,
                "fallback": True,
                "error": error,
                "message": "DALL-E generation failed, using placeholder"
            },
            "cached": False
        }