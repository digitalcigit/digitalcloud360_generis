import os
import structlog
from openai import AsyncOpenAI
from app.utils.exceptions import IntegrationException

logger = structlog.get_logger(__name__)

class OpenAIClient:
    """
    Client pour interagir avec l'API OpenAI.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables.")
            raise IntegrationException("OpenAI API key is not configured.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        logger.info("OpenAIClient initialized.")

    async def generate_text(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """
        Génère du texte en utilisant le modèle GPT d'OpenAI.

        Args:
            prompt: Le prompt pour la génération de texte.
            max_tokens: Le nombre maximum de tokens à générer.
            temperature: La température pour la génération.

        Returns:
            Le texte généré.
        """
        try:
            logger.info("Generating text with OpenAI...", prompt=prompt)
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            logger.info("Text generated successfully with OpenAI.")
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Error during OpenAI text generation", error=str(e))
            raise IntegrationException("Failed to generate text with OpenAI.", details=str(e))