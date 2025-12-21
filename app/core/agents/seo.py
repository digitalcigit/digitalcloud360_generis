import structlog
from typing import Dict, Any, List, Optional
from app.core.integrations.tavily import TavilyClient
from app.core.providers.deepseek import DeepseekProvider
from app.config.settings import settings
from app.utils.exceptions import AgentException

logger = structlog.get_logger(__name__)

class SeoAgent:
    """
    Agent spécialisé dans l'optimisation SEO intelligente.
    
    Features:
    - Recherche concurrentielle via Tavily
    - Analyse LLM (Deepseek) pour génération SEO optimisée
    - Mots-clés contextuels intelligents
    - Méta-tags professionnels
    - Structure headings recommandée
    """
    def __init__(self):
        self.tavily_client = TavilyClient()
        self.llm_provider = DeepseekProvider(
            api_key=settings.DEEPSEEK_API_KEY
        )
        logger.info("SeoAgent initialized with Deepseek LLM")

    async def run(
        self,
        business_name: str,
        business_description: str,
        industry_sector: str,
        target_location: Optional[Dict[str, str]] = None,
        unique_value_proposition: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère un package SEO complet via LLM + recherche concurrentielle.

        Args:
            business_name: Nom de l'entreprise.
            business_description: Description métier.
            industry_sector: Secteur d'activité.
            target_location: Dict avec country, city (optionnel).
            unique_value_proposition: Proposition de valeur unique (optionnel).

        Returns:
            Dict contenant:
                - primary_keywords: Liste mots-clés primaires
                - secondary_keywords: Liste mots-clés secondaires
                - meta_title: Titre SEO optimisé (50-60 chars)
                - meta_description: Description SEO (150-160 chars)
                - heading_structure: Structure H1/H2/H3 recommandée
                - local_seo: Infos SEO local si location fournie
        """
        try:
            # 1. Recherche concurrentielle via Tavily
            location_str = ""
            if target_location:
                country = target_location.get("country", "")
                city = target_location.get("city", "")
                location_str = f"{city}, {country}" if city else country
            
            search_query = f"SEO {industry_sector} {location_str}".strip()
            
            logger.info(
                "SEO Agent: Starting competitive research",
                business_name=business_name,
                industry=industry_sector,
                location=location_str
            )
            
            competitive_data = await self.tavily_client.search_market(
                query=search_query
            )
            
            # 2. Générer SEO optimisé via LLM
            seo_prompt = self._build_seo_prompt(
                business_name=business_name,
                business_description=business_description,
                industry_sector=industry_sector,
                location=location_str,
                unique_value_proposition=unique_value_proposition,
                competitive_insights=competitive_data
            )
            
            logger.info("SEO Agent: Generating optimized SEO via Deepseek LLM")
            
            seo_result = await self.llm_provider.generate_structured(
                prompt=seo_prompt,
                response_schema={
                    "primary_keywords": "array of 3-5 most important keywords",
                    "secondary_keywords": "array of 5-8 supporting keywords",
                    "meta_title": "string (50-60 characters)",
                    "meta_description": "string (150-160 characters)",
                    "heading_structure": {
                        "h1": "string (main page title)",
                        "h2_sections": "array of 3-5 section headings"
                    },
                    "local_seo": {
                        "optimized_for": "string (location)",
                        "local_keywords": "array (if applicable)"
                    }
                }
            )
            
            # 3. Enrichir avec métadonnées agent
            enriched_result = {
                **seo_result,
                "metadata": {
                    "agent": "SeoAgent",
                    "business_name": business_name,
                    "industry": industry_sector,
                    "location": location_str,
                    "competitive_sources": len(competitive_data) if isinstance(competitive_data, list) else 0,
                    "llm_provider": "deepseek"
                }
            }
            
            logger.info(
                "SEO data generated successfully",
                primary_keywords_count=len(enriched_result.get("primary_keywords", [])),
                meta_title_length=len(enriched_result.get("meta_title", ""))
            )
            
            return enriched_result

        except Exception as e:
            logger.error(
                "Error during SEO agent execution",
                error=str(e),
                business_name=business_name
            )
            
            # Fallback: retourner SEO minimal
            return self._get_fallback_seo(
                business_name=business_name,
                business_description=business_description,
                industry_sector=industry_sector,
                error=str(e)
            )
    
    def _build_seo_prompt(
        self,
        business_name: str,
        business_description: str,
        industry_sector: str,
        location: str,
        unique_value_proposition: Optional[str],
        competitive_insights: Dict[str, Any]
    ) -> str:
        """
        Construit prompt optimisé pour génération SEO via LLM.
        """
        prompt_parts = [
            "Tu es un expert SEO spécialisé dans l'optimisation pour les moteurs de recherche.",
            f"\nEntreprise: {business_name}",
            f"Secteur: {industry_sector}",
            f"Description: {business_description}"
        ]
        
        if location:
            prompt_parts.append(f"Localisation: {location}")
        
        if unique_value_proposition:
            prompt_parts.append(f"Proposition de valeur: {unique_value_proposition}")
        
        # Ajouter insights concurrentiels
        if competitive_insights and isinstance(competitive_insights, list) and len(competitive_insights) > 0:
            prompt_parts.append("\nAnalyse concurrentielle disponible (utilise ces données pour affiner le SEO).")
        
        prompt_parts.extend([
            "\nGénère un package SEO complet et optimisé:",
            "1. Mots-clés primaires (3-5): Termes essentiels à fort volume",
            "2. Mots-clés secondaires (5-8): Termes longue traîne",
            "3. Meta title (50-60 chars): Accrocheur, avec mot-clé principal",
            "4. Meta description (150-160 chars): Call-to-action + bénéfices",
            "5. Structure headings: H1 principal + 3-5 H2 pour sections",
            "6. SEO local si localisation fournie",
            "\nRespects les best practices SEO 2025 et Google guidelines."
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_fallback_seo(
        self,
        business_name: str,
        business_description: str,
        industry_sector: str,
        error: str
    ) -> Dict[str, Any]:
        """
        Retourne SEO minimal si LLM échoue.
        """
        # SEO basique généré sans LLM
        truncated_desc = business_description[:150]
        
        return {
            "primary_keywords": [industry_sector, business_name.lower()],
            "secondary_keywords": ["services", "professional", "quality"],
            "meta_title": f"{business_name} - {industry_sector}",
            "meta_description": f"{truncated_desc}...",
            "heading_structure": {
                "h1": business_name,
                "h2_sections": ["Our Services", "About Us", "Contact"]
            },
            "local_seo": {
                "optimized_for": "",
                "local_keywords": []
            },
            "metadata": {
                "agent": "SeoAgent",
                "business_name": business_name,
                "industry": industry_sector,
                "fallback": True,
                "error": error,
                "message": "LLM SEO generation failed, using basic fallback"
            }
        }