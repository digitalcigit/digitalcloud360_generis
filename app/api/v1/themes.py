"""
Themes endpoints for Genesis AI Service
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
import structlog
import json

from app.config.database import get_db
from app.api.v1.dependencies import get_redis_client
import redis.asyncio as redis
from app.models.user import User
from app.models.theme import Theme
from app.models.coaching import BusinessBrief, CoachingSession, SessionStatusEnum
from app.schemas.theme import (
    ThemeResponse, 
    ThemeRecommendationList, 
    ThemeRecommendationResponse,
    ThemeSelectRequest
)
from app.services.user_service import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

# For Recommendation and Generation
from app.core.agents.theme_recommender import ThemeRecommendationAgent
from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.services.transformer import BriefToSiteTransformer
from app.schemas.business_brief_data import BusinessBriefData

router = APIRouter()
logger = structlog.get_logger()

@router.get("/", response_model=List[ThemeResponse])
async def list_themes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste tous les thèmes actifs disponibles"""
    result = await db.execute(select(Theme).where(Theme.is_active == True))
    themes = result.scalars().all()
    return themes

@router.post("/recommend", response_model=ThemeRecommendationList)
async def recommend_themes(
    request: Dict[str, Any], # { "brief_id": int }
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Recommande les thèmes les plus adaptés pour un brief donné"""
    brief_id = request.get("brief_id")
    if not brief_id:
        raise HTTPException(status_code=400, detail="brief_id is required")

    # Security Check: Ensure brief belongs to current user
    result = await db.execute(
        select(BusinessBrief)
        .join(CoachingSession)
        .filter(BusinessBrief.id == brief_id)
        .filter(CoachingSession.user_id == current_user.id)
    )
    brief = result.scalars().first()
    
    if not brief:
        # Check if brief exists but belongs to another user (security ambiguity)
        # or doesn't exist at all. For security, we return 404 in both cases.
        raise HTTPException(status_code=404, detail="Brief not found or access denied")

    # Charger tous les thèmes
    themes_result = await db.execute(select(Theme).where(Theme.is_active == True))
    themes = themes_result.scalars().all()

    if not themes:
        logger.error("No active themes found in database")
        raise HTTPException(status_code=503, detail="No active themes available. Please contact support.")
    
    # Appeler l'agent de recommandation
    agent = ThemeRecommendationAgent()
    brief_data = {
        "business_name": brief.business_name,
        "industry_sector": brief.sector,
        "vision": brief.vision,
        "mission": brief.mission,
        "target_market": brief.target_audience,
        "competitive_advantage": brief.differentiation,
        "value_proposition": brief.value_proposition
    }
    
    recommendations = await agent.recommend(brief_data, themes)
    
    # Formater la réponse
    formatted_recs = []
    # Créer un dictionnaire pour accès rapide aux objets Theme
    theme_map = {t.slug: t for t in themes}
    
    for rec in recommendations:
        theme_obj = theme_map.get(rec.slug)
        if theme_obj:
            formatted_recs.append(
                ThemeRecommendationResponse(
                    theme=ThemeResponse.from_orm(theme_obj),
                    match_score=rec.match_score,
                    reasoning=rec.reasoning
                )
            )
            
    return ThemeRecommendationList(
        brief_id=brief.id,
        recommendations=formatted_recs
    )

@router.post("/select", status_code=status.HTTP_202_ACCEPTED)
async def select_theme_and_generate(
    request: ThemeSelectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Sélectionne un thème et lance la génération finale du site.
    """
    logger.info("theme_selected_triggering_generation", brief_id=request.brief_id, theme_id=request.theme_id)
    
    # 1. Security & Data Check: Ensure brief belongs to current user
    brief_result = await db.execute(
        select(BusinessBrief)
        .join(CoachingSession)
        .filter(BusinessBrief.id == request.brief_id)
        .filter(CoachingSession.user_id == current_user.id)
    )
    brief = brief_result.scalars().first()
    
    theme_result = await db.execute(select(Theme).filter(Theme.id == request.theme_id))
    theme = theme_result.scalars().first()
    
    if not brief or not theme:
        raise HTTPException(status_code=404, detail="Brief or Theme not found")

    # 2. Préparer l'orchestrateur avec le thème choisi
    # On récupère la session coaching liée
    session_result = await db.execute(select(CoachingSession).filter(CoachingSession.id == brief.coaching_session_id))
    coaching_session = session_result.scalars().first()
    
    if not coaching_session:
        raise HTTPException(status_code=404, detail="Coaching session not found")

    # On récupère les données de session depuis Redis car elles contiennent l'onboarding
    session_data_json = await redis_client.get(f"session:{coaching_session.session_id}")
    session_data = json.loads(session_data_json) if session_data_json else {}

    business_brief_dict = {
        "business_name": brief.business_name,
        "industry_sector": brief.sector,
        "vision": brief.vision,
        "mission": brief.mission,
        "target_market": brief.target_audience,
        "competitive_advantage": brief.differentiation,
        "value_proposition": brief.value_proposition,
        "location": brief.location or {"country": "Sénégal", "city": "Dakar"}
    }

    # 3. Exécuter l'orchestrateur LangGraph
    orchestrator = LangGraphOrchestrator()
    orchestration_result = await orchestrator.run({
        "user_id": current_user.id,
        "brief_id": coaching_session.session_id,
        "business_brief": business_brief_dict,
        "selected_theme_id": theme.id,
        "selected_theme_slug": theme.slug
    })
    
    # 4. Transformer en SiteDefinition avec injection du thème
    transformer = BriefToSiteTransformer()
    
    # GEN-WO-SAVOR-V2: Priorité au secteur de la DB (onboarding) sur celui de l'orchestrateur
    # L'orchestrateur peut échouer ou retourner un secteur par défaut, mais le secteur 
    # validé lors de l'onboarding est stocké dans brief.sector et doit prévaloir.
    resolved_sector = brief.sector or orchestration_result["business_brief"].get("industry_sector") or "default"
    
    logger.info("theme_generation_data", 
                brief_sector=brief.sector, 
                orchestrator_sector=orchestration_result["business_brief"].get("industry_sector"),
                resolved_sector=resolved_sector,
                theme_slug=theme.slug, 
                theme_features=theme.features)

    enriched_brief = BusinessBriefData(
        business_name=orchestration_result["business_brief"].get("business_name") or brief.business_name or "Projet Sans Nom",
        sector=resolved_sector,
        vision=brief.vision,
        mission=brief.mission,
        target_audience=brief.target_audience,
        differentiation=brief.differentiation,
        value_proposition=brief.value_proposition,
        location=brief.location or {"country": "Sénégal", "city": "Dakar"},
        content_generation=orchestration_result.get("content_generation", {}),
        logo_creation=orchestration_result.get("logo_creation", {}),
        seo_optimization=orchestration_result.get("seo_optimization", {})
    )
    
    # Le transformateur s'occupe maintenant de configurer le thème proprement
    site_definition = transformer.transform(enriched_brief, theme=theme)
    
    # 5. Sauvegarder en Redis pour le frontend
    await redis_client.set(
        f"site:{coaching_session.session_id}", 
        json.dumps(site_definition), 
        ex=604800  # 7 days (Quick fix for persistence)
    )
    
    # Mettre à jour le statut de la session
    coaching_session.status = SessionStatusEnum.COMPLETED
    await db.commit()

    return {
        "status": "GENERATION_COMPLETED",
        "session_id": coaching_session.session_id,
        "site_data": site_definition
    }
