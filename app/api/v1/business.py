"""Business endpoints for Genesis AI Service"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.business import (
    BusinessBriefRequest,
    BusinessBriefResponse,
    SubAgentResultsResponse
)
from app.schemas.responses import SuccessResponse
import structlog
import uuid
from datetime import datetime

from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.core.integrations.digitalcloud360 import DigitalCloud360APIClient
from app.api.v1.dependencies import get_orchestrator, get_redis_vfs, get_digitalcloud360_client, get_current_user

router = APIRouter()
logger = structlog.get_logger()


@router.post(
    "/brief/generate",
    response_model=BusinessBriefResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Générer un business brief complet",
    description="""
    Génère un business brief complet avec orchestration intelligente des sub-agents LangGraph.
    
    **Workflow** :
    1. Orchestrateur LangGraph coordonne les sub-agents (Research, Content, Logo, SEO, Template)
    2. Analyse marché via Tavily/Kimi (tendances, concurrents, opportunités)
    3. Génération contenu multilingue (fr, wo, en) via Deepseek/OpenAI
    4. Création logo via DALL-E 3 (7 styles disponibles)
    5. Optimisation SEO locale (mots-clés, meta tags)
    6. Sélection template adaptée au secteur
    7. Persistance dans Redis Virtual FS (TTL 7 jours)
    
    **Temps génération** : ~20-40 secondes
    
    **Quotas** :
    - Trial : 10 briefs/mois
    - Basic : 25 briefs/mois
    - Pro : 50 briefs/mois
    - Enterprise : Illimité
    """,
    responses={
        201: {
            "description": "Business brief généré avec succès",
            "content": {
                "application/json": {
                    "example": {
                        "brief_id": "brief_550e8400-e29b-41d4-a716-446655440000",
                        "user_id": 123,
                        "session_id": "session_789",
                        "results": {
                            "research": {
                                "market_size": "15M FCFA marché local Dakar",
                                "competitors": ["Competitor A", "Competitor B"],
                                "opportunities": ["Mobile-first", "Paiement Orange Money"]
                            },
                            "content": {
                                "homepage": {"fr": "Bienvenue...", "wo": "Dalal ak jàmm..."},
                                "about": {"fr": "Notre histoire..."},
                                "services": {"fr": "Nos services..."}
                            },
                            "logo": {"url": "https://...", "style": "modern-minimalist"},
                            "seo": {"keywords": ["startup tech dakar", "innovation sénégal"]},
                            "template": {"id": "tech-startup-v2", "name": "Tech Startup Modern"}
                        }
                    }
                }
            }
        },
        400: {"description": "Requête invalide (champs manquants ou format incorrect)"},
        401: {"description": "Non authentifié (JWT token manquant ou invalide)"},
        403: {"description": "Quota atteint pour ce plan"},
        429: {"description": "Rate limit dépassé (max 5 req/min)"},
        500: {"description": "Erreur serveur (provider API fail, timeout orchestrateur)"}
    }
)
async def generate_business_brief(
    request: BusinessBriefRequest,
    current_user: dict = Depends(get_current_user),
    orchestrator: LangGraphOrchestrator = Depends(get_orchestrator),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    """
    Générer le brief business complet avec orchestration des sub-agents.
    """
    logger.info("Business brief generation requested", 
               user_id=current_user.id,
               session_id=request.coaching_session_id)
    
    try:
        # 1. Run the orchestration
        business_brief_data = request.dict()
        final_state = await orchestrator.run(business_brief_data)

        # 2. Assemble the final brief
        brief_id = f"brief_{uuid.uuid4()}"
        response_data = {
            "brief_id": brief_id,
            "user_id": current_user.id,
            "session_id": request.session_id,
            "results": final_state
        }

        # 3. Save to Redis Virtual File System
        await redis_fs.write_session(current_user.id, brief_id, response_data)
        
        logger.info("Business brief generated and saved successfully", brief_id=brief_id)

        return response_data

    except Exception as e:
        logger.error("Failed to generate business brief", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate business brief: {str(e)}"
        )

@router.get(
    "/brief/{brief_id}",
    response_model=BusinessBriefResponse,
    summary="Récupérer un business brief existant",
    description="""
    Récupère un business brief complet depuis Redis Virtual File System.
    
    **Autorisation** : Seul le propriétaire (user_id) peut accéder à ses briefs.
    
    **Clé Redis** : `genesis:session:{user_id}:{brief_id}`
    
    **TTL** : 7 jours par défaut (extensible via `/extend-ttl`)
    
    **Cas d'usage** :
    - Consulter brief généré précédemment
    - Partager brief avec équipe DC360
    - Regénérer sections spécifiques
    - Créer site web depuis brief
    """,
    responses={
        200: {
            "description": "Business brief récupéré avec succès",
            "content": {
                "application/json": {
                    "example": {
                        "brief_id": "brief_550e8400-e29b-41d4-a716-446655440000",
                        "user_id": 123,
                        "session_id": "session_789",
                        "results": {
                            "research": {"market_size": "..."},
                            "content": {"homepage": {"fr": "..."}},
                            "logo": {"url": "..."},
                            "seo": {"keywords": ["..."]},
                            "template": {"id": "..."}
                        },
                        "created_at": "2025-11-22T02:30:00Z",
                        "updated_at": "2025-11-22T02:30:00Z"
                    }
                }
            }
        },
        401: {"description": "Non authentifié (JWT token manquant ou invalide)"},
        403: {"description": "Accès refusé (brief appartient à un autre utilisateur)"},
        404: {"description": "Brief non trouvé (ID invalide ou expiré)"},
        500: {"description": "Erreur serveur (Redis unavailable)"}
    }
)
async def get_business_brief(
    brief_id: str,
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    """
    Récupérer un brief business existant depuis Redis.
    """
    logger.info("Business brief retrieval requested", brief_id=brief_id, user_id=current_user.id)
    
    try:
        brief_data = await redis_fs.read_session(current_user.id, brief_id)
        if not brief_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business brief not found."
            )
        
        logger.info("Business brief retrieved successfully", brief_id=brief_id)
        return brief_data

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Failed to retrieve business brief", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve business brief: {str(e)}"
        )

@router.get("/brief/{brief_id}/results", response_model=SubAgentResultsResponse)
async def get_subagent_results(
    brief_id: str,
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    """
    Récupérer les résultats détaillés des sub-agents pour un brief donné.
    """
    logger.info("Sub-agent results requested", brief_id=brief_id, user_id=current_user.id)
    
    try:
        brief_data = await redis_fs.read_session(current_user.id, brief_id)
        if not brief_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business brief not found."
            )
        
        # Extraire et formater les résultats des sub-agents
        results = brief_data.get("results", {})
        
        # Valider que les résultats ne sont pas vides
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sub-agent results not found in the brief."
            )
            
        logger.info("Sub-agent results retrieved successfully", brief_id=brief_id)
        
        # Retourner les résultats directement s'ils correspondent au schéma
        return {"results": results}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Failed to retrieve sub-agent results", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sub-agent results: {str(e)}"
        )

@router.post("/brief/{brief_id}/regenerate", response_model=BusinessBriefResponse)
async def regenerate_business_brief(
    brief_id: str,
    request: dict, # Contient les sections à régénérer
    current_user: dict = Depends(get_current_user),
    orchestrator: LangGraphOrchestrator = Depends(get_orchestrator),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    """
    Régénérer des sections spécifiques du brief business.
    
    Le corps de la requête doit contenir `regenerate_sections`, une liste de sections à régénérer.
    Exemple: {"regenerate_sections": ["content", "logo"]}
    """
    regenerate_sections = request.get("regenerate_sections", [])
    logger.info("Business brief regeneration requested", 
               brief_id=brief_id,
               sections=regenerate_sections,
               user_id=current_user.id)

    if not regenerate_sections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="`regenerate_sections` list cannot be empty."
        )

    try:
        # 1. Charger le brief existant
        existing_brief = await redis_fs.read_session(current_user.id, brief_id)
        if not existing_brief:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business brief not found."
            )

        # 2. Préparer les données pour la régénération
        # Note: L'orchestrateur doit être capable de gérer une exécution partielle
        # ou de recevoir l'état existant pour ne régénérer que le nécessaire.
        regeneration_data = existing_brief.get("results", {}).get("business_brief_request", {})
        if not regeneration_data:
            # Si les données initiales ne sont pas trouvées, on ne peut pas régénérer
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Initial business brief data not found, cannot regenerate."
            )

        # 3. Exécuter l'orchestrateur (potentiellement avec un état initial)
        # Pour l'instant, nous relançons une orchestration complète, mais une version
        # optimisée pourrait ne relancer que les branches nécessaires.
        final_state = await orchestrator.run(regeneration_data)

        # 4. Mettre à jour le brief avec les nouveaux résultats
        # Ici, on pourrait fusionner les résultats au lieu de tout remplacer
        existing_brief["results"] = final_state
        existing_brief["updated_at"] = datetime.utcnow().isoformat()

        # 5. Sauvegarder le brief mis à jour
        await redis_fs.write_session(current_user.id, brief_id, existing_brief)

        logger.info("Business brief regenerated and saved successfully", brief_id=brief_id)

        return existing_brief

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Failed to regenerate business brief", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate business brief: {str(e)}"
        )

@router.post("/website/create", response_model=SuccessResponse)
async def create_website_from_brief(
    request: dict, # Contient le brief_id
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs),
    client: DigitalCloud360APIClient = Depends(get_digitalcloud360_client)
):
    """
    Créer le site web sur DigitalCloud360 à partir du brief.
    
    Le corps de la requête doit contenir `brief_id`.
    Exemple: {"brief_id": "brief_12345"}
    """
    brief_id = request.get("brief_id")
    if not brief_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="`brief_id` is required."
        )

    logger.info("Website creation requested", brief_id=brief_id, user_id=current_user.id)

    try:
        # 1. Charger le brief complet depuis Redis
        brief_data = await redis_fs.read_session(current_user.id, brief_id)
        if not brief_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business brief not found."
            )

        # 2. Valider que le brief contient les informations nécessaires
        results = brief_data.get("results")
        if not results or not all(k in results for k in ["content", "logo", "seo", "template"]):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The business brief is incomplete and cannot be used to create a website."
            )

        # 3. Appeler l'API DigitalCloud360 pour créer le site
        website_response = await client.create_website(brief_data)

        logger.info("Website created successfully on DigitalCloud360", 
                   brief_id=brief_id, 
                   website_url=website_response.get("url"))

        return {
            "success": True,
            "message": "Website created successfully",
            "details": {"website_url": website_response.get("url")}
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Failed to create website", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create website: {str(e)}"
        )
