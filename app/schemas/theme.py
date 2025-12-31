"""
Schemas Pydantic pour les thèmes Genesis
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ThemeBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    category: str
    compatibility_tags: List[str] = []
    features: Dict[str, Any] = {}
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    is_premium: bool = False

class ThemeResponse(ThemeBase):
    id: int

    class Config:
        from_attributes = True

class ThemeRecommendationResponse(BaseModel):
    theme: ThemeResponse
    match_score: float
    reasoning: str

class ThemeRecommendationList(BaseModel):
    brief_id: int
    recommendations: List[ThemeRecommendationResponse]

class BriefCompletedResponse(BaseModel):
    status: str = "BRIEF_COMPLETED"
    brief_id: int
    session_id: str
    redirect_url: str
    message: str

class ThemeSelectRequest(BaseModel):
    brief_id: int
    theme_id: int
