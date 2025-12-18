"""
Chat API Endpoint
Endpoint: POST /api/v1/chat/

SECURITY ARCHITECTURE:
- Rule #1 "The Token is the Truth": User identity from JWT only (get_current_user dependency)
- Rule #2 "Chain of Trust": Token validated by FastAPI OAuth2 scheme
- Rule #3 "Zero Trust Input": Pydantic validation with extra='forbid'
"""

import uuid
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.dependencies import get_current_user, get_redis_vfs, get_orchestrator
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.services.transformer import BriefToSiteTransformer
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.logger import logger

router = APIRouter()
transformer = BriefToSiteTransformer()

def extract_business_context(message: str) -> Dict[str, Any]:
    """
    Extraction basique pour Phase 2 MVP.
    Extrait les informations structurées du message utilisateur.
    """
    # TODO: Pour la Phase 2+, utiliser un LLM pour l'extraction
    return {
        "business_name": "Entreprise",  # À extraire ou demander plus tard
        "industry_sector": "default",
        "vision": message[:200],  # Utiliser le début du message comme vision
        "mission": message[:200],
        "location": {"country": "Sénégal", "city": "Dakar"},  # Défaut pour MVP
        "services": [],
        "target_market": "",
        "competitive_advantage": ""
    }

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # ✅ SECURITY: Source of Truth
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs),
    orchestrator: LangGraphOrchestrator = Depends(get_orchestrator),
):
    """
    Secure Chat Endpoint.
    Identity is derived from JWT Token, NOT request body.
    """
    logger.info(f"Chat request from user_id={current_user.id}")
    
    try:
        # Analyse du message pour voir si c'est une demande de création de site
        # Pour le MVP, on suppose que toute demande longue (> 10 chars) est une demande de site
        # ou si le mot "site" est présent.
        is_site_request = "site" in request.message.lower() or len(request.message) > 20

        if is_site_request:
            logger.info("Detected site generation request, triggering LangGraph orchestrator")
            
            # 1. Extraction du contexte business
            business_context = extract_business_context(request.message)
            brief_id = f"brief_{uuid.uuid4()}"
            
            # 2. Exécution de l'orchestrateur
            orchestration_input = {
                "user_id": current_user.id,
                "brief_id": brief_id,
                "business_brief": business_context
            }
            
            result_state = await orchestrator.run(orchestration_input)
            
            if not result_state.get("is_ready_for_website"):
                 logger.warning("Orchestration finished but not ready for website generation")
                 # On pourrait retourner une réponse demandant plus d'infos, 
                 # mais pour le MVP on continue si possible ou on notifie l'erreur.
                 if result_state.get("error"):
                     raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Generation failed: {result_state['error']}"
                    )
            
            # 3. Construction du BusinessBrief complet pour transformation
            # Le transformer attend un objet qui a des attributs comme un modèle SQLAlchemy
            # ou un dict. BriefToSiteTransformer gère BusinessBrief (SQLAlchemy) ou BusinessBriefData (Pydantic)
            # Ici, result_state contient des dicts. On va construire un objet compatible.
            
            class BriefAdapter:
                def __init__(self, data):
                    self.business_name = data.get('business_brief', {}).get('business_name')
                    self.sector = data.get('business_brief', {}).get('industry_sector')
                    self.mission = data.get('business_brief', {}).get('mission')
                    self.vision = data.get('business_brief', {}).get('vision')
                    self.differentiation = data.get('business_brief', {}).get('competitive_advantage', '')
                    self.value_proposition = "" # Pas dans l'input initial extraction
                    self.services = data.get('business_brief', {}).get('services', [])
                    
                    self.content_generation = data.get('content_generation')
                    self.logo_creation = data.get('logo_creation')
                    self.seo_optimization = data.get('seo_optimization')
                    self.template_selection = data.get('template_selection')
            
            brief_adapter = BriefAdapter(result_state)
            
            # 4. Transformation en SiteDefinition
            site_definition = transformer.transform(brief_adapter)
            
            # 5. Sauvegarde en Redis
            # On sauvegarde le résultat brut de l'orchestrateur + la définition du site
            session_data = {
                "business_brief": result_state,
                "site_definition": site_definition
            }
            
            success = await redis_fs.write_session(current_user.id, brief_id, session_data, ttl=86400)
            if not success:
                logger.error("Failed to write session to Redis")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save generated site.",
                )

            # Construct agents status for transparency
            agents_status = {}
            for agent_name in ['market_research', 'content_generation', 'logo_creation', 'seo_optimization', 'template_selection']:
                agent_result = result_state.get(agent_name, {})
                if agent_result.get('error'):
                    status_code = 'failed'
                elif agent_result.get('fallback_mode'):
                    status_code = 'fallback'
                elif agent_result:
                    status_code = 'success'
                else:
                    status_code = 'pending'
                agents_status[agent_name] = status_code

            return ChatResponse(
                response=f"J'ai analysé votre demande pour '{brief_adapter.business_name}'. Mes agents ont travaillé sur votre projet (Confiance: {result_state.get('overall_confidence', 0):.2f}). Voici le résultat préliminaire.",
                brief_generated=True,
                brief_id=brief_id,
                site_data=site_definition,
                orchestration_confidence=result_state.get('overall_confidence', 0.0),
                agents_status=agents_status
            )
            
        return ChatResponse(
            response=f"Bonjour {current_user.email}, je suis Genesis. Parlez-moi de votre projet de site web pour que je puisse activer mes agents.",
            brief_generated=False
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        # SECURITY: Ne pas exposer les détails d'erreur au client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne est survenue. Veuillez réessayer."
        )
