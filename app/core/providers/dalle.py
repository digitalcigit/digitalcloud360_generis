"""
DALL-E 3 Image Provider - Génération logos et images
OpenAI DALL-E 3 pour création visuels professionnels
"""

import httpx
import base64
import structlog
from typing import Dict, Any, List, Optional

from .base import BaseImageProvider

logger = structlog.get_logger(__name__)


class DALLEImageProvider(BaseImageProvider):
    """
    Provider DALL-E 3 pour génération images/logos
    
    Modèles:
    - dall-e-3 (haute qualité, recommandé)
    - dall-e-2 (legacy, moins cher)
    
    Avantages:
    - Qualité supérieure vs autres modèles
    - Compréhension contexte business
    - Styles professionnels variés
    - Résolutions HD
    
    Remplace: LogoAI (abandonné pour complexité API)
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "dall-e-3",
        base_url: str = "https://api.openai.com",
        timeout: int = 60,
        **kwargs
    ):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(
            "DALLEImageProvider initialized",
            model=model,
            base_url=base_url
        )
    
    async def generate_logo(
        self,
        business_name: str,
        industry: str,
        style: str = "modern",
        color_scheme: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère un logo professionnel via DALL-E 3
        
        Args:
            business_name: Nom de l'entreprise
            industry: Secteur d'activité
            style: Style visuel (modern, minimalist, elegant, bold, traditional)
            color_scheme: Palette couleurs (ex: ["blue", "green"])
            
        Returns:
            Dict contenant:
                - image_url: URL image générée (valide 1h)
                - image_data: Base64 si response_format='b64_json'
                - prompt_used: Prompt DALL-E utilisé
                - metadata: Métadonnées génération
                
        Note:
            DALL-E 3 sizes: 1024x1024, 1792x1024, 1024x1792
            Pour logos, on utilise 1024x1024 (carré)
        """
        
        # Construire prompt optimisé pour logos
        logo_prompt = self._build_logo_prompt(
            business_name=business_name,
            industry=industry,
            style=style,
            color_scheme=color_scheme
        )
        
        logger.info(
            "DALL-E generate logo",
            business_name=business_name,
            industry=industry,
            style=style
        )
        
        # Configuration génération logo
        size = kwargs.pop("size", "1024x1024")  # Carré pour logo
        quality = kwargs.pop("quality", "hd")  # HD recommandé logos
        
        try:
            result = await self.generate_image(
                prompt=logo_prompt,
                size=size,
                quality=quality,
                **kwargs
            )
            
            # Ajouter métadonnées spécifiques logo
            result["metadata"]["logo_type"] = "business_logo"
            result["metadata"]["business_name"] = business_name
            result["metadata"]["industry"] = industry
            result["metadata"]["style"] = style
            
            logger.info("DALL-E logo generation success")
            
            return result
            
        except Exception as e:
            logger.error("DALL-E logo generation failed", error=str(e))
            raise
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère une image générique via DALL-E 3
        
        Args:
            prompt: Description détaillée de l'image
            size: Taille image (1024x1024, 1792x1024, 1024x1792)
            quality: Qualité (standard, hd)
            
        Returns:
            Dict contenant:
                - image_url: URL image (expire après 1h)
                - image_data: Base64 si response_format='b64_json'
                - revised_prompt: Prompt révisé par DALL-E (sécurité)
                - metadata: Métadonnées
                
        Raises:
            Exception: Si erreur API, content policy, rate limit
        """
        
        # Validation size pour DALL-E 3
        valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
        if self.model == "dall-e-3" and size not in valid_sizes:
            logger.warning(
                f"Invalid size {size} for DALL-E 3, using 1024x1024",
                requested_size=size
            )
            size = "1024x1024"
        
        # Configuration payload
        response_format = kwargs.get("response_format", "url")  # url ou b64_json
        n = 1  # DALL-E 3 ne supporte que n=1
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n,
            "response_format": response_format
        }
        
        # Style optionnel (vivid ou natural)
        if "style" in kwargs and self.model == "dall-e-3":
            payload["style"] = kwargs["style"]
        
        logger.info(
            "DALL-E generate image request",
            model=self.model,
            size=size,
            quality=quality,
            prompt_length=len(prompt)
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/images/generations",
                    headers=self.headers,
                    json=payload
                )
                
                # Gestion erreurs HTTP
                if response.status_code == 400:
                    error_detail = response.json().get("error", {}).get("message", "Unknown error")
                    
                    # Content policy violation
                    if "content_policy" in error_detail.lower():
                        logger.error("DALL-E content policy violation", prompt=prompt)
                        raise Exception("Content policy violation - prompt refused by DALL-E")
                    
                    logger.error("DALL-E bad request", error=error_detail)
                    raise Exception(f"DALL-E API error: {error_detail}")
                
                elif response.status_code == 429:
                    logger.error("DALL-E rate limit exceeded")
                    raise Exception("DALL-E rate limit - retry later")
                
                elif response.status_code == 503:
                    logger.error("DALL-E service unavailable")
                    raise Exception("DALL-E API unavailable - retry later")
                
                elif response.status_code != 200:
                    logger.error(
                        "DALL-E API error",
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise Exception(f"DALL-E API error: {response.status_code}")
                
                # Parse réponse
                result = response.json()
                
                if not result.get("data"):
                    logger.error("No data in DALL-E response", result=result)
                    raise Exception("Invalid DALL-E response format")
                
                image_data = result["data"][0]
                
                # Construire réponse normalisée
                output = {
                    "prompt_used": prompt,
                    "metadata": {
                        "provider": "dalle",
                        "model": self.model,
                        "size": size,
                        "quality": quality,
                        "response_format": response_format
                    }
                }
                
                # URL ou base64 selon format
                if response_format == "url":
                    output["image_url"] = image_data.get("url")
                    output["image_data"] = None
                elif response_format == "b64_json":
                    output["image_url"] = None
                    output["image_data"] = image_data.get("b64_json")
                
                # Revised prompt (DALL-E 3 améliore parfois le prompt)
                if "revised_prompt" in image_data:
                    output["metadata"]["revised_prompt"] = image_data["revised_prompt"]
                
                logger.info(
                    "DALL-E image generation success",
                    has_url=output["image_url"] is not None,
                    has_data=output["image_data"] is not None
                )
                
                return output
                
        except httpx.TimeoutException:
            logger.error("DALL-E request timeout", timeout=self.timeout)
            raise Exception(f"DALL-E timeout after {self.timeout}s - retry or reduce quality")
        
        except httpx.RequestError as e:
            logger.error("DALL-E network error", error=str(e))
            raise Exception(f"DALL-E network error: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        Vérifie disponibilité DALL-E API
        
        Returns:
            bool: True si API accessible
            
        Note:
            Ne génère PAS d'image réelle (coûteux),
            on vérifie juste les credentials via endpoint models
        """
        
        logger.info("DALL-E health check")
        
        try:
            # Vérifier API key via endpoint /models
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/v1/models",
                    headers=self.headers
                )
                
                is_healthy = response.status_code == 200
                
                logger.info("DALL-E health check result", healthy=is_healthy)
                
                return is_healthy
                
        except Exception as e:
            logger.warning("DALL-E health check failed", error=str(e))
            return False
    
    # ============================================================
    # MÉTHODES PRIVÉES
    # ============================================================
    
    def _build_logo_prompt(
        self,
        business_name: str,
        industry: str,
        style: str = "modern",
        color_scheme: Optional[List[str]] = None
    ) -> str:
        """
        Construit prompt optimisé pour génération logo
        
        Techniques:
        - Clarté description style
        - Mention "logo professionnel"
        - Spécifications couleurs
        - Contexte industrie
        - Format simple (pas texte complexe dans logo)
        """
        
        # Base prompt
        prompt_parts = [
            f"A professional {style} logo for '{business_name}',",
            f"a {industry} business."
        ]
        
        # Style descriptions
        style_descriptions = {
            "modern": "Clean lines, contemporary design, minimalist approach",
            "minimalist": "Simple, elegant, essential elements only",
            "elegant": "Sophisticated, refined, timeless design",
            "bold": "Strong, impactful, vibrant and eye-catching",
            "traditional": "Classic, established, trustworthy appearance",
            "creative": "Innovative, artistic, unique visual identity",
            "tech": "Futuristic, digital, cutting-edge aesthetic"
        }
        
        if style.lower() in style_descriptions:
            prompt_parts.append(style_descriptions[style.lower()])
        
        # Couleurs si spécifiées
        if color_scheme and len(color_scheme) > 0:
            colors_str = ", ".join(color_scheme)
            prompt_parts.append(f"Color scheme: {colors_str}.")
        
        # Instructions format logo
        prompt_parts.extend([
            "Vector-style design.",
            "Suitable for business cards and website.",
            "No text or letters in the design (symbol/icon only).",
            "White or transparent background."
        ])
        
        final_prompt = " ".join(prompt_parts)
        
        logger.debug("Logo prompt built", prompt=final_prompt)
        
        return final_prompt
    
    async def generate_logo_with_text(
        self,
        business_name: str,
        industry: str,
        style: str = "modern",
        color_scheme: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère logo AVEC texte business name intégré
        
        Note:
            DALL-E 3 meilleur pour texte que DALL-E 2,
            mais peut encore avoir typos. À utiliser avec précaution.
            
        Returns:
            Même format que generate_logo()
        """
        
        # Prompt avec texte
        prompt_parts = [
            f"A professional {style} logo design with the text '{business_name}'",
            f"for a {industry} business."
        ]
        
        if color_scheme:
            colors_str = ", ".join(color_scheme)
            prompt_parts.append(f"Color scheme: {colors_str}.")
        
        prompt_parts.extend([
            "The business name must be clearly readable.",
            "Modern typography, well-balanced composition.",
            "White or transparent background."
        ])
        
        logo_prompt = " ".join(prompt_parts)
        
        logger.info(
            "DALL-E generate logo with text",
            business_name=business_name,
            style=style
        )
        
        return await self.generate_image(
            prompt=logo_prompt,
            size=kwargs.get("size", "1024x1024"),
            quality=kwargs.get("quality", "hd")
        )
