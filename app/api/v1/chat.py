"""
Chat API Endpoint
Endpoint: POST /api/v1/chat/

SECURITY ARCHITECTURE:
- Rule #1 "The Token is the Truth": User identity from JWT only (get_current_user dependency)
- Rule #2 "Chain of Trust": Token validated by FastAPI OAuth2 scheme
- Rule #3 "Zero Trust Input": Pydantic validation with extra='forbid'
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.dependencies import get_current_user, get_redis_vfs
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.logger import logger

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # ✅ SECURITY: Source of Truth
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs),
):
    """
    Secure Chat Endpoint.
    Identity is derived from JWT Token, NOT request body.
    """
    logger.info(f"Chat request from user_id={current_user.id}")
    
    try:
        # TODO: Connecter ici l'orchestrateur LangGraph ultérieurement.
        # Pour la Phase 1B (Test E2E), nous simulons une réponse simple.
        
        # MOCK LOGIC POUR TEST E2E :
        # Si le message contient "site", on simule une génération réussie
        if "site" in request.message.lower():
            brief_id = f"brief_{uuid.uuid4()}"
            brief_data = {
                "business_brief": {
                    "business_name": "Mon Entreprise",
                    "sector": "default",
                    "services": [],
                },
            }

            success = await redis_fs.write_session(current_user.id, brief_id, brief_data, ttl=86400)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save business brief.",
                )

            return ChatResponse(
                response="J'ai bien compris votre demande. Je génère votre site immédiatement...",
                brief_generated=True,
                brief_id=brief_id,
                site_data={
                    "id": 1,
                    "theme": "modern",
                    "colors": {"primary": "#000000"}
                }
            )
            
        return ChatResponse(
            response=f"Bonjour {current_user.email}, je suis Genesis. Parlez-moi de votre projet de site web.",
            brief_generated=False
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne est survenue."
        )
