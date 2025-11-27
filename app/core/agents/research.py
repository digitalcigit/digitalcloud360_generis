import structlog
from app.core.integrations.tavily import TavilyClient
from app.utils.exceptions import AgentException

logger = structlog.get_logger(__name__)

class ResearchAgent:
    """
    Agent spécialisé dans la recherche et l'analyse de marché en utilisant Tavily.
    """
    def __init__(self):
        self.tavily_client = TavilyClient()
        logger.info("ResearchAgent initialized.")

    async def run(self, company_description: str, market_focus: str) -> dict:
        """
        Exécute la recherche de marché et l'analyse des concurrents.

        Args:
            company_description: Description de l'entreprise du client.
            market_focus: Marché cible (ex: "e-commerce de mode au Sénégal").

        Returns:
            Un dictionnaire contenant les résultats de la recherche.
        """
        try:
            logger.info(
                "Running market research...",
                company_description=company_description,
                market_focus=market_focus
            )
            
            # 1. Recherche de marché générale
            market_research = await self.tavily_client.search_market(
                query=f"Analyse du marché pour {market_focus} en Afrique",
                topic="market_analysis"
            )
            
            # 2. Analyse des concurrents
            competitor_analysis = await self.tavily_client.analyze_competitors(
                query=f"Concurrents principaux pour {market_focus}",
                company_description=company_description
            )
            
            logger.info("Market research and competitor analysis completed successfully.")
            
            return {
                "market_research": market_research,
                "competitor_analysis": competitor_analysis
            }

        except Exception as e:
            logger.error("Error during research agent execution", error=str(e))
            raise AgentException(
                message="Failed to execute market research.",
                error_code="RESEARCH_AGENT_ERROR",
                details={"error": str(e)}
            )