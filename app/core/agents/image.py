"""
ImageAgent - Génération d'images de contenu via DALL-E 3
Phase 2 Premium - Vision "WHAOUUUU"

Génère toutes les images du site (pas seulement le logo):
- Hero images personnalisées
- Illustrations services
- Images features
- Galerie photos
"""

import structlog
import hashlib
import json
import asyncio
import os
import httpx
from typing import Dict, Any, List, Optional
from app.core.providers.dalle import DALLEImageProvider
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.config.settings import settings

logger = structlog.get_logger(__name__)


class ImageAgent:
    """
    Agent spécialisé génération images contenu via DALL-E 3.
    
    Features:
    - Hero images personnalisées selon secteur
    - Illustrations services
    - Images features/différenciateurs
    - Cache Redis (TTL 7 jours)
    - Fallback images stock Unsplash
    - Persistance locale des images (évite expiration liens OpenAI)
    """
    
    # Images de fallback haute qualité (Unsplash)
    FALLBACK_IMAGES = {
        "hero": "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=1792&h=1024&fit=crop",
        "service": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=1024&h=1024&fit=crop",
        "feature": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1024&h=1024&fit=crop",
        "gallery": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1024&h=1024&fit=crop"
    }
    
    # Tailles optimales DALL-E par type d'image
    IMAGE_SIZES = {
        "hero": "1792x1024",      # Wide pour hero sections
        "service": "1024x1024",   # Carré pour cards services
        "feature": "1024x1024",   # Carré pour features
        "gallery": "1024x1024"    # Carré pour galerie
    }

    # Dossier de stockage local
    LOCAL_STORAGE_PATH = "/app/app/static/images"
    
    def __init__(self):
        self.dalle_provider = DALLEImageProvider(
            api_key=settings.OPENAI_API_KEY,
            model="dall-e-3"
        )
        self.redis_fs = RedisVirtualFileSystem()
        
        # Ensure local storage exists
        os.makedirs(self.LOCAL_STORAGE_PATH, exist_ok=True)
        
        logger.info("ImageAgent initialized with DALL-E 3 and local persistence")
    
    async def _download_and_save_image(self, url: str, filename: str) -> Optional[str]:
        """Télécharge l'image depuis l'URL et la sauvegarde localement."""
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=30.0)
                if response.status_code == 200:
                    filepath = os.path.join(self.LOCAL_STORAGE_PATH, filename)
                    
                    # Write file synchronously (fast enough for images) to avoid aiofiles dependency
                    with open(filepath, mode='wb') as f:
                        f.write(response.content)
                    
                    # Retourne l'URL relative accessible via l'API
                    # Assumant que /static est monté dans FastAPI
                    return f"/static/images/{filename}"
                else:
                    logger.error("Failed to download image", status_code=response.status_code, url=url)
                    return None
        except Exception as e:
            logger.error("Error saving image locally", error=str(e), url=url)
            return None

    async def run(
        self,
        business_name: str,
        industry_sector: str,
        image_type: str,
        context: Optional[str] = None,
        style: str = "professional",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Génère une image de contenu adaptée au business.
        """
        try:
            logger.info(
                "ImageAgent generating image",
                business_name=business_name,
                industry_sector=industry_sector,
                image_type=image_type,
                context=context
            )
            
            # 1. Vérifier cache
            cache_key = self._generate_cache_key(
                business_name, industry_sector, image_type, context, style
            )
            
            if use_cache:
                cached = await self._get_cached_image(cache_key)
                if cached:
                    logger.info("ImageAgent cache hit", cache_key=cache_key)
                    return {**cached, "cached": True}
            
            # 2. Construire prompt optimisé
            prompt = self._build_image_prompt(
                business_name=business_name,
                industry_sector=industry_sector,
                image_type=image_type,
                context=context,
                style=style
            )
            
            # 3. Générer via DALL-E
            size = self.IMAGE_SIZES.get(image_type, "1024x1024")
            quality = "hd" if image_type == "hero" else "standard"
            
            result = await self.dalle_provider.generate_image(
                prompt=prompt,
                size=size,
                quality=quality
            )
            
            # 4. Persistance Locale
            image_url = result.get("image_url")
            local_url = None
            
            if image_url:
                # Générer un nom de fichier unique (sanitize colons for Windows compatibility)
                safe_key = cache_key.replace(":", "_")
                filename = f"{safe_key}_{hashlib.md5(image_url.encode()).hexdigest()[:8]}.png"
                local_url = await self._download_and_save_image(image_url, filename)
            
            # Si le téléchargement échoue, on garde l'URL DALL-E (qui expirera...)
            final_url = local_url if local_url else image_url
            
            # 5. Préparer résultat
            output = {
                "image_url": final_url,
                "original_url": image_url, # On garde l'original au cas où
                "metadata": {
                    **result.get("metadata", {}),
                    "agent": "ImageAgent",
                    "image_type": image_type,
                    "business_name": business_name,
                    "industry_sector": industry_sector,
                    "context": context,
                    "style": style,
                    "local_persistence": bool(local_url)
                },
                "cached": False
            }
            
            # 6. Cacher le résultat
            await self._cache_image(cache_key, output)
            
            logger.info(
                "ImageAgent generation success",
                image_type=image_type,
                business_name=business_name,
                persisted=bool(local_url)
            )
            
            return output
            
        except Exception as e:
            logger.error(
                "ImageAgent generation failed, using fallback",
                error=str(e),
                image_type=image_type
            )
            
            # Fallback vers image stock
            return {
                "image_url": self.FALLBACK_IMAGES.get(image_type, self.FALLBACK_IMAGES["hero"]),
                "metadata": {
                    "agent": "ImageAgent",
                    "fallback": True,
                    "error": str(e),
                    "image_type": image_type,
                    "business_name": business_name
                },
                "cached": False
            }
    
    async def generate_all_site_images(
        self,
        business_name: str,
        industry_sector: str,
        services: Optional[List[str]] = None,
        features: Optional[List[str]] = None,
        style: str = "professional"
    ) -> Dict[str, Any]:
        """
        Génère toutes les images nécessaires pour un site en PARALLÈLE.
        """
        
        logger.info(
            "Generating all site images (PARALLEL)",
            business_name=business_name,
            industry_sector=industry_sector,
            services_count=len(services or []),
            features_count=len(features or [])
        )
        
        images = {}
        stats = {"generated": 0, "cached": 0, "fallback": 0}
        
        # Prepare all tasks
        tasks = []
        
        # 1. Hero Task
        tasks.append(self.run(
            business_name=business_name,
            industry_sector=industry_sector,
            image_type="hero",
            context=None,
            style=style
        ))
        
        # 2. Service Tasks (max 4)
        for service in (services or [])[:4]:
            tasks.append(self.run(
                business_name=business_name,
                industry_sector=industry_sector,
                image_type="service",
                context=service,
                style=style
            ))
            
        # 3. Feature Tasks (max 3)
        for feature in (features or [])[:3]:
            tasks.append(self.run(
                business_name=business_name,
                industry_sector=industry_sector,
                image_type="feature",
                context=feature,
                style=style
            ))
            
        # Execute all in parallel
        # Note: Be mindful of rate limits. DALL-E has RPM limits.
        # If rate limited, individual calls might fail and fallback to stock images, which is handled in run()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        hero_result = None
        service_results = []
        feature_results = []
        
        # Map results back to categories
        idx = 0
        
        # Hero (1)
        if idx < len(results):
            res = results[idx]
            hero_result = res if not isinstance(res, Exception) else self._get_fallback_result("hero", str(res))
            idx += 1
            
        # Services (count)
        svc_count = len((services or [])[:4])
        for _ in range(svc_count):
            if idx < len(results):
                res = results[idx]
                service_results.append(res if not isinstance(res, Exception) else self._get_fallback_result("service", str(res)))
                idx += 1
                
        # Features (count)
        feat_count = len((features or [])[:3])
        for _ in range(feat_count):
            if idx < len(results):
                res = results[idx]
                feature_results.append(res if not isinstance(res, Exception) else self._get_fallback_result("feature", str(res)))
                idx += 1
        
        # Update stats & images
        if hero_result:
            images["hero_image"] = hero_result["image_url"]
            self._update_stats(stats, hero_result)
            
        images["service_images"] = []
        for res in service_results:
            images["service_images"].append(res["image_url"])
            self._update_stats(stats, res)
            
        images["feature_images"] = []
        for res in feature_results:
            images["feature_images"].append(res["image_url"])
            self._update_stats(stats, res)
            
        images["generation_stats"] = stats
        
        logger.info(
            "All site images generated",
            stats=stats,
            hero=bool(images.get("hero_image")),
            services_count=len(images["service_images"]),
            features_count=len(images["feature_images"])
        )
        
        return images

    def _get_fallback_result(self, image_type: str, error: str) -> Dict[str, Any]:
        """Helper for exception fallback"""
        return {
            "image_url": self.FALLBACK_IMAGES.get(image_type, self.FALLBACK_IMAGES["hero"]),
            "metadata": {
                "agent": "ImageAgent",
                "fallback": True,
                "error": error,
                "image_type": image_type
            },
            "cached": False
        }
    
    def _build_image_prompt(
        self,
        business_name: str,
        industry_sector: str,
        image_type: str,
        context: Optional[str],
        style: str
    ) -> str:
        """Construit prompt DALL-E optimisé selon type d'image."""
        
        # Prompts templates par type
        prompts = {
            "hero": f"""
Professional hero image for {business_name}, a {industry_sector} business.
Scene showing {context or 'the business activity in a professional environment'}.
Style: {style}, modern, high-quality, well-lit.
NO text, NO logos, NO watermarks.
Photorealistic, wide format suitable for website hero section.
Clean composition with space for text overlay.
            """.strip(),
            
            "service": f"""
Professional illustration for a business service: {context or 'professional service'}.
Business: {business_name} in {industry_sector} industry.
Style: {style}, clean, professional, inviting.
NO text, NO logos, NO watermarks.
Square format, suitable for service card.
Show people or activity related to the service.
            """.strip(),
            
            "feature": f"""
Abstract professional visual representing: {context or 'business excellence'}.
For a {industry_sector} business.
Style: {style}, modern, subtle gradients, professional.
NO text, NO logos, NO watermarks.
Clean minimalist design, suitable for feature showcase.
            """.strip(),
            
            "gallery": f"""
Professional photograph of {context or industry_sector + ' business environment'}.
For {business_name}.
Style: realistic, well-lit, {style}.
NO text, NO logos, NO watermarks.
High-quality, suitable for portfolio or gallery section.
            """.strip()
        }
        
        return prompts.get(image_type, prompts["gallery"])
    
    def _generate_cache_key(self, *args) -> str:
        """Génère clé cache unique basée sur les paramètres."""
        content = "_".join(str(arg).lower() for arg in args if arg)
        hash_digest = hashlib.md5(content.encode()).hexdigest()
        return f"image_agent:{hash_digest}"
    
    async def _get_cached_image(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Récupère image depuis cache Redis."""
        try:
            cached_data = await self.redis_fs.read_file(f"cache/{cache_key}.json")
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.debug("Cache miss or error", cache_key=cache_key, error=str(e))
        return None
    
    async def _cache_image(
        self,
        cache_key: str,
        data: Dict[str, Any],
        ttl: int = 604800  # 7 jours
    ) -> None:
        """Cache image dans Redis avec TTL."""
        try:
            cache_data = {
                "image_url": data.get("image_url"),
                "metadata": data.get("metadata", {})
            }
            await self.redis_fs.write_file(
                f"cache/{cache_key}.json",
                json.dumps(cache_data),
                ttl=ttl
            )
            logger.debug("Image cached", cache_key=cache_key)
        except Exception as e:
            logger.warning("Failed to cache image", cache_key=cache_key, error=str(e))
    
    def _update_stats(self, stats: Dict[str, int], result: Dict[str, Any]) -> None:
        """Met à jour statistiques de génération."""
        if result.get("cached"):
            stats["cached"] += 1
        elif result.get("metadata", {}).get("fallback"):
            stats["fallback"] += 1
        else:
            stats["generated"] += 1
