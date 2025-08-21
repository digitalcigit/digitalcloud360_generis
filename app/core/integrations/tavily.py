from tavily import TavilyClient as TavilySDK
from typing import Dict, Any, List
import structlog
from app.config.settings import settings

logger = structlog.get_logger()

class TavilyClient:
    """Client Tavily pour recherche marché africain"""
    
    def __init__(self):
        if not settings.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY is not set in the environment variables.")
        self.client = TavilySDK(api_key=settings.TAVILY_API_KEY)
    
    async def search_market(self, query: str, location: str = "Africa") -> List[Dict[str, Any]]:
        """Recherche marché avec spécialisation Afrique"""
        try:
            search_query = f"{query} in {location}"
            logger.info("Performing market search with Tavily", query=search_query)
            response = await self.client.search(query=search_query, search_depth="advanced")
            logger.info("Successfully performed market search", query=search_query)
            return response['results']
        except Exception as e:
            logger.error("Tavily market search failed", query=query, location=location, error=str(e))
            # Fallback to an empty list if the API fails
            return []
    
    async def analyze_competitors(self, business_sector: str, location: str) -> Dict[str, Any]:
        """Analyse concurrence locale"""
        try:
            query = f"competitors of {business_sector} in {location}"
            logger.info("Performing competitor analysis with Tavily", query=query)
            response = await self.client.search(query=query, search_depth="advanced")
            logger.info("Successfully performed competitor analysis", query=query)
            return {"analysis": response['results']}
        except Exception as e:
            logger.error(
                "Tavily competitor analysis failed", 
                business_sector=business_sector, 
                location=location, 
                error=str(e)
            )
            return {"error": "Failed to analyze competitors."}