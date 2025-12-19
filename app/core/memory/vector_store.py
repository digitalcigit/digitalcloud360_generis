"""Vector Store Service for semantic memory operations"""

import structlog
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from openai import AsyncOpenAI

from app.config.settings import settings
from app.models.embedding import UserEmbedding

logger = structlog.get_logger()

class VectorStore:
    """Service for storing and searching embeddings"""
    
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimensions = 1536
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = await self.openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = response.data[0].embedding
            logger.info("Text embedded successfully", text_length=len(text))
            return embedding
        except Exception as e:
            logger.error("Failed to embed text", error=str(e))
            raise
    
    async def store_embedding(
        self,
        db: AsyncSession,
        user_id: int,
        brief_id: str,
        text: str,
        embedding_type: str = "brief",
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserEmbedding:
        """
        Store text and its embedding in the database.
        
        Args:
            db: Database session
            user_id: User ID
            brief_id: Brief ID
            text: Source text to embed
            embedding_type: Type of embedding (brief, conversation, preference)
            metadata: Additional metadata for filtering
            
        Returns:
            Created UserEmbedding object
        """
        # Generate embedding
        embedding_vector = await self.embed_text(text)
        
        # Create record
        user_embedding = UserEmbedding(
            user_id=user_id,
            brief_id=brief_id,
            embedding=embedding_vector,
            source_text=text,
            embedding_type=embedding_type,
            metadata_=metadata or {}
        )
        
        db.add(user_embedding)
        await db.commit()
        await db.refresh(user_embedding)
        
        logger.info(
            "Embedding stored",
            user_id=user_id,
            brief_id=brief_id,
            embedding_type=embedding_type
        )
        
        return user_embedding
    
    async def search_similar(
        self,
        db: AsyncSession,
        query_text: str,
        user_id: Optional[int] = None,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings using cosine similarity.
        
        Args:
            db: Database session
            query_text: Text to search for
            user_id: Optional user ID to filter results
            limit: Maximum number of results
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar embeddings with scores
        """
        # Generate query embedding
        query_embedding = await self.embed_text(query_text)
        
        # Build query with pgvector cosine distance
        # Note: pgvector uses <=> for cosine distance (1 - similarity)
        # So we convert to similarity: 1 - distance
        
        query = text("""
            SELECT 
                id,
                user_id,
                brief_id,
                source_text,
                embedding_type,
                metadata,
                1 - (embedding <=> :query_embedding) as similarity
            FROM user_embeddings
            WHERE 1 - (embedding <=> :query_embedding) >= :threshold
            {user_filter}
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """.format(
            user_filter="AND user_id = :user_id" if user_id else ""
        ))
        
        params = {
            "query_embedding": json.dumps(query_embedding),
            "threshold": threshold,
            "limit": limit
        }
        if user_id:
            params["user_id"] = user_id
        
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        similar_items = []
        for row in rows:
            similar_items.append({
                "id": row.id,
                "user_id": row.user_id,
                "brief_id": row.brief_id,
                "source_text": row.source_text,
                "embedding_type": row.embedding_type,
                "metadata": row.metadata,
                "similarity": float(row.similarity)
            })
        
        logger.info(
            "Similar embeddings found",
            query_length=len(query_text),
            results_count=len(similar_items)
        )
        
        return similar_items
    
    async def delete_user_embeddings(
        self,
        db: AsyncSession,
        user_id: int,
        brief_id: Optional[str] = None
    ) -> int:
        """
        Delete embeddings for a user.
        
        Args:
            db: Database session
            user_id: User ID
            brief_id: Optional specific brief ID
            
        Returns:
            Number of deleted records
        """
        query = select(UserEmbedding).where(UserEmbedding.user_id == user_id)
        if brief_id:
            query = query.where(UserEmbedding.brief_id == brief_id)
        
        result = await db.execute(query)
        embeddings = result.scalars().all()
        
        count = len(embeddings)
        for embedding in embeddings:
            await db.delete(embedding)
        
        await db.commit()
        
        logger.info("Embeddings deleted", user_id=user_id, count=count)
        return count
