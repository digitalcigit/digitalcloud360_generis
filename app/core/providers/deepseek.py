"""
Deepseek LLM Provider - Primary LLM for Genesis AI
Deepseek-V3 optimisé pour génération contenu et analyse
"""

import httpx
import json
import structlog
from typing import Dict, Any, Optional

from .base import BaseLLMProvider

logger = structlog.get_logger(__name__)


class DeepseekProvider(BaseLLMProvider):
    """
    Provider Deepseek pour génération LLM
    
    Modèles supportés:
    - deepseek-chat (recommandé)
    - deepseek-coder (code generation)
    
    Avantages:
    - Performant pour tâches francophones
    - Coût optimisé vs GPT-4
    - Latence acceptable
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        timeout: int = 30,
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
            "DeepseekProvider initialized",
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
        Génère une réponse textuelle via Deepseek API
        
        Args:
            prompt: Le prompt utilisateur
            system_message: Message système optionnel
            temperature: Température de génération (0.0-2.0)
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
        
        # Merge avec kwargs additionnels (top_p, frequency_penalty, etc.)
        payload.update(kwargs)
        
        logger.info(
            "Deepseek generate request",
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
                    logger.error("Deepseek rate limit exceeded")
                    raise Exception("Deepseek API rate limit - retry later")
                
                elif response.status_code == 503:
                    logger.error("Deepseek service unavailable")
                    raise Exception("Deepseek API unavailable - use fallback")
                
                elif response.status_code != 200:
                    logger.error(
                        "Deepseek API error",
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise Exception(f"Deepseek API error: {response.status_code}")
                
                # Parse réponse
                result = response.json()
                
                if not result.get("choices"):
                    logger.error("No choices in Deepseek response", result=result)
                    raise Exception("Invalid Deepseek response format")
                
                generated_text = result["choices"][0]["message"]["content"]
                
                logger.info(
                    "Deepseek generate success",
                    response_length=len(generated_text),
                    tokens_used=result.get("usage", {}).get("total_tokens", 0)
                )
                
                return generated_text
                
        except httpx.TimeoutException:
            logger.error("Deepseek request timeout", timeout=self.timeout)
            raise Exception(f"Deepseek timeout after {self.timeout}s")
        
        except httpx.RequestError as e:
            logger.error("Deepseek network error", error=str(e))
            raise Exception(f"Deepseek network error: {str(e)}")
    
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère une réponse structurée JSON via Deepseek
        
        Args:
            prompt: Le prompt utilisateur
            response_schema: Schéma de réponse attendu (utilisé dans system message)
            system_message: Message système optionnel
            
        Returns:
            Dict: Réponse structurée parsée
            
        Note:
            Deepseek ne supporte pas JSON mode natif comme OpenAI,
            on force via instructions dans le system message
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
        
        logger.info("Deepseek generate_structured request")
        
        # Appeler generate normal avec instructions JSON
        response_text = await self.generate(
            prompt=prompt,
            system_message=full_system_message,
            temperature=kwargs.get("temperature", 0.3),  # Plus bas pour structured
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
            
            logger.info("Deepseek structured response parsed successfully")
            
            return structured_response
            
        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse Deepseek structured response",
                error=str(e),
                response_text=response_text[:500]
            )
            raise Exception(f"Invalid JSON in Deepseek response: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        Vérifie la disponibilité de Deepseek API
        
        Returns:
            bool: True si API accessible
        """
        
        logger.info("Deepseek health check")
        
        try:
            # Test simple avec prompt minimal
            test_response = await self.generate(
                prompt="Hello",
                system_message="Reply with 'OK'",
                max_tokens=10,
                temperature=0.0
            )
            
            is_healthy = len(test_response) > 0
            
            logger.info("Deepseek health check result", healthy=is_healthy)
            
            return is_healthy
            
        except Exception as e:
            logger.warning("Deepseek health check failed", error=str(e))
            return False
