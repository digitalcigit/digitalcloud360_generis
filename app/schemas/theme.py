"""
Schemas Pydantic pour les thèmes Genesis
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.coaching import CoachingStepEnum

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
    coach_message: str = ""
    examples: List[str] = Field(default_factory=list)
    current_step: CoachingStepEnum = CoachingStepEnum.OFFRE
    progress: Dict[str, bool] = Field(default_factory=dict)

class ThemeSelectRequest(BaseModel):
    brief_id: int
    theme_id: int
