"""Embedding model for semantic memory with pgvector"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from .base import BaseModel

class UserEmbedding(BaseModel):
    """Stockage des embeddings utilisateur pour mémoire sémantique"""
    __tablename__ = "user_embeddings"
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    brief_id = Column(String, nullable=False, index=True)
    
    # Embedding vector (OpenAI text-embedding-3-small = 1536 dimensions)
    embedding = Column(Vector(1536), nullable=False)
    
    # Source content that was embedded
    source_text = Column(Text, nullable=False)
    embedding_type = Column(String, default="brief")  # brief, conversation, preference
    
    # Metadata for filtering
    metadata_ = Column("metadata", JSONB, default={})
    # Example: {"sector": "restaurant", "location": "Dakar", "template": "modern"}
    
    # Relationships
    user = relationship("User", back_populates="embeddings")
