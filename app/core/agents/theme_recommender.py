"""
ThemeRecommendationAgent - Agent IA pour la recommandation de thèmes visuels
"""

import json
import structlog
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.core.providers.factory import ProviderFactory
from app.core.providers.base import BaseLLMProvider
from app.models.theme import Theme

logger = structlog.get_logger(__name__)

class ThemeRecommendation(BaseModel):
    """Résultat d'une recommandation pour un thème spécifique"""
    slug: str = Field(..., description="Slug du thème recommandé")
    match_score: float = Field(..., description="Score de pertinence entre 0 et 100")
    reasoning: str = Field(..., description="Justification de la recommandation en français")

class ThemeRecommendationResult(BaseModel):
    """Liste des recommandations ordonnées"""
    recommendations: List[ThemeRecommendation]


class ThemeRecommendationAgent:
    """Agent spécialisé dans le matching entre un brief business et les thèmes Genesis"""
    
    def __init__(self):
        from app.config.settings import settings
        
        self.provider_factory = ProviderFactory(api_keys=settings.get_provider_api_keys())
        self.llm_provider: BaseLLMProvider = self.provider_factory.create_llm_provider(
            plan="genesis_basic",
            override_provider="deepseek",
            override_model="deepseek-chat"
        )
        
        logger.info("ThemeRecommendationAgent initialized with Deepseek")

    async def recommend(self, brief_data: Dict[str, Any], themes: List[Theme]) -> List[ThemeRecommendation]:
        """
        Analyse le brief et recommande les thèmes les plus adaptés.
        
        Args:
            brief_data: Dictionnaire contenant les infos du brief (sector, vision, passion, etc.)
            themes: Liste des thèmes disponibles en base
            
        Returns:
            Liste de ThemeRecommendation ordonnée par score décroissant
        """
        
        # Préparer la liste des thèmes pour le prompt
        themes_context = []
        for t in themes:
            themes_context.append({
                "slug": t.slug,
                "name": t.name,
                "category": t.category,
                "description": t.description,
                "tags": t.compatibility_tags
            })

        system_message = """Tu es l'Expert Design de Genesis AI. 
Ton rôle est d'analyser le brief d'un entrepreneur et de recommander les thèmes visuels les plus adaptés parmi une liste fournie.
Tu dois évaluer la pertinence sémantique entre le secteur, la vision, et les tags/descriptions des thèmes.
RÉPONDS TOUJOURS EN JSON VALIDE."""

        prompt = f"""
ANALYSE DE RECOMMANDATION DE THÈME

DONNÉES DU BRIEF:
{json.dumps(brief_data, indent=2, ensure_ascii=False)}

THÈMES DISPONIBLES:
{json.dumps(themes_context, indent=2, ensure_ascii=False)}

TÂCHE:
1. Analyse le brief par rapport à chaque thème.
2. Attribue un score de matching (0 à 100) pour chaque thème.
3. Rédige une courte justification (reasoning) en français pour chaque recommandation, expliquant pourquoi ce thème correspond au business de l'utilisateur.
4. Ordonne les thèmes du plus pertinent au moins pertinent.

FORMAT JSON ATTENDU:
{{
    "recommendations": [
        {{
            "slug": "slug-du-theme",
            "match_score": 95.5,
            "reasoning": "La justification en français..."
        }},
        ...
    ]
}}

RÈGLES CRITIQUES:
- Un restaurant DOIT avoir un score très élevé (> 90%) pour le thème 'savor'.
- Un business technologique ou B2B doit préférer 'nova'.
- Le luxe ou l'esthétique haut de gamme doit préférer 'luxe'.
- Sois précis et professionnel dans tes justifications.
"""

        try:
            logger.info("requesting_theme_recommendations", theme_count=len(themes))
            
            response = await self.llm_provider.generate_structured(
                prompt=prompt,
                system_message=system_message,
                response_schema=ThemeRecommendationResult.model_json_schema(),
                temperature=0.2
            )
            
            # Valider et parser
            result = ThemeRecommendationResult(**response)
            
            # Trier par score par sécurité (même si demandé dans le prompt)
            sorted_recommendations = sorted(
                result.recommendations, 
                key=lambda x: x.match_score, 
                reverse=True
            )
            
            logger.info(
                "theme_recommendations_completed", 
                top_recommendation=sorted_recommendations[0].slug if sorted_recommendations else None,
                top_score=sorted_recommendations[0].match_score if sorted_recommendations else 0
            )
            
            return sorted_recommendations

        except Exception as e:
            logger.error("theme_recommendation_failed", error=str(e))
            # Fallback basique en cas d'erreur IA: score de 50 pour tous
            return [
                ThemeRecommendation(
                    slug=t.slug, 
                    match_score=50.0, 
                    reasoning="Recommandation par défaut suite à une erreur d'analyse."
                ) for t in themes[:3]
            ]
