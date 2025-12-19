"""Memory API Endpoints for semantic search"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any

from app.api.v1.dependencies import get_current_user, get_db
from app.models.user import User
from app.core.memory.vector_store import VectorStore
from app.utils.logger import logger

router = APIRouter()
vector_store = VectorStore()

class SimilarSearchRequest(BaseModel):
    """Request schema for similarity search"""
    query: str = Field(..., min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    include_all_users: bool = Field(
        default=False,
        description="Si True, recherche dans TOUS les briefs (pour recommandations anonymisées). "
                    "Par défaut False = recherche limitée à l'utilisateur courant."
    )
    
    model_config = ConfigDict(extra="forbid")

class SimilarItem(BaseModel):
    """Single similar item in response"""
    brief_id: str
    source_text: str
    embedding_type: str
    metadata: dict
    similarity: float

class SimilarSearchResponse(BaseModel):
    """Response schema for similarity search"""
    results: List[SimilarItem]
    query: str
    count: int

@router.post("/similar", response_model=SimilarSearchResponse)
async def search_similar(
    request: SimilarSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for similar briefs/content in semantic memory.
    
    Returns items similar to the query text, ordered by similarity.
    By default, searches only the current user's embeddings.
    Set include_all_users=True to search across all users (for recommendations).
    """
    logger.info(f"Similarity search from user_id={current_user.id}")
    
    try:
        user_id = None if request.include_all_users else current_user.id
        
        results = await vector_store.search_similar(
            db=db,
            query_text=request.query,
            user_id=user_id,
            limit=request.limit,
            threshold=request.threshold
        )
        
        return SimilarSearchResponse(
            results=[SimilarItem(**r) for r in results],
            query=request.query,
            count=len(results)
        )
        
    except Exception as e:
        logger.error(f"Similarity search failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors de la recherche."
        )

@router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_memory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete all semantic memory for the current user.
    Use with caution - this action is irreversible.
    """
    logger.info(f"Deleting all embeddings for user_id={current_user.id}")
    
    try:
        count = await vector_store.delete_user_embeddings(db, current_user.id)
        logger.info(f"Deleted {count} embeddings for user_id={current_user.id}")
        
    except Exception as e:
        logger.error(f"Failed to delete embeddings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors de la suppression."
        )
