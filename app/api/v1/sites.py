"""Sites API endpoints for Genesis AI Service.

Ce module expose les endpoints pour générer et récupérer des SiteDefinition.
Il connecte le Transformer (GEN-7) au Block Renderer frontend (GEN-9).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
import structlog

from app.services.transformer import BriefToSiteTransformer
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.api.v1.dependencies import get_redis_vfs, get_current_user
from app.schemas.business_brief_data import (
    BusinessBriefData,
    ContentGenerationData,
    LogoCreationData,
    SEOOptimizationData,
    TemplateSelectionData,
    ServiceItem
)

router = APIRouter()
logger = structlog.get_logger()
transformer = BriefToSiteTransformer()


# ===== Request/Response Schemas =====

class GenerateSiteRequest(BaseModel):
    """Request body for POST /sites/generate"""
    brief_id: str = Field(..., description="ID du BusinessBrief à transformer")


class SiteResponse(BaseModel):
    """Response for site endpoints"""
    site_id: str
    brief_id: str
    user_id: int
    site_definition: Dict[str, Any]
    created_at: str


# ===== Helper Functions =====

def _build_business_brief_from_redis(redis_data: Dict[str, Any]) -> BusinessBriefData:
    """
    Construit un BusinessBriefData depuis les données Redis.
    
    Supporte deux formats :
    - Format business.py (HOTFIX): redis_data["content_generation"], redis_data["logo_creation"], etc.
    - Format legacy sub-agents: redis_data["content"]["data"], redis_data["logo"]["data"], etc.
    """
    # Données de base - support des deux formats
    brief = redis_data.get("business_brief", {})
    
    # Si business_brief est un objet Pydantic sérialisé, extraire le dict
    if isinstance(brief, str):
        import json
        try:
            brief = json.loads(brief)
        except:
            brief = {}
    
    # Résultats sub-agents - support des deux formats
    # Format 1 (business.py HOTFIX): content_generation, logo_creation, etc.
    # Format 2 (legacy): content.data, logo.data, etc.
    content_data = redis_data.get("content_generation") or redis_data.get("content", {}).get("data", {}) or {}
    logo_data = redis_data.get("logo_creation") or redis_data.get("logo", {}).get("data", {}) or {}
    seo_data = redis_data.get("seo_optimization") or redis_data.get("seo", {}).get("data", {}) or {}
    template_data = redis_data.get("template_selection") or redis_data.get("template", {}).get("data", {}) or {}
    
    # Extraire les services
    services_raw = brief.get("services", [])
    services = []
    for svc in services_raw:
        if isinstance(svc, dict):
            services.append(ServiceItem(
                title=svc.get("title", svc.get("name", "Service")),
                description=svc.get("description"),
                icon=svc.get("icon"),
                price=svc.get("price")
            ))
        elif isinstance(svc, str):
            services.append(ServiceItem(title=svc))
    
    # Construire le modèle
    return BusinessBriefData(
        business_name=brief.get("business_name", "Mon Entreprise"),
        sector=brief.get("sector", "default"),
        mission=brief.get("mission"),
        vision=brief.get("vision"),
        value_proposition=brief.get("value_proposition"),
        target_audience=brief.get("target_audience"),
        differentiation=brief.get("differentiation"),
        services=services,
        email=brief.get("email"),
        phone=brief.get("phone"),
        address=brief.get("address"),
        content_generation=ContentGenerationData(**content_data) if content_data else None,
        logo_creation=LogoCreationData(**logo_data) if logo_data else None,
        seo_optimization=SEOOptimizationData(**seo_data) if seo_data else None,
        template_selection=TemplateSelectionData(**template_data) if template_data else None
    )


# ===== Endpoints =====

@router.post(
    "/generate",
    response_model=SiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Générer un SiteDefinition depuis un BusinessBrief",
    description="""
    Transforme un BusinessBrief existant en SiteDefinition JSON
    utilisable par le Block Renderer frontend.
    
    **Workflow** :
    1. Charge le BusinessBrief depuis Redis (via brief_id)
    2. Applique le Transformer (mapping déterministe)
    3. Sauvegarde le SiteDefinition dans Redis
    4. Retourne le site_id et la définition complète
    """
)
async def generate_site(
    request: GenerateSiteRequest,
    current_user = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
) -> SiteResponse:
    brief_id = request.brief_id
    user_id = current_user.id
    
    logger.info("Generating site from brief", brief_id=brief_id, user_id=user_id)
    
    # 1. Charger le brief depuis Redis
    brief_data = await redis_fs.read_session(user_id, brief_id)
    if not brief_data:
        logger.warning("Brief not found", brief_id=brief_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business brief '{brief_id}' not found."
        )
    
    # 2. Construire le BusinessBriefData model
    try:
        business_brief = _build_business_brief_from_redis(brief_data)
    except Exception as e:
        logger.error("Failed to parse brief data", error=str(e), brief_id=brief_id)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse brief data: {str(e)}"
        )
    
    # 3. Transformer en SiteDefinition
    try:
        site_definition = transformer.transform(business_brief)
    except Exception as e:
        logger.error("Transformer failed", error=str(e), brief_id=brief_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transform brief to site: {str(e)}"
        )
    
    # 4. Sauvegarder dans Redis
    site_id = f"site_{uuid.uuid4()}"
    created_at = datetime.utcnow().isoformat() + "Z"
    
    site_data = {
        "site_id": site_id,
        "brief_id": brief_id,
        "user_id": user_id,
        "site_definition": site_definition,
        "created_at": created_at
    }
    
    success = await redis_fs.write_session(user_id, site_id, site_data, ttl=86400)  # 24h TTL
    if not success:
        logger.error("Failed to save site to Redis", site_id=site_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save site definition."
        )
    
    logger.info("Site generated successfully", site_id=site_id, brief_id=brief_id)
    
    return SiteResponse(**site_data)


@router.get(
    "/{site_id}",
    response_model=SiteResponse,
    summary="Récupérer un SiteDefinition existant"
)
async def get_site(
    site_id: str,
    current_user = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
) -> SiteResponse:
    user_id = current_user.id
    
    logger.info("Fetching site", site_id=site_id, user_id=user_id)
    
    site_data = await redis_fs.read_session(user_id, site_id)
    if not site_data:
        logger.warning("Site not found", site_id=site_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site '{site_id}' not found."
        )
    
    return SiteResponse(**site_data)


@router.get(
    "/{site_id}/preview",
    summary="Récupérer le SiteDefinition pour le renderer",
    description="Retourne uniquement le site_definition (sans métadonnées) pour le Block Renderer frontend."
)
async def get_site_preview(
    site_id: str,
    current_user = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
) -> Dict[str, Any]:
    user_id = current_user.id
    
    logger.info("Fetching site preview", site_id=site_id, user_id=user_id)
    
    site_data = await redis_fs.read_session(user_id, site_id)
    if not site_data:
        logger.warning("Site not found for preview", site_id=site_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site '{site_id}' not found."
        )
    
    # Retourne uniquement le site_definition pour le renderer
    return site_data.get("site_definition", {})
