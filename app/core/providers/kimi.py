"""
Kimi/Moonshot Search Provider - Web Search avec LLM natif
Moonshot AI (Kimi) avec capacités de recherche web intégrées
"""

import httpx
import json
import structlog
from typing import Dict, Any, List, Optional

from .base import BaseSearchProvider

logger = structlog.get_logger(__name__)


class KimiProvider(BaseSearchProvider):
    """
    Provider Kimi/Moonshot pour recherche web + analyse LLM
    
    Modèles supportés:
    - moonshot-v1-8k (recommandé pour search)
    - moonshot-v1-32k (longue analyse)
    - moonshot-v1-128k (contexte massif)
    
    Avantages:
    - LLM avec accès web natif (pas besoin API search séparée)
    - Combine search + analyse en un seul appel
    - Optimisé pour marché chinois/asiatique (peut aider Afrique)
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "moonshot-v1-8k",
        base_url: str = "https://api.moonshot.cn",
        timeout: int = 45,
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
            "KimiProvider initialized",
            model=model,
            base_url=base_url
        )
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Recherche web via Kimi avec analyse LLM intégrée
        
        Args:
            query: Requête de recherche
            max_results: Nombre max résultats (ignoré, Kimi decide)
            search_depth: Profondeur (basic/advanced)
            include_domains: Domaines à inclure (hint dans prompt)
            exclude_domains: Domaines à exclure (hint dans prompt)
            
        Returns:
            Dict contenant:
                - results: Liste résultats web analysés
                - query: Requête originale
                - search_metadata: Métadonnées
                - llm_analysis: Analyse LLM des résultats (bonus Kimi)
                
        Note:
            Kimi n'a pas d'API search dédiée, on utilise son LLM
            avec instructions de recherche web dans le prompt
        """
        
        # Construire prompt de recherche avec instructions
        search_prompt = self._build_search_prompt(
            query=query,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            search_depth=search_depth
        )
        
        logger.info(
            "Kimi search request",
            query=query,
            search_depth=search_depth,
            include_domains=include_domains
        )
        
        try:
            # Appel LLM Kimi avec web search enabled
            messages = [
                {
                    "role": "system",
                    "content": "Tu es un assistant de recherche web expert. Tu utilises ta capacité de recherche web pour trouver des informations actuelles et pertinentes."
                },
                {
                    "role": "user",
                    "content": search_prompt
                }
            ]
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,  # Plus bas pour recherche factuelle
                "max_tokens": 4000,
                # Kimi specific: enable web search
                "tools": [{
                    "type": "web_search",
                    "web_search": {
                        "search_query": query
                    }
                }]
            }
            
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
                    raise Exception("Kimi API unavailable - use Tavily fallback")
                
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
                
                llm_response = result["choices"][0]["message"]["content"]
                
                # Parser les résultats de recherche depuis la réponse LLM
                # Kimi retourne analyse textuelle, on la structure
                parsed_results = self._parse_llm_search_results(llm_response, query)
                
                logger.info(
                    "Kimi search success",
                    results_count=len(parsed_results["results"]),
                    tokens_used=result.get("usage", {}).get("total_tokens", 0)
                )
                
                return {
                    "results": parsed_results["results"],
                    "query": query,
                    "search_metadata": {
                        "provider": "kimi",
                        "model": self.model,
                        "search_depth": search_depth,
                        "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                    },
                    "llm_analysis": llm_response  # Bonus: analyse complète LLM
                }
                
        except httpx.TimeoutException:
            logger.error("Kimi request timeout", timeout=self.timeout)
            raise Exception(f"Kimi timeout after {self.timeout}s")
        
        except httpx.RequestError as e:
            logger.error("Kimi network error", error=str(e))
            raise Exception(f"Kimi network error: {str(e)}")
    
    async def analyze_market(
        self,
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyse marché spécialisée via recherche web Kimi
        
        Args:
            business_context: Contexte business (secteur, localisation, etc.)
            
        Returns:
            Dict contenant:
                - market_size: Taille marché estimée
                - competitors: Liste concurrents
                - opportunities: Opportunités identifiées
                - pricing_insights: Insights tarifaires
                - trends: Tendances marché
        """
        
        sector = business_context.get('industry_sector', 'business')
        location = business_context.get('location', {})
        country = location.get('country', 'Afrique')
        city = location.get('city', '')
        
        # Construire query de recherche marché
        market_query = f"analyse marché {sector} {city} {country} concurrents tendances opportunités 2024-2025"
        
        logger.info(
            "Kimi market analysis",
            sector=sector,
            country=country,
            query=market_query
        )
        
        # Prompt spécialisé analyse marché
        analysis_prompt = f"""
Effectue une analyse de marché approfondie pour:

CONTEXTE BUSINESS:
- Secteur: {sector}
- Localisation: {city}, {country}
- Marché cible: {business_context.get('target_market', 'Non spécifié')}

RECHERCHE WEB REQUISE:
1. Recherche concurrents locaux et régionaux
2. Taille et croissance du marché
3. Tendances secteur 2024-2025
4. Données pricing si disponibles
5. Opportunités business inexploitées

FOCUS GÉOGRAPHIQUE:
- Prioriser sources africaines et francophones
- Inclure contexte économique local
- Identifier spécificités culturelles/réglementaires

FORMAT RÉPONSE (JSON):
{{
    "market_size": {{"estimated_value": "...", "growth_rate": "...", "maturity": "..."}},
    "competitors": [{{"name": "...", "market_share": "...", "strengths": [...]}}],
    "opportunities": ["...", "..."],
    "pricing": {{"range": "...", "positioning": "..."}},
    "trends": ["...", "..."],
    "risks": ["...", "..."]
}}
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Tu es un expert en analyse de marché pour l'Afrique francophone. Utilise tes capacités de recherche web pour obtenir des données actuelles."
                },
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ]
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 4000,
                "tools": [{
                    "type": "web_search",
                    "web_search": {
                        "search_query": market_query
                    }
                }]
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error("Kimi market analysis failed", status_code=response.status_code)
                    raise Exception(f"Kimi API error: {response.status_code}")
                
                result = response.json()
                llm_response = result["choices"][0]["message"]["content"]
                
                # Parser JSON de l'analyse
                market_analysis = self._parse_market_analysis(llm_response)
                
                logger.info("Kimi market analysis success")
                
                return market_analysis
                
        except Exception as e:
            logger.error("Kimi market analysis failed", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        """
        Vérifie disponibilité Kimi API
        
        Returns:
            bool: True si API accessible
        """
        
        logger.info("Kimi health check")
        
        try:
            # Test simple search
            test_result = await self.search(
                query="test API health check",
                max_results=1,
                search_depth="basic"
            )
            
            is_healthy = len(test_result.get("results", [])) >= 0
            
            logger.info("Kimi health check result", healthy=is_healthy)
            
            return is_healthy
            
        except Exception as e:
            logger.warning("Kimi health check failed", error=str(e))
            return False
    
    # ============================================================
    # MÉTHODES PRIVÉES
    # ============================================================
    
    def _build_search_prompt(
        self,
        query: str,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        search_depth: str = "basic"
    ) -> str:
        """Construit prompt de recherche optimisé"""
        
        prompt = f"Recherche web: {query}\n\n"
        
        if include_domains:
            prompt += f"Prioriser ces sources: {', '.join(include_domains)}\n"
        
        if exclude_domains:
            prompt += f"Exclure ces sources: {', '.join(exclude_domains)}\n"
        
        if search_depth == "advanced":
            prompt += "\nEffectue une recherche approfondie avec analyse détaillée.\n"
        
        prompt += """
Retourne les résultats sous forme structurée:
- Titre de chaque source
- URL
- Extrait pertinent
- Pertinence au sujet

Focus sur sources récentes et fiables.
"""
        
        return prompt
    
    def _parse_llm_search_results(self, llm_response: str, query: str) -> Dict[str, Any]:
        """
        Parse réponse LLM Kimi pour extraire résultats de recherche
        
        Kimi retourne texte analysé, on extrait structure
        """
        
        # Tentative parsing JSON si présent
        try:
            # Nettoyer markdown code blocks
            cleaned = llm_response.strip()
            if "```json" in cleaned:
                json_start = cleaned.find("```json") + 7
                json_end = cleaned.find("```", json_start)
                cleaned = cleaned[json_start:json_end].strip()
            
            parsed = json.loads(cleaned)
            
            if "results" in parsed:
                return parsed
            
        except json.JSONDecodeError:
            pass
        
        # Fallback: créer structure basique depuis texte
        # En production, améliorer parsing avec regex/NLP
        return {
            "results": [
                {
                    "title": f"Analyse Kimi: {query}",
                    "url": "https://kimi.moonshot.cn",
                    "snippet": llm_response[:500],  # Premier 500 chars
                    "score": 0.8
                }
            ]
        }
    
    def _parse_market_analysis(self, llm_response: str) -> Dict[str, Any]:
        """Parse analyse marché depuis réponse LLM"""
        
        try:
            # Nettoyer et parser JSON
            cleaned = llm_response.strip()
            if "```json" in cleaned:
                json_start = cleaned.find("```json") + 7
                json_end = cleaned.find("```", json_start)
                cleaned = cleaned[json_start:json_end].strip()
            elif "```" in cleaned:
                json_start = cleaned.find("```") + 3
                json_end = cleaned.find("```", json_start)
                cleaned = cleaned[json_start:json_end].strip()
            
            analysis = json.loads(cleaned)
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Kimi market analysis JSON", error=str(e))
            
            # Fallback structure minimale
            return {
                "market_size": {"estimated_value": "Non disponible", "maturity": "unknown"},
                "competitors": [],
                "opportunities": ["Analyse textuelle disponible"],
                "pricing": {"range": "Non disponible"},
                "trends": [],
                "risks": [],
                "raw_analysis": llm_response  # Texte complet en fallback
            }
