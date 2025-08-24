"""Client Tavily pour recherche marché africain"""

import httpx
from typing import Dict, Any, List, Optional
import structlog
from app.config.settings import settings

logger = structlog.get_logger()

class TavilyClient:
    """Client Tavily pour recherche marché africain"""
    
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.base_url = settings.TAVILY_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def health_check(self) -> bool:
        """Vérifier connexion Tavily API"""
        try:
            if self.api_key == "your-tavily-key":
                logger.warning("Tavily API key not configured, using mock mode")
                return True  # Mode mock pour développement
                
            async with httpx.AsyncClient(timeout=30) as client:
                # Test simple de recherche pour vérifier la connexion
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json={
                        "query": "test",
                        "max_results": 1
                    }
                )
                
                if response.status_code == 200:
                    logger.info("Tavily API connection healthy")
                    return True
                else:
                    logger.warning("Tavily API health check failed", status_code=response.status_code)
                    return False
        except Exception as e:
            logger.error("Tavily API connection failed", error=str(e))
            return False
    
    async def search_market(self, query: str, location: str = "Africa", max_results: int = 10) -> List[Dict[str, Any]]:
        """Recherche marché avec spécialisation Afrique"""
        try:
            if self.api_key == "your-tavily-key":
                # Mode mock pour développement
                return self._mock_market_search(query, location)
            
            # Construire requête optimisée pour l'Afrique
            african_query = f"{query} {location} marché africain business opportunités"
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json={
                        "query": african_query,
                        "max_results": max_results,
                        "search_depth": "advanced",
                        "include_domains": [
                            "africa.com",
                            "africanews.com", 
                            "theafricareport.com",
                            "businessdayonline.com"
                        ]
                    }
                )
                
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    logger.info("Market search completed", 
                              query=query, location=location, results_count=len(results))
                    return results
                else:
                    logger.error("Market search failed", 
                               query=query, status_code=response.status_code)
                    return []
        except Exception as e:
            logger.error("Error in market search", query=query, error=str(e))
            return []
    
    async def analyze_competitors(self, business_sector: str, location: str) -> Dict[str, Any]:
        """Analyse concurrence locale"""
        try:
            if self.api_key == "your-tavily-key":
                return self._mock_competitor_analysis(business_sector, location)
            
            query = f"concurrents {business_sector} {location} analyse marché compétition"
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json={
                        "query": query,
                        "max_results": 15,
                        "search_depth": "advanced"
                    }
                )
                
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    
                    # Analyser les résultats pour extraire insights concurrence
                    competitors = []
                    market_insights = []
                    
                    for result in results:
                        competitors.append({
                            "name": result.get("title", ""),
                            "description": result.get("content", "")[:200],
                            "url": result.get("url", ""),
                            "relevance_score": result.get("score", 0)
                        })
                        
                        if any(keyword in result.get("content", "").lower() 
                              for keyword in ["prix", "tarif", "coût", "offre"]):
                            market_insights.append(result.get("content", "")[:300])
                    
                    analysis = {
                        "sector": business_sector,
                        "location": location,
                        "competitors_found": len(competitors),
                        "competitors": competitors[:10],  # Top 10
                        "market_insights": market_insights[:5],  # Top 5 insights
                        "analysis_timestamp": self._get_timestamp()
                    }
                    
                    logger.info("Competitor analysis completed", 
                              sector=business_sector, location=location, 
                              competitors_count=len(competitors))
                    return analysis
                else:
                    logger.error("Competitor analysis failed", 
                               sector=business_sector, status_code=response.status_code)
                    return self._empty_analysis(business_sector, location)
        except Exception as e:
            logger.error("Error in competitor analysis", 
                        sector=business_sector, error=str(e))
            return self._empty_analysis(business_sector, location)
    
    async def research_trends(self, business_sector: str, location: str = "Africa") -> Dict[str, Any]:
        """Recherche tendances sectorielles"""
        try:
            query = f"tendances {business_sector} {location} 2024 marché croissance innovation"
            
            if self.api_key == "your-tavily-key":
                return self._mock_trends_research(business_sector, location)
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json={
                        "query": query,
                        "max_results": 12,
                        "search_depth": "advanced"
                    }
                )
                
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    
                    trends = {
                        "sector": business_sector,
                        "location": location,
                        "trends": [
                            {
                                "title": result.get("title", ""),
                                "summary": result.get("content", "")[:250],
                                "source": result.get("url", ""),
                                "relevance": result.get("score", 0)
                            }
                            for result in results[:8]
                        ],
                        "analysis_timestamp": self._get_timestamp()
                    }
                    
                    logger.info("Trends research completed", 
                              sector=business_sector, location=location)
                    return trends
                else:
                    logger.error("Trends research failed", status_code=response.status_code)
                    return {"trends": [], "error": "API request failed"}
        except Exception as e:
            logger.error("Error in trends research", error=str(e))
            return {"trends": [], "error": str(e)}
    
    def _mock_market_search(self, query: str, location: str) -> List[Dict[str, Any]]:
        """Données mock pour développement"""
        return [
            {
                "title": f"Opportunités marché {query} en {location}",
                "content": f"Le marché de {query} en {location} présente des opportunités intéressantes avec une croissance estimée à 15% par an.",
                "url": "https://example.com/market-analysis",
                "score": 0.9
            },
            {
                "title": f"Analyse secteur {query} - {location}",
                "content": f"Le secteur {query} en {location} est en pleine expansion avec de nouveaux acteurs qui émergent régulièrement.",
                "url": "https://example.com/sector-analysis", 
                "score": 0.8
            }
        ]
    
    def _mock_competitor_analysis(self, sector: str, location: str) -> Dict[str, Any]:
        """Analyse concurrence mock"""
        return {
            "sector": sector,
            "location": location,
            "competitors_found": 3,
            "competitors": [
                {
                    "name": f"Leader {sector} {location}",
                    "description": f"Principal concurrent dans le secteur {sector}",
                    "url": "https://example-competitor.com",
                    "relevance_score": 0.9
                }
            ],
            "market_insights": [
                f"Le marché {sector} en {location} est dominé par 2-3 acteurs principaux"
            ],
            "analysis_timestamp": self._get_timestamp()
        }
    
    def _mock_trends_research(self, sector: str, location: str) -> Dict[str, Any]:
        """Recherche tendances mock"""
        return {
            "sector": sector,
            "location": location,
            "trends": [
                {
                    "title": f"Digitalisation du secteur {sector}",
                    "summary": f"Les entreprises de {sector} adoptent massivement les outils numériques",
                    "source": "https://example.com/trends",
                    "relevance": 0.8
                }
            ],
            "analysis_timestamp": self._get_timestamp()
        }
    
    def _empty_analysis(self, sector: str, location: str) -> Dict[str, Any]:
        """Retour vide en cas d'erreur"""
        return {
            "sector": sector,
            "location": location,
            "competitors_found": 0,
            "competitors": [],
            "market_insights": [],
            "analysis_timestamp": self._get_timestamp(),
            "error": "Analysis failed"
        }
    
    def _get_timestamp(self) -> str:
        """Timestamp actuel"""
        from datetime import datetime
        return datetime.utcnow().isoformat()