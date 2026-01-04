from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
import json
import structlog

from app.config.database import get_db
from app.api.v1.dependencies import get_redis_client
from app.services.user_service import get_current_user
from app.models.user import User
from app.models.coaching import CoachingSession, BusinessBrief, SessionStatusEnum
from app.schemas.dashboard import SiteListItem, BriefResponse, BriefUpdateRequest, ConversationHistoryResponse
from app.services.transformer import BriefToSiteTransformer
from app.schemas.business_brief_data import BusinessBriefData
from app.models.theme import Theme

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/sites", response_model=List[SiteListItem])
async def list_user_sites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Liste tous les sites de l'utilisateur (Hybrid DB + Redis).
    Status 'ready' si présent en Redis, 'expired' sinon.
    """
    logger.info("dashboard_list_sites", user_id=current_user.id)
    
    # 1. Récupérer toutes les sessions COMPLETED avec leur Brief
    result = await db.execute(
        select(CoachingSession, BusinessBrief)
        .join(BusinessBrief, CoachingSession.id == BusinessBrief.coaching_session_id)
        .where(
            CoachingSession.user_id == current_user.id,
            CoachingSession.status == SessionStatusEnum.COMPLETED
        )
        .order_by(desc(CoachingSession.updated_at))
    )
    
    sites_list = []
    rows = result.all()
    
    if not rows:
        return []

    for session, brief in rows:
        # 2. Vérifier Redis pour le statut du site
        redis_key = f"site:{session.session_id}"
        site_exists = await redis_client.exists(redis_key)
        
        # Tenter d'extraire theme_slug depuis Redis si dispo pour info
        theme_slug = None
        hero_image = None
        
        if site_exists:
            try:
                # On ne charge pas tout le JSON pour la liste, trop lourd. 
                # Idealement on aurait un hash Redis, mais ici structure simple string.
                # On assume 'ready' si valid key.
                pass 
            except Exception:
                pass
        
        sites_list.append(SiteListItem(
            session_id=session.session_id,
            business_name=brief.business_name,
            sector=brief.sector,
            theme_slug=None, # Difficile à avoir sans parser tout le JSON site, on laisse vide pour l'instant
            preview_url=f"/preview/{session.session_id}",
            status="ready" if site_exists else "expired",
            created_at=session.created_at,
            updated_at=session.updated_at
        ))
        
    return sites_list

@router.get("/sites/{session_id}/brief", response_model=BriefResponse)
async def get_site_brief(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Récupère le Business Brief associé à un site"""
    
    result = await db.execute(
        select(BusinessBrief)
        .join(CoachingSession)
        .where(
            CoachingSession.session_id == session_id,
            CoachingSession.user_id == current_user.id
        )
    )
    brief = result.scalars().first()
    
    if not brief:
        raise HTTPException(status_code=404, detail="Site/Brief not found")
        
    return BriefResponse(
        session_id=session_id,
        business_name=brief.business_name,
        vision=brief.vision,
        mission=brief.mission,
        target_audience=brief.target_audience,
        differentiation=brief.differentiation,
        value_proposition=brief.value_proposition,
        sector=brief.sector,
        location=brief.location,
        logo_url=(brief.logo_creation.get("logo_url") if isinstance(brief.logo_creation, dict) else None) if brief.logo_creation else None,
        created_at=brief.created_at,
        updated_at=brief.updated_at,
        market_research_summary=brief.market_research
    )

@router.patch("/sites/{session_id}/brief")
async def update_site_brief(
    session_id: str,
    updates: BriefUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Met à jour le Brief et invalide le cache site (status -> expired)
    L'utilisateur devra cliquer sur 'Regénérer' pour voir les changements.
    """
    # 1. Fetch brief
    result = await db.execute(
        select(BusinessBrief, CoachingSession)
        .join(CoachingSession)
        .where(
            CoachingSession.session_id == session_id,
            CoachingSession.user_id == current_user.id
        )
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Brief not found")
        
    brief, session = row
    
    # 2. Update fields
    has_changes = False
    update_data = updates.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if getattr(brief, key) != value:
            setattr(brief, key, value)
            has_changes = True
            
    if has_changes:
        await db.commit()
        # Optionnel: Supprimer le site du cache pour forcer régénération?
        # Non, on laisse le site actuel visible ("expired" logic is tricky here if we delete)
        # Mais le user doit savoir que c'est out-of-sync.
        
    return {"status": "updated", "needs_regeneration": has_changes}

@router.post("/sites/{session_id}/regenerate")
async def regenerate_site(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Régénère le site basé sur le brief actuel (db) et le thème précédent (si possible).
    """
    logger.info("dashboard_regenerate_site", session_id=session_id)
    
    # 1. Fetch data
    result = await db.execute(
        select(BusinessBrief)
        .join(CoachingSession)
        .where(
            CoachingSession.session_id == session_id,
            CoachingSession.user_id == current_user.id
        )
    )
    brief = result.scalars().first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    # 2. Récupérer l'ancien site de Redis pour garder le même theme si possible
    redis_key = f"site:{session_id}"
    old_site_json = await redis_client.get(redis_key)
    
    theme_obj = None
    
    # Essayer de trouver quel thème utiliser
    if old_site_json:
        try:
            old_site = json.loads(old_site_json)
            old_theme_slug = old_site.get("theme", {}).get("slug")
            if old_theme_slug:
                theme_res = await db.execute(select(Theme).where(Theme.slug == old_theme_slug))
                theme_obj = theme_res.scalars().first()
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning("Failed to parse old site theme", session_id=session_id, error=str(e))
            
    # Si pas de thème trouvé (site expiré), fallback sur Savor (défaut) ou logique plus complexe
    if not theme_obj:
        # Fallback par défaut
        theme_res = await db.execute(select(Theme).where(Theme.slug == "savor"))
        theme_obj = theme_res.scalars().first()
        if not theme_obj:
             raise HTTPException(status_code=500, detail="Default theme not found")

    # 3. Préparer BusinessBriefData
    # Note: On réutilise les résultats IA existants (images, SEO) s'ils sont là
    # Seuls les textes modifiés manuellement dans le brief (BusinessBriefData) changent
    
    enriched_brief = BusinessBriefData(
        business_name=brief.business_name,
        sector=brief.sector,
        vision=brief.vision,
        mission=brief.mission,
        target_audience=brief.target_audience,
        differentiation=brief.differentiation,
        value_proposition=brief.value_proposition,
        location=brief.location or {"country": "Sénégal", "city": "Dakar"},
        # On garde les générations précédentes
        content_generation=brief.content_generation or {},
        logo_creation=brief.logo_creation or {},
        seo_optimization=brief.seo_optimization or {}
    )

    # 4. Transformer
    transformer = BriefToSiteTransformer()
    new_site_definition = transformer.transform(enriched_brief, theme=theme_obj)
    
    # 5. Save Redis & Refresh TTL (7 days)
    await redis_client.set(
        redis_key, 
        json.dumps(new_site_definition), 
        ex=604800 
    )
    
    return {"status": "regenerated", "preview_url": f"/preview/{session_id}"}

@router.get("/sites/{session_id}/conversation", response_model=ConversationHistoryResponse)
async def get_site_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Récupère l'historique de conversation de la session"""
    
    # 1. Verify session ownership
    result = await db.execute(
        select(CoachingSession)
        .where(
            CoachingSession.session_id == session_id,
            CoachingSession.user_id == current_user.id
        )
    )
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # 2. Extract messages from DB or Redis? 
    # CoachingSession stores 'conversation_history' as JSON in DB.
    # It sends it as a list of dicts.
    
    messages = []
    if session.conversation_history:
        for msg in session.conversation_history:
            # Adapt structure if needed. DB usually stores {role, content, timestamp}
            messages.append(msg)
            
    return ConversationHistoryResponse(
        session_id=session_id,
        messages=messages
    )
