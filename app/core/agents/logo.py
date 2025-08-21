import structlog
from app.core.integrations.logoai import LogoAIClient # Assumes a LogoAI client exists
from app.utils.exceptions import AgentException

logger = structlog.get_logger(__name__)

class LogoAgent:
    """
    Agent spécialisé dans la création de logos en utilisant un service externe.
    """
    def __init__(self):
        self.logo_client = LogoAIClient()
        logger.info("LogoAgent initialized.")

    async def run(self, company_name: str, company_slogan: str = None) -> dict:
        """
        Génère un logo pour l'entreprise.

        Args:
            company_name: Le nom de l'entreprise.
            company_slogan: Le slogan de l'entreprise (optionnel).

        Returns:
            Un dictionnaire contenant l'URL du logo généré.
        """
        try:
            logger.info("Generating logo...", company_name=company_name)
            
            logo_result = await self.logo_client.generate_logo(
                company_name=company_name,
                slogan=company_slogan
            )
            
            logger.info("Logo generated successfully.", logo_url=logo_result.get("logo_url"))
            
            return logo_result

        except Exception as e:
            logger.error("Error during logo agent execution", error=str(e))
            raise AgentException(
                "LOGO_AGENT_ERROR",
                "Failed to generate logo.",
                details=str(e)
            )