import structlog
from app.core.integrations.tavily import TavilyClient
from app.utils.exceptions import AgentException

logger = structlog.get_logger(__name__)

class SeoAgent:
    """
    Agent spécialisé dans l'optimisation pour les moteurs de recherche (SEO).
    """
    def __init__(self):
        self.tavily_client = TavilyClient()
        logger.info("SeoAgent initialized.")

    async def run(self, company_description: str, market_focus: str) -> dict:
        """
        Génère des mots-clés et des méta-descriptions pour le SEO.

        Args:
            company_description: Description de l'entreprise.
            market_focus: Marché cible.

        Returns:
            Un dictionnaire contenant les mots-clés et la méta-description.
        """
        try:
            logger.info("Generating SEO data...", market_focus=market_focus)
            
            # Recherche de mots-clés pertinents
            keywords_research = await self.tavily_client.search_market(
                query=f"SEO keywords for {market_focus}",
                topic="seo_keywords"
            )
            
            # Génération de la méta-description (simulée, pourrait utiliser un LLM)
            meta_description = self._generate_meta_description(company_description, keywords_research)
            
            logger.info("SEO data generated successfully.")
            
            return {
                "keywords": keywords_research.get("keywords", []),
                "meta_description": meta_description
            }

        except Exception as e:
            logger.error("Error during SEO agent execution", error=str(e))
            raise AgentException(
                "SEO_AGENT_ERROR",
                "Failed to generate SEO data.",
                details=str(e)
            )

    def _generate_meta_description(self, description: str, keywords_data: dict) -> str:
        """Génère une méta-description concise."""
        top_keywords = ", ".join(keywords_data.get("keywords", [])[:3])
        return f"{description[:120]}... | Mots-clés: {top_keywords}"