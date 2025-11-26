"""
DC360 Adapter - Endpoint alias pour DigitalCloud360
Route: /api/genesis/generate-brief/

Ce module implémente l'adaptateur de payload DC360 → Genesis
selon les spécifications du WO-GENESIS-DC360-ADAPTER-S3-001.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog
import uuid

from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.core.quota import QuotaManager, QuotaExceededException
from app.api.v1.dependencies import get_orchestrator, get_redis_vfs, get_quota_manager
from app.config.settings import settings

router = APIRouter()
logger = structlog.get_logger()


# ============================================================================
# SCHEMAS PYDANTIC DC360
# ============================================================================

class DC360BusinessInfo(BaseModel):
    """Informations business DC360"""
    company_name: str = Field(..., description="Nom de l'entreprise")
    industry: str = Field(..., description="Secteur d'activité")
    company_size: Optional[str] = Field(None, description="Taille entreprise (ex: 1-10)")
    description: str = Field(..., description="Description de l'entreprise")


class DC360MarketInfo(BaseModel):
    """Informations marché DC360"""
    target_audience: str = Field(..., description="Audience cible")
    competitors: List[str] = Field(default_factory=list, description="Liste des concurrents")
    market_challenges: Optional[str] = Field(None, description="Défis du marché")
    goals: List[str] = Field(default_factory=list, description="Objectifs business")


class DC360GenerateBriefRequest(BaseModel):
    """Request DC360 pour génération brief"""
    user_id: int = Field(..., description="ID utilisateur DC360")
    business_info: DC360BusinessInfo = Field(..., description="Informations business")
    market_info: DC360MarketInfo = Field(..., description="Informations marché")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "business_info": {
                    "company_name": "Ma Startup",
                    "industry": "Tech",
                    "company_size": "1-10",
                    "description": "Une startup innovante dans la tech au Sénégal"
                },
                "market_info": {
                    "target_audience": "PME et entrepreneurs",
                    "competitors": ["Competitor A", "Competitor B"],
                    "market_challenges": "Accès au financement, digitalisation",
                    "goals": ["Augmenter visibilité", "Générer des leads"]
                }
            }
        }


class DC360SubAgentResult(BaseModel):
    """Résultat d'un sub-agent (format Genesis)"""
    status: str = Field(..., description="completed|failed|pending")
    data: Optional[Dict[str, Any]] = Field(None, description="Données générées")
    timestamp: str = Field(..., description="Timestamp ISO 8601")


class DC360GenerateBriefResponse(BaseModel):
    """Response DC360 génération brief (format Genesis)"""
    id: str = Field(..., description="ID unique du brief")
    user_id: int = Field(..., description="ID utilisateur")
    session_id: str = Field(..., description="ID session coaching")
    status: str = Field(..., description="completed|in_progress|failed")
    
    # Sub-agents results
    market_research: Optional[DC360SubAgentResult] = None
    content_generation: Optional[DC360SubAgentResult] = None
    logo_creation: Optional[DC360SubAgentResult] = None
    seo_optimization: Optional[DC360SubAgentResult] = None
    template_selection: Optional[DC360SubAgentResult] = None
    
    # Metadata
    overall_confidence: float = Field(..., description="Confiance globale (0-1)")
    is_ready_for_website: bool = Field(..., description="Prêt pour création site")
    generated_at: str = Field(..., description="Timestamp génération ISO 8601")
    tokens_used: Optional[int] = Field(None, description="Tokens consommés")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "brief_a1b2c3d4e5f6",
                "user_id": 123,
                "session_id": "session_abc12345",
                "status": "completed",
                "market_research": {
                    "status": "completed",
                    "data": {"competitors_found": 3, "opportunities": 5},
                    "timestamp": "2025-11-26T01:30:00Z"
                },
                "content_generation": {
                    "status": "completed",
                    "data": {"pages_generated": 5, "languages": ["fr"]},
                    "timestamp": "2025-11-26T01:30:00Z"
                },
                "logo_creation": {
                    "status": "completed",
                    "data": {"url": "https://example.com/logo.png"},
                    "timestamp": "2025-11-26T01:30:00Z"
                },
                "seo_optimization": {
                    "status": "completed",
                    "data": {"keywords": 10, "meta_tags": 5},
                    "timestamp": "2025-11-26T01:30:00Z"
                },
                "template_selection": {
                    "status": "completed",
                    "data": {"template_id": "modern_business_01"},
                    "timestamp": "2025-11-26T01:30:00Z"
                },
                "overall_confidence": 0.85,
                "is_ready_for_website": True,
                "generated_at": "2025-11-26T01:30:00Z",
                "tokens_used": 1250
            }
        }


# ============================================================================
# AUTHENTIFICATION
# ============================================================================

async def verify_service_secret(
    x_service_secret: str = Header(..., alias="X-Service-Secret")
) -> bool:
    """
    Valide le header X-Service-Secret pour authentification service-to-service.
    
    Args:
        x_service_secret: Secret passé dans le header HTTP
        
    Returns:
        True si valide
        
    Raises:
        HTTPException: 401 si secret invalide ou manquant
    """
    if not settings.GENESIS_SERVICE_SECRET:
        logger.error("GENESIS_SERVICE_SECRET not configured in settings")
        raise HTTPException(
            status_code=500,
            detail="Service authentication not configured"
        )
    
    if x_service_secret != settings.GENESIS_SERVICE_SECRET:
        logger.warning(
            "Invalid service secret attempt",
            provided_secret_length=len(x_service_secret) if x_service_secret else 0
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid service secret"
        )
    
    return True


# ============================================================================
# ADAPTATEUR PAYLOAD
# ============================================================================

def adapt_dc360_to_genesis(dc360_request: DC360GenerateBriefRequest) -> dict:
    """
    Transforme le payload DC360 vers le format Genesis interne.
    
    Mapping selon WO-GENESIS-DC360-ADAPTER-S3-001 :
    - business_info.company_name → brief_data.business_name
    - business_info.industry → brief_data.industry_sector
    - business_info.description → brief_data.vision + mission
    - market_info.target_audience → brief_data.target_market
    - market_info.competitors → brief_data.competitive_advantage (join)
    - market_info.goals → brief_data.services (liste)
    - location par défaut → Sénégal, Dakar, Afrique de l'Ouest
    
    Args:
        dc360_request: Request DC360
        
    Returns:
        Dict au format Genesis orchestrator input
    """
    # Génération coaching_session_id auto
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    # Transformation payload
    genesis_payload = {
        "user_id": dc360_request.user_id,
        "coaching_session_id": session_id,
        "brief_data": {
            "business_name": dc360_request.business_info.company_name,
            "industry_sector": dc360_request.business_info.industry,
            "vision": dc360_request.business_info.description,
            "mission": dc360_request.business_info.description,  # Copie de description
            "target_market": dc360_request.market_info.target_audience,
            "services": dc360_request.market_info.goals,  # Liste goals → services
            "competitive_advantage": ", ".join(dc360_request.market_info.competitors) if dc360_request.market_info.competitors else "À définir",
            "location": {
                "country": "Sénégal",
                "city": "Dakar",
                "region": "Afrique de l'Ouest"
            }
        }
    }
    
    logger.info(
        "DC360 payload adapted to Genesis format",
        user_id=dc360_request.user_id,
        session_id=session_id,
        company_name=dc360_request.business_info.company_name
    )
    
    return genesis_payload


# ============================================================================
# ENDPOINT PRINCIPAL
# ============================================================================

@router.post(
    "/generate-brief/",
    response_model=DC360GenerateBriefResponse,
    status_code=201,
    summary="Générer un business brief (alias DC360)",
    description="""
    Endpoint alias pour DigitalCloud360.
    
    **Authentification :** Header `X-Service-Secret` requis.
    
    **Workflow :**
    1. Validation service secret
    2. Vérification quota utilisateur
    3. Adaptation payload DC360 → Genesis
    4. Orchestration LangGraph (sub-agents)
    5. Persistance Redis Virtual FS
    6. Retour réponse format Genesis
    
    **Note :** DC360 s'adapte côté frontend pour interpréter la réponse.
    """,
    responses={
        201: {"description": "Brief généré avec succès"},
        400: {"description": "Payload invalide"},
        401: {"description": "X-Service-Secret manquant ou invalide"},
        403: {"description": "Quota dépassé"},
        500: {"description": "Erreur génération"},
        504: {"description": "Timeout génération (>65s)"}
    }
)
async def generate_brief_dc360(
    request: DC360GenerateBriefRequest,
    _: bool = Depends(verify_service_secret),
    orchestrator: LangGraphOrchestrator = Depends(get_orchestrator),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs),
    quota_manager: QuotaManager = Depends(get_quota_manager)
):
    """
    POST /api/genesis/generate-brief/
    
    Génère un business brief complet via orchestration LangGraph.
    Endpoint alias dédié DC360 (sans préfixe /v1/).
    """
    logger.info(
        "DC360 brief generation requested",
        user_id=request.user_id,
        company_name=request.business_info.company_name,
        industry=request.business_info.industry
    )
    
    try:
        # 1. Vérifier quotas AVANT génération
        try:
            quota_status = await quota_manager.check_quota(request.user_id)
            logger.info(
                "Quota check passed",
                user_id=request.user_id,
                plan=quota_status.get("plan", "unknown"),
                usage=f"{quota_status.get('current_usage', 0)}/{quota_status.get('max_monthly_sessions', 'unlimited')}"
            )
        except QuotaExceededException as qe:
            logger.warning(
                "Quota exceeded - DC360 request denied",
                user_id=request.user_id,
                error=qe.message
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "QUOTA_EXCEEDED",
                    "message": qe.message,
                    "quota_info": qe.details
                }
            )
        
        # 2. Adapter payload DC360 → Genesis
        genesis_input = adapt_dc360_to_genesis(request)
        
        # 3. Générer ID unique brief
        brief_id = f"brief_{uuid.uuid4().hex[:12]}"
        genesis_input["brief_id"] = brief_id
        
        # 4. Exécuter orchestration
        logger.info(
            "Starting LangGraph orchestration for DC360 request",
            brief_id=brief_id,
            user_id=request.user_id
        )
        
        final_state = await orchestrator.run(genesis_input)
        
        # 5. Sauvegarder dans Redis Virtual FS
        brief_data_for_redis = {
            "brief_id": brief_id,
            "user_id": request.user_id,
            "session_id": genesis_input["coaching_session_id"],
            "business_info": request.business_info.model_dump(),
            "market_info": request.market_info.model_dump(),
            "results": final_state,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        await redis_fs.write_session(
            user_id=request.user_id,
            brief_id=brief_id,
            data=brief_data_for_redis,
            ttl=settings.REDIS_SESSION_TTL
        )
        
        logger.info(
            "Brief saved to Redis VFS",
            brief_id=brief_id,
            user_id=request.user_id,
            ttl=settings.REDIS_SESSION_TTL
        )
        
        # 6. Incrémenter usage quota
        await quota_manager.increment_usage(request.user_id)
        
        # 7. Assembler réponse format Genesis (DC360 compatible)
        current_time = datetime.utcnow().isoformat() + "Z"
        
        response = DC360GenerateBriefResponse(
            id=brief_id,
            user_id=request.user_id,
            session_id=genesis_input["coaching_session_id"],
            status="completed",
            market_research=DC360SubAgentResult(
                status="completed",
                data=final_state.get("market_research", {}),
                timestamp=current_time
            ),
            content_generation=DC360SubAgentResult(
                status="completed",
                data=final_state.get("content_generation", {}),
                timestamp=current_time
            ),
            logo_creation=DC360SubAgentResult(
                status="completed" if final_state.get("logo_creation") else "pending",
                data=final_state.get("logo_creation", {}),
                timestamp=current_time
            ),
            seo_optimization=DC360SubAgentResult(
                status="completed" if final_state.get("seo_optimization") else "pending",
                data=final_state.get("seo_optimization", {}),
                timestamp=current_time
            ),
            template_selection=DC360SubAgentResult(
                status="completed",
                data=final_state.get("template_selection", {}),
                timestamp=current_time
            ),
            overall_confidence=final_state.get("confidence_score", 0.8),
            is_ready_for_website=final_state.get("ready_for_website", True),
            generated_at=current_time,
            tokens_used=final_state.get("tokens_used", None)
        )
        
        logger.info(
            "DC360 brief generation completed successfully",
            brief_id=brief_id,
            user_id=request.user_id,
            confidence=response.overall_confidence
        )
        
        return response
        
    except QuotaExceededException:
        # Déjà géré ci-dessus, re-raise
        raise
    except HTTPException:
        # Re-raise les HTTPException (401, etc.)
        raise
    except Exception as e:
        logger.error(
            "DC360 brief generation failed",
            user_id=request.user_id,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "GENERATION_FAILED",
                "message": f"Brief generation failed: {str(e)}"
            }
        )
