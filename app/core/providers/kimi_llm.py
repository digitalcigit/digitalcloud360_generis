"""
Kimi LLM Provider - Alternative LLM pour Genesis AI
Moonshot AI (Kimi) pour génération contenu et analyse
"""

import httpx
import json
import structlog
from typing import Dict, Any, Optional

from .base import BaseLLMProvider

logger = structlog.get_logger(__name__)


class KimiLLMProvider(BaseLLMProvider):
    """
    Provider Kimi/Moonshot pour génération LLM
    
    Modèles supportés:
    - moonshot-v1-8k
    - moonshot-v1-32k
    - moonshot-v1-128k (recommandé - long contexte)
    
    Avantages:
    - 128K tokens de contexte
    - Performant pour tâches multilingues
    - Accès web natif (bonus)
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "moonshot-v1-128k",
        base_url: str = "https://api.moonshot.ai",
        timeout: int = 90,
        **kwargs
    ):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(
            "KimiLLMProvider initialized",
            model=model,
            base_url=base_url
        )
    
    async def generate(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Génère une réponse textuelle via Kimi API
        
        Args:
            prompt: Le prompt utilisateur
            system_message: Message système optionnel
            temperature: Température de génération (0.0-1.0)
            max_tokens: Nombre maximum de tokens
            
        Returns:
            str: Texte généré
            
        Raises:
            Exception: Si erreur API (429, 503, timeout)
        """
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        # Merge avec kwargs additionnels
        payload.update(kwargs)
        
        logger.info(
            "Kimi generate request",
            model=self.model,
            prompt_length=len(prompt),
            temperature=temperature
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                # Gestion erreurs HTTP
                if response.status_code == 429:
                    logger.error("Kimi rate limit exceeded")
                    raise Exception("Kimi API rate limit - retry later")
                
                elif response.status_code == 503:
                    logger.error("Kimi service unavailable")
                    raise Exception("Kimi API unavailable - use fallback")
                
                elif response.status_code != 200:
                    logger.error(
                        "Kimi API error",
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise Exception(f"Kimi API error: {response.status_code}")
                
                # Parse réponse
                result = response.json()
                
                if not result.get("choices"):
                    logger.error("No choices in Kimi response", result=result)
                    raise Exception("Invalid Kimi response format")
                
                generated_text = result["choices"][0]["message"]["content"]
                
                logger.info(
                    "Kimi generate success",
                    response_length=len(generated_text),
                    tokens_used=result.get("usage", {}).get("total_tokens", 0)
                )
                
                return generated_text
                
        except httpx.TimeoutException:
            logger.error("Kimi request timeout", timeout=self.timeout)
            raise Exception(f"Kimi timeout after {self.timeout}s")
        
        except httpx.RequestError as e:
            logger.error("Kimi network error", error=str(e))
            raise Exception(f"Kimi network error: {str(e)}")
    
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère une réponse structurée JSON via Kimi
        
        Args:
            prompt: Le prompt utilisateur
            response_schema: Schéma de réponse attendu
            system_message: Message système optionnel
            
        Returns:
            Dict: Réponse structurée parsée
        """
        
        # Construire system message avec schéma JSON
        schema_instruction = f"""
Tu dois répondre UNIQUEMENT avec un JSON valide respectant ce schéma:

{json.dumps(response_schema, indent=2, ensure_ascii=False)}

IMPORTANT:
- Réponds UNIQUEMENT avec le JSON, sans texte avant/après
- Respecte exactement le schéma fourni
- Utilise des doubles quotes pour les strings
"""
        
        full_system_message = f"{system_message}\n\n{schema_instruction}" if system_message else schema_instruction
        
        logger.info("Kimi generate_structured request")
        
        # Appeler generate normal avec instructions JSON
        response_text = await self.generate(
            prompt=prompt,
            system_message=full_system_message,
            temperature=kwargs.get("temperature", 0.3),
            max_tokens=kwargs.get("max_tokens", 3000)
        )
        
        # Parser JSON de la réponse
        try:
            # Nettoyer markdown code blocks si présents
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            structured_response = json.loads(cleaned_text)
            
            logger.info("Kimi structured response parsed successfully")
            
            return structured_response
            
        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse Kimi structured response",
                error=str(e),
                response_text=response_text[:500]
            )
            raise Exception(f"Invalid JSON in Kimi response: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        Vérifie la disponibilité de Kimi API
        
        Returns:
            bool: True si API accessible
        """
        
        logger.info("Kimi health check")
        
        try:
            test_response = await self.generate(
                prompt="Hello",
                system_message="Reply with 'OK'",
                max_tokens=10,
                temperature=0.0
            )
            
            is_healthy = len(test_response) > 0
            
            logger.info("Kimi health check result", healthy=is_healthy)
            
            return is_healthy
            
        except Exception as e:
            logger.warning("Kimi health check failed", error=str(e))
            return False
