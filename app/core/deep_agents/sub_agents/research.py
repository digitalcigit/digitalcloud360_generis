"""
Research Sub-Agent - Analyse Marché et Concurrence Automatisée

Spécialisé pour l'Afrique francophone avec:
- Recherche web via Tavily/Kimi
- Analyse concurrence locale
- Estimation taille marché
- Identification opportunités sectorielles
- Insights tarifaires
"""

import asyncio
import json
import structlog
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.core.providers.factory import ProviderFactory
from app.core.providers.base import BaseSearchProvider, BaseLLMProvider
from app.utils.exceptions import AgentException

logger = structlog.get_logger(__name__)


class ResearchSubAgent:
    """
    Sous-agent recherche marché/concurrence spécialisé Afrique francophone.
    
    Utilise l'architecture multi-provider pour:
    - Recherche web (Tavily primary, Kimi fallback)
    - Analyse LLM (Deepseek primary, OpenAI fallback)
    """
    
    def __init__(self):
        """Initialise le sub-agent avec providers configurés"""
        self.provider_factory = ProviderFactory()
        
        # Providers search (Tavily primary)
        self.search_provider: BaseSearchProvider = self.provider_factory.get_search_provider()
        
        # Providers LLM (Deepseek primary pour analyse)
        self.llm_provider: BaseLLMProvider = self.provider_factory.get_llm_provider(
            provider_name="deepseek",
            fallback=True
        )
        
        # Domaines africains prioritaires pour recherche
        self.african_domains = [
            "africanentrepreneur.com",
            "businessafrica.net",
            "entrepreneurafrique.com",
            "lesechos.fr",
            "jeune-afrique.com",
            "afrik.com",
            "africaintelligence.fr"
        ]
        
        logger.info("ResearchSubAgent initialized with multi-provider architecture")
    
    async def analyze_market(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse marché automatisée complète avec focus Afrique francophone.
        
        Args:
            business_context: Contexte business contenant:
                - business_name: Nom de l'entreprise
                - industry_sector: Secteur d'activité
                - location: {country, city, region}
                - target_market: Marché cible
                - vision: Vision entreprise
                - mission: Mission entreprise
                
        Returns:
            Dict contenant:
                - market_size_estimation: Taille et potentiel marché
                - main_competitors: Top 5 concurrents identifiés
                - market_opportunities: Opportunités business
                - pricing_insights: Insights tarifaires secteur
                - differentiation_suggestions: Suggestions différenciation
                - cultural_insights: Facteurs culturels pertinents
                - risk_factors: Risques identifiés
                - success_factors: Clés de succès
        """
        
        logger.info(
            "Starting market analysis",
            business=business_context.get('business_name'),
            sector=business_context.get('industry_sector'),
            location=business_context.get('location')
        )
        
        try:
            # Recherche parallèle sources multiples
            search_tasks = [
                self._search_competitors(business_context),
                self._search_market_trends(business_context),
                self._search_pricing_data(business_context),
                self._search_opportunities(business_context)
            ]
            
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Filtrer erreurs et conserver résultats valides
            valid_results = [
                r for r in search_results 
                if not isinstance(r, Exception)
            ]
            
            if not valid_results:
                logger.warning("All search tasks failed, using fallback analysis")
                return await self._fallback_analysis(business_context)
            
            # Agrégation et analyse IA
            market_analysis = await self._analyze_with_llm(
                search_results=valid_results,
                business_context=business_context
            )
            
            logger.info(
                "Market analysis completed successfully",
                competitors_found=len(market_analysis.get('competitors', [])),
                opportunities_found=len(market_analysis.get('opportunities', []))
            )
            
            return {
                'market_size_estimation': market_analysis.get('market_size', {}),
                'main_competitors': market_analysis.get('competitors', [])[:5],
                'market_opportunities': market_analysis.get('opportunities', []),
                'pricing_insights': market_analysis.get('pricing', {}),
                'differentiation_suggestions': market_analysis.get('differentiators', []),
                'cultural_insights': market_analysis.get('cultural_factors', {}),
                'risk_factors': market_analysis.get('risks', []),
                'success_factors': market_analysis.get('success_keys', []),
                'search_metadata': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'sources_consulted': len(valid_results),
                    'search_failures': len(search_results) - len(valid_results)
                }
            }
            
        except Exception as e:
            logger.error("Market analysis failed", error=str(e), exc_info=True)
            # Fallback gracieux
            return await self._fallback_analysis(business_context)
    
    async def _search_competitors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recherche concurrents directs et indirects.
        
        Args:
            context: Contexte business
            
        Returns:
            Dict avec type 'competitors' et résultats recherche
        """
        try:
            location = context.get('location', {})
            sector = context.get('industry_sector', 'business')
            city = location.get('city', '')
            country = location.get('country', 'Afrique')
            
            query = f"concurrents {sector} {city} {country} marché entreprise"
            
            logger.info("Searching competitors", query=query)
            
            competitors_data = await self.search_provider.search(
                query=query,
                max_results=8,
                search_depth="advanced",
                include_domains=self.african_domains
            )
            
            return {
                'type': 'competitors',
                'data': competitors_data,
                'query': query,
                'context': context
            }
            
        except Exception as e:
            logger.warning("Competitor search failed", error=str(e))
            return {
                'type': 'competitors',
                'data': {},
                'error': str(e),
                'context': context
            }
    
    async def _search_market_trends(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recherche tendances marché secteur.
        
        Args:
            context: Contexte business
            
        Returns:
            Dict avec type 'trends' et résultats recherche
        """
        try:
            sector = context.get('industry_sector', 'business')
            country = context.get('location', {}).get('country', 'Afrique')
            
            query = f"tendances marché {sector} {country} francophone 2025 croissance"
            
            logger.info("Searching market trends", query=query)
            
            trends_data = await self.search_provider.search(
                query=query,
                max_results=5,
                search_depth="basic",
                include_domains=["statista.com", "mordorintelligence.com"] + self.african_domains
            )
            
            return {
                'type': 'trends',
                'data': trends_data,
                'query': query,
                'context': context
            }
            
        except Exception as e:
            logger.warning("Market trends search failed", error=str(e))
            return {
                'type': 'trends',
                'data': {},
                'error': str(e),
                'context': context
            }
    
    async def _search_pricing_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recherche données tarification secteur.
        
        Args:
            context: Contexte business
            
        Returns:
            Dict avec type 'pricing' et résultats recherche
        """
        try:
            sector = context.get('industry_sector', 'business')
            country = context.get('location', {}).get('country', 'Afrique')
            
            query = f"prix tarif {sector} {country} coût abonnement service"
            
            logger.info("Searching pricing data", query=query)
            
            pricing_data = await self.search_provider.search(
                query=query,
                max_results=6,
                search_depth="basic",
                exclude_domains=["wikipedia.org", "pinterest.com"]
            )
            
            return {
                'type': 'pricing',
                'data': pricing_data,
                'query': query,
                'context': context
            }
            
        except Exception as e:
            logger.warning("Pricing search failed", error=str(e))
            return {
                'type': 'pricing',
                'data': {},
                'error': str(e),
                'context': context
            }
    
    async def _search_opportunities(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recherche opportunités business inexploitées.
        
        Args:
            context: Contexte business
            
        Returns:
            Dict avec type 'opportunities' et résultats recherche
        """
        try:
            sector = context.get('industry_sector', 'business')
            
            query = f"opportunités business {sector} Afrique innovation startup"
            
            logger.info("Searching opportunities", query=query)
            
            opportunities_data = await self.search_provider.search(
                query=query,
                max_results=5,
                search_depth="basic"
            )
            
            return {
                'type': 'opportunities',
                'data': opportunities_data,
                'query': query,
                'context': context
            }
            
        except Exception as e:
            logger.warning("Opportunities search failed", error=str(e))
            return {
                'type': 'opportunities',
                'data': {},
                'error': str(e),
                'context': context
            }
    
    async def _analyze_with_llm(
        self, 
        search_results: List[Dict[str, Any]], 
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyse LLM sophistiquée des données marché avec prompt spécialisé.
        
        Args:
            search_results: Résultats de recherche agrégés
            business_context: Contexte business
            
        Returns:
            Dict avec analyse structurée marché
        """
        # Agrégation données par type
        all_data = {}
        for result in search_results:
            result_type = result.get('type', 'unknown')
            all_data[result_type] = result.get('data', {})
        
        location = business_context.get('location', {})
        
        analysis_prompt = f"""
ANALYSE MARCHÉ EXPERT - {business_context.get('industry_sector', 'SECTEUR').upper()} EN AFRIQUE FRANCOPHONE

CONTEXTE BUSINESS:
- Nom entreprise: {business_context.get('business_name', 'Non spécifié')}
- Secteur: {business_context.get('industry_sector', 'Non spécifié')}
- Localisation: {location.get('city', 'N/A')}, {location.get('country', 'Afrique')}
- Marché cible: {business_context.get('target_market', 'Non spécifié')}
- Vision: {business_context.get('vision', 'Non spécifié')}

DONNÉES RECHERCHE WEB:
{json.dumps(all_data, indent=2, ensure_ascii=False)[:4000]}

INSTRUCTIONS ANALYSE:
1. Analyser UNIQUEMENT les données fournies (pas d'invention)
2. Adapter analyse au contexte africain francophone
3. Identifier opportunités concrètes et réalisables
4. Estimer taille marché de manière conservative
5. Proposer axes différenciation culturellement pertinents
6. Considérer contraintes infrastructure locale
7. Évaluer risques spécifiques contexte africain

FORMAT RÉPONSE JSON STRICT:
{{
    "market_size": {{
        "estimation": "estimation en FCFA ou devise locale avec unité",
        "confidence_level": "haute/moyenne/faible",
        "growth_potential": "pourcentage croissance annuelle estimée",
        "market_maturity": "émergent/en croissance/mature",
        "market_segment": "segment marché principal"
    }},
    "competitors": [
        {{
            "name": "nom concurrent",
            "strengths": ["force 1", "force 2"],
            "weaknesses": ["faiblesse 1"],
            "market_share": "part marché estimée en %"
        }}
    ],
    "opportunities": [
        {{
            "opportunity": "description opportunité claire",
            "potential_impact": "faible/moyen/élevé",
            "difficulty": "facile/moyen/difficile",
            "timeframe": "court terme (0-6mois) / moyen terme (6-18mois) / long terme (18mois+)"
        }}
    ],
    "pricing": {{
        "average_price_range": "fourchette prix moyenne marché",
        "pricing_model": "modèle tarifaire dominant secteur",
        "price_sensitivity": "sensibilité prix clientèle (faible/moyenne/élevée)"
    }},
    "differentiators": [
        "axe différenciation pertinent 1",
        "axe différenciation pertinent 2",
        "axe différenciation pertinent 3"
    ],
    "cultural_factors": {{
        "key_values": ["valeur culturelle 1", "valeur culturelle 2"],
        "local_preferences": "préférences locales importantes",
        "trust_factors": "facteurs confiance spécifiques contexte"
    }},
    "risks": [
        "risque identifié 1",
        "risque identifié 2"
    ],
    "success_keys": [
        "facteur clé succès 1",
        "facteur clé succès 2",
        "facteur clé succès 3"
    ]
}}

GÉNÉRER ANALYSE MAINTENANT:
"""
        
        system_message = """Tu es un expert en analyse de marché spécialisé dans l'entrepreneuriat africain francophone avec 15 ans d'expérience. Tu produis des analyses pragmatiques, ancrées dans la réalité terrain, avec insights culturels pertinents. Tu réponds TOUJOURS en JSON valide."""
        
        try:
            # Génération avec provider LLM (Deepseek primary)
            response = await self.llm_provider.generate_structured(
                prompt=analysis_prompt,
                system_message=system_message,
                response_schema={
                    "market_size": "object",
                    "competitors": "array",
                    "opportunities": "array",
                    "pricing": "object",
                    "differentiators": "array",
                    "cultural_factors": "object",
                    "risks": "array",
                    "success_keys": "array"
                },
                temperature=0.3,  # Bas pour analyse factuelle
                max_tokens=2500
            )
            
            return response
            
        except Exception as e:
            logger.error("LLM analysis failed", error=str(e))
            # Fallback: analyse basique depuis données recherche
            return await self._fallback_llm_analysis(all_data, business_context)
    
    async def _fallback_analysis(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse fallback si recherches échouent.
        
        Retourne analyse générique basée sur secteur et localisation.
        """
        logger.warning("Using fallback market analysis")
        
        sector = business_context.get('industry_sector', 'services')
        location = business_context.get('location', {})
        country = location.get('country', 'Afrique')
        
        return {
            'market_size_estimation': {
                'estimation': 'Non disponible (données insuffisantes)',
                'confidence_level': 'faible',
                'growth_potential': 'Potentiel élevé marché africain',
                'market_maturity': 'émergent'
            },
            'main_competitors': [],
            'market_opportunities': [
                {
                    'opportunity': f'Marché {sector} en croissance en {country}',
                    'potential_impact': 'moyen',
                    'difficulty': 'moyen',
                    'timeframe': 'moyen terme'
                }
            ],
            'pricing_insights': {
                'average_price_range': 'Variable selon segment',
                'pricing_model': 'À définir selon positionnement',
                'price_sensitivity': 'élevée (marchés africains)'
            },
            'differentiation_suggestions': [
                'Service client personnalisé',
                'Adaptation culturelle forte',
                'Solutions accessibles financièrement'
            ],
            'cultural_insights': {
                'key_values': ['proximité', 'confiance', 'communauté'],
                'local_preferences': 'Préférence relations humaines',
                'trust_factors': 'Bouche-à-oreille, recommandations locales'
            },
            'risk_factors': [
                'Infrastructure technologique variable',
                'Pouvoir achat limité'
            ],
            'success_factors': [
                'Connaissance terrain local',
                'Réseau communautaire fort',
                'Flexibilité modèle économique'
            ],
            'fallback_mode': True
        }
    
    async def _fallback_llm_analysis(
        self, 
        search_data: Dict[str, Any], 
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyse fallback structurée si LLM primary échoue"""
        
        logger.warning("Using fallback LLM analysis structure")
        
        # Extraction basique données disponibles
        competitors_raw = search_data.get('competitors', {}).get('results', [])
        competitors = [
            {
                'name': c.get('title', 'Concurrent'),
                'strengths': ['Présence établie'],
                'weaknesses': ['Information limitée'],
                'market_share': 'Non disponible'
            }
            for c in competitors_raw[:3]
        ]
        
        return {
            'market_size': {
                'estimation': 'Données limitées',
                'confidence_level': 'faible',
                'growth_potential': 'Positif',
                'market_maturity': 'en croissance'
            },
            'competitors': competitors if competitors else [],
            'opportunities': [
                {
                    'opportunity': 'Marché en développement',
                    'potential_impact': 'moyen',
                    'difficulty': 'moyen',
                    'timeframe': 'moyen terme'
                }
            ],
            'pricing': {
                'average_price_range': 'Variable',
                'pricing_model': 'Flexible',
                'price_sensitivity': 'élevée'
            },
            'differentiators': [
                'Service personnalisé',
                'Adaptation locale'
            ],
            'cultural_factors': {
                'key_values': ['confiance', 'proximité'],
                'local_preferences': 'Relations directes',
                'trust_factors': 'Recommandations'
            },
            'risks': ['Données limitées pour analyse approfondie'],
            'success_keys': ['Connaissance terrain', 'Flexibilité'],
            'fallback_llm_mode': True
        }
