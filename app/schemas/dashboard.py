from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class SiteListItem(BaseModel):
    """Schéma résumé pour la liste des sites dans le dashboard"""
    session_id: str = Field(..., description="UUID de la session de coaching (clé primaire)")
    business_name: str
    sector: str
    theme_slug: Optional[str] = None
    preview_url: str
    status: str = Field(..., description="'ready' (Redis OK) | 'expired' (Redis KO)")
    created_at: datetime
    updated_at: Optional[datetime] = None
    hero_image_url: Optional[str] = None

class BriefUpdateRequest(BaseModel):
    """Champs modifiables du Business Brief"""
    business_name: Optional[str] = None
    vision: Optional[str] = None
    mission: Optional[str] = None
    target_audience: Optional[str] = None
    differentiation: Optional[str] = None
    value_proposition: Optional[str] = None
    # Sector et Location sont structurels, modifications plus risquées (a voir plus tard)

class BriefResponse(BaseModel):
    """Vue détaillée du Business Brief pour le dashboard"""
    session_id: str
    business_name: str
    vision: str
    mission: str
    target_audience: str
    differentiation: str
    value_proposition: str
    sector: str
    location: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Données statiques des agents (lecture seule pour reference)
    market_research_summary: Optional[Dict[str, Any]] = None

class ConversationMessage(BaseModel):
    role: str  # "coach" | "user"
    content: str
    timestamp: Optional[datetime] = None

class ConversationHistoryResponse(BaseModel):
    session_id: str
    messages: List[ConversationMessage]
