"""
Genesis endpoints - Aligned with DigitalCloud360 API Contract
Route: /api/v1/genesis/business-brief/

Ce module implémente les endpoints alignés avec le contrat API DigitalCloud360
selon les spécifications P0.4 du Scrum Master.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import structlog
import uuid

from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.core.integrations.digitalcloud360 import DigitalCloud360APIClient
from app.core.quota import QuotaManager, QuotaExceededException
from app.api.v1.dependencies import (
    get_orchestrator, 
    get_redis_vfs, 
    get_digitalcloud360_client, 
    get_current_user,
    get_quota_manager
)

router = APIRouter()
logger = structlog.get_logger()


# ============================================================================
# SCHEMAS - Alignés avec contrat DC360
# ============================================================================

class BusinessBriefPayload(BaseModel):
    """Payload aligné avec wizard Genesis de DigitalCloud360"""
    business_name: str = Field(..., description="Nom de l'entreprise")
    industry_sector: str = Field(..., description="Secteur d'activité")
    vision: str = Field(..., description="Vision à long terme")
    mission: str = Field(..., description="Mission de l'entreprise")
    target_market: str = Field(..., description="Marché cible")
    services: List[str] = Field(..., description="Services ou produits proposés")
    competitive_advantage: str = Field(..., description="Avantage concurrentiel")
    location: Dict[str, str] = Field(..., description="Localisation (country, city, region)")
    years_in_business: Optional[int] = Field(None, description="Années d'existence")
    
    # Champs optionnels additionnels
    differentiation: Optional[str] = Field(None, description="Points de différenciation")
    value_proposition: Optional[str] = Field(None, description="Proposition de valeur")
    cultural_context: Optional[Dict[str, Any]] = Field(None, description="Contexte culturel")


class BusinessBriefGenerateRequest(BaseModel):
    """Request pour génération business brief"""
    user_id: int = Field(..., description="ID utilisateur DC360")
    brief_data: BusinessBriefPayload = Field(..., description="Données business")
    coaching_session_id: Optional[int] = Field(None, description="ID session coaching si existante")


class SubAgentResult(BaseModel):
    """Résultat d'un sub-agent"""
    status: str = Field(..., description="completed|failed|pending")
    data: Optional[Dict[str, Any]] = Field(None, description="Données générées")
    error: Optional[str] = Field(None, description="Erreur si échec")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BusinessBriefGenerateResponse(BaseModel):
    """Response génération business brief"""
    brief_id: str = Field(..., description="ID unique du brief généré")
    user_id: int = Field(..., description="ID utilisateur")
    status: str = Field(..., description="completed|in_progress|failed")
    
    # Business data
    business_brief: BusinessBriefPayload
    
    # Sub-agents results
    market_research: Optional[SubAgentResult] = None
    content_generation: Optional[SubAgentResult] = None
    logo_creation: Optional[SubAgentResult] = None
    seo_optimization: Optional[SubAgentResult] = None
    template_selection: Optional[SubAgentResult] = None
    
    # Metadata
    overall_confidence: float = Field(0.0, description="Confiance globale (0-1)")
    is_ready_for_website: bool = Field(False, description="Prêt pour création site")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BusinessBriefGetResponse(BaseModel):
    """Response récupération business brief existant"""
    brief_id: str
    user_id: int
    status: str
    business_brief: BusinessBriefPayload
    market_research: Optional[SubAgentResult] = None
    content_generation: Optional[SubAgentResult] = None
    logo_creation: Optional[SubAgentResult] = None
    seo_optimization: Optional[SubAgentResult] = None
    template_selection: Optional[SubAgentResult] = None
    overall_confidence: float
    is_ready_for_website: bool
    created_at: datetime
    updated_at: datetime


# ============================================================================
# ENDPOINTS - /api/v1/genesis/business-brief/
# ============================================================================

@router.post("/business-brief/", response_model=BusinessBriefGenerateResponse, status_code=201)
async def generate_business_brief(
    request: BusinessBriefGenerateRequest,
    current_user: dict = Depends(get_current_user),
    orchestrator: LangGraphOrchestrator = Depends(get_orchestrator),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs),
    quota_manager: QuotaManager = Depends(get_quota_manager)
):
    """
    POST /api/v1/genesis/business-brief/
    
    Génère un business brief complet via l'orchestrateur LangGraph.
    Coordonne les 5 sub-agents (Research, Content, Logo, SEO, Template).
    
    **Workflow:**
    1. Vérification quota utilisateur (P0.5)
    2. Validation payload
    3. Orchestration sub-agents (Sprint 1: mocks)
    4. Assemblage résultat final
    5. Persistance Redis Virtual FS
    6. Incrémentation usage
    7. Retour business brief structuré
    """
    logger.info(
        "Business brief generation requested", 
        user_id=request.user_id,
        business_name=request.brief_data.business_name,
        industry=request.brief_data.industry_sector
    )
    
    try:
        # 1. Vérifier quotas AVANT génération (P0.5)
        try:
            quota_status = await quota_manager.check_quota(request.user_id)
            logger.info(
                "Quota check passed",
                user_id=request.user_id,
                plan=quota_status["plan"],
                usage=f"{quota_status['current_usage']}/{quota_status['max_monthly_sessions'] or 'unlimited'}"
            )
        except QuotaExceededException as qe:
            # Quota dépassé - retourner 403 avec détails
            logger.warning(
                "Quota exceeded - request denied",
                user_id=request.user_id,
                error=qe.message
            )
            raise HTTPException(
                status_code=403,
                detail=qe.details
            )
        
        # 2. Générer ID unique brief
        brief_id = f"brief_{uuid.uuid4().hex[:12]}"
        
        # 3. Préparer payload orchestrateur
        orchestration_input = {
            "user_id": request.user_id,
            "brief_id": brief_id,
            "business_brief": request.brief_data.model_dump(),
            "coaching_session_id": request.coaching_session_id
        }
        
        # 4. Exécuter orchestration (Sprint 1: mocks)
        final_state = await orchestrator.run(orchestration_input)
        
        # 5. Assembler réponse structurée
        response_data = {
            "brief_id": brief_id,
            "user_id": request.user_id,
            "status": "completed",
            "business_brief": request.brief_data,
            "market_research": SubAgentResult(
                status="completed",
                data=final_state.get("market_research", {}),
                timestamp=datetime.utcnow()
            ),
            "content_generation": SubAgentResult(
                status="completed",
                data=final_state.get("content_generation", {}),
                timestamp=datetime.utcnow()
            ),
            "logo_creation": SubAgentResult(
                status="completed",
                data=final_state.get("logo_creation", {}),
                timestamp=datetime.utcnow()
            ),
            "seo_optimization": SubAgentResult(
                status="completed",
                data=final_state.get("seo_optimization", {}),
                timestamp=datetime.utcnow()
            ),
            "template_selection": SubAgentResult(
                status="completed",
                data=final_state.get("template_selection", {}),
                timestamp=datetime.utcnow()
            ),
            "overall_confidence": final_state.get("overall_confidence", 0.85),
            "is_ready_for_website": final_state.get("is_ready_for_website", True),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # 6. Sauvegarder dans Redis VFS
        await redis_fs.write_session(request.user_id, brief_id, response_data)
        
        # 7. Incrémenter usage (best-effort, ne pas bloquer si échec)
        try:
            await quota_manager.increment_usage(request.user_id, brief_id)
        except Exception as inc_err:
            logger.warning(
                "Failed to increment usage counter",
                error=str(inc_err),
                user_id=request.user_id,
                brief_id=brief_id
            )
        
        logger.info(
            "Business brief generated successfully",
            brief_id=brief_id,
            user_id=request.user_id,
            confidence=response_data["overall_confidence"]
        )
        
        return response_data
        
    except QuotaExceededException:
        raise  # Déjà géré ci-dessus
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to generate business brief",
            error=str(e),
            user_id=request.user_id,
            business_name=request.brief_data.business_name
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "GENESIS_BRIEF_GENERATION_FAILED",
                "message": f"Échec génération business brief: {str(e)}"
            }
        )


@router.get("/business-brief/{brief_id}", response_model=BusinessBriefGetResponse)
async def get_business_brief(
    brief_id: str,
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    """
    GET /api/v1/genesis/business-brief/{brief_id}
    
    Récupère un business brief existant depuis Redis VFS.
    
    **Returns:**
    - 200: Brief trouvé
    - 404: Brief introuvable
    - 403: Accès refusé (brief appartient à un autre utilisateur)
    """
    logger.info("Business brief retrieval requested", brief_id=brief_id, user_id=current_user.id)
    
    try:
        # Récupérer depuis Redis VFS
        brief_data = await redis_fs.read_session(current_user.id, brief_id)
        
        if not brief_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "GENESIS_BRIEF_NOT_FOUND",
                    "message": f"Business brief {brief_id} introuvable"
                }
            )
        
        # Validation ownership
        if brief_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "GENESIS_BRIEF_ACCESS_DENIED",
                    "message": "Accès refusé à ce business brief"
                }
            )
        
        logger.info("Business brief retrieved successfully", brief_id=brief_id)
        return brief_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve business brief", error=str(e), brief_id=brief_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "GENESIS_BRIEF_RETRIEVAL_FAILED",
                "message": f"Échec récupération business brief: {str(e)}"
            }
        )


@router.delete("/business-brief/{brief_id}", status_code=204)
async def delete_business_brief(
    brief_id: str,
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    """
    DELETE /api/v1/genesis/business-brief/{brief_id}
    
    Supprime un business brief de Redis VFS.
    
    **Returns:**
    - 204: Brief supprimé avec succès
    - 404: Brief introuvable
    - 403: Accès refusé
    """
    logger.info("Business brief deletion requested", brief_id=brief_id, user_id=current_user.id)
    
    try:
        # Vérifier existence et ownership
        brief_data = await redis_fs.read_session(current_user.id, brief_id)
        
        if not brief_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "GENESIS_BRIEF_NOT_FOUND",
                    "message": f"Business brief {brief_id} introuvable"
                }
            )
        
        if brief_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "GENESIS_BRIEF_ACCESS_DENIED",
                    "message": "Accès refusé à ce business brief"
                }
            )
        
        # Supprimer de Redis VFS
        await redis_fs.delete_session(current_user.id, brief_id)
        
        logger.info("Business brief deleted successfully", brief_id=brief_id)
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete business brief", error=str(e), brief_id=brief_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "GENESIS_BRIEF_DELETION_FAILED",
                "message": f"Échec suppression business brief: {str(e)}"
            }
        )


@router.get("/quota/status", response_model=Dict[str, Any])
async def get_quota_status(
    current_user: dict = Depends(get_current_user),
    quota_manager: QuotaManager = Depends(get_quota_manager)
):
    """
    GET /api/v1/genesis/quota/status
    
    Récupère le statut quota actuel de l'utilisateur.
    
    **Returns:**
    - user_id: ID utilisateur
    - plan: Plan tarifaire (trial, basic, pro, enterprise)
    - current_usage: Nombre sessions utilisées ce mois
    - max_monthly_sessions: Limite mensuelle (null si illimité)
    - remaining: Sessions restantes
    - reset_date: Date reset quota (ISO format)
    - percentage_used: Pourcentage quota utilisé
    
    **Usage frontend:**
    Permet d'afficher barre progression quota dans dashboard.
    """
    logger.info("Quota status requested", user_id=current_user.id)
    
    try:
        quota_status = await quota_manager.get_quota_status(current_user.id)
        
        logger.info(
            "Quota status retrieved",
            user_id=current_user.id,
            plan=quota_status.get("plan"),
            usage=f"{quota_status.get('current_usage')}/{quota_status.get('max_monthly_sessions') or 'unlimited'}"
        )
        
        return quota_status
        
    except Exception as e:
        logger.error("Failed to get quota status", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "GENESIS_QUOTA_STATUS_FAILED",
                "message": f"Échec récupération statut quota: {str(e)}"
            }
        )
