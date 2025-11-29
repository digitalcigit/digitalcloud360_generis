"""
Chat Schema Definitions
SECURITY: Strict Pydantic validation with extra='forbid' (Zero Trust Input)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any


class Message(BaseModel):
    """Single message in conversation history"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    """
    Chat endpoint request schema
    
    SECURITY NOTE:
    - NO user_id field (Rule #1: The Token is the Truth)
    - User identity extracted from JWT via get_current_user dependency
    - extra='forbid' prevents malicious field injection
    """
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_history: List[Message] = Field(default_factory=list)
    
    # ⛔ SECURITY: Interdiction d'ajouter user_id ici
    
    class Config:
        extra = "forbid"  # Rejette tout champ parasite


class ChatResponse(BaseModel):
    """Chat endpoint response schema"""
    response: str
    brief_generated: bool = False
    site_data: Optional[dict[str, Any]] = None
