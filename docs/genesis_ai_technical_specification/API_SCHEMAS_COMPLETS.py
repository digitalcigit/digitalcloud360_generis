"""
Genesis AI Deep Agents - Schémas API Complets
============================================
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# =============================================================================
# ENUMS DE BASE
# =============================================================================

class CoachingStepEnum(str, Enum):
    VISION = "vision"
    MISSION = "mission" 
    CLIENTELE = "clientele"
    DIFFERENTIATION = "differentiation"
    OFFRE = "offre"
    SYNTHESIS = "synthesis"

class SessionStatusEnum(str, Enum):
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COACHING_COMPLETE = "coaching_complete"
    SUB_AGENTS_RUNNING = "sub_agents_running"
    BRIEF_READY = "brief_ready"
    COMPLETED = "completed"
    FAILED = "failed"

# =============================================================================
# SCHÉMAS USER & AUTH
# =============================================================================

class UserProfile(BaseModel):
    """Profil utilisateur Genesis AI"""
    user_id: int = Field(..., description="ID utilisateur DigitalCloud360")
    email: str = Field(..., description="Email utilisateur")
    name: str = Field(..., description="Nom complet")
    location: Dict[str, str] = Field(default_factory=dict, description="Localisation")
    sector: Optional[str] = Field(None, description="Secteur d'activité")
    experience_level: str = Field("débutant", description="Niveau expérience")
    
class AuthResponse(BaseModel):
    """Réponse authentification"""
    access_token: str = Field(..., description="JWT token")
    token_type: str = Field("bearer", description="Type token")
    user_profile: UserProfile = Field(..., description="Profil utilisateur")

# =============================================================================
# SCHÉMAS COACHING
# =============================================================================

class CoachingRequest(BaseModel):
    """Requête démarrage coaching"""
    user_id: int = Field(..., description="ID utilisateur")
    session_id: Optional[str] = Field(None, description="ID session existante")
    user_response: Optional[str] = Field(None, description="Réponse utilisateur")
    current_step: Optional[CoachingStepEnum] = Field(None, description="Étape actuelle")

class CoachingResponse(BaseModel):
    """Réponse coaching"""
    session_id: str = Field(..., description="ID session coaching")
    current_step: CoachingStepEnum = Field(..., description="Étape courante")
    coach_message: str = Field(..., description="Message coach IA")
    examples: List[str] = Field(default_factory=list, description="Exemples sectoriels")
    next_questions: List[str] = Field(default_factory=list, description="Questions suivantes")
    progress: Dict[str, bool] = Field(default_factory=dict, description="Progression étapes")
    confidence_score: float = Field(0.0, description="Score confiance réponse")

class BusinessBrief(BaseModel):
    """Brief business complet"""
    business_name: str = Field(..., description="Nom business")
    vision: str = Field(..., description="Vision entrepreneur")
    mission: str = Field(..., description="Mission business")
    target_audience: str = Field(..., description="Clientèle cible")
    differentiation: str = Field(..., description="Différenciation")
    value_proposition: str = Field(..., description="Proposition valeur")
    sector: str = Field(..., description="Secteur activité")
    location: Dict[str, str] = Field(..., description="Localisation")

# =============================================================================
# SCHÉMAS SUB-AGENTS
# =============================================================================

class ResearchResult(BaseModel):
    """Résultat recherche marché"""
    market_size: Dict[str, Any] = Field(..., description="Taille marché")
    competitors: List[Dict[str, Any]] = Field(..., description="Concurrents")
    opportunities: List[Dict[str, Any]] = Field(..., description="Opportunités")
    pricing: Dict[str, Any] = Field(..., description="Données prix")
    
class ContentResult(BaseModel):
    """Résultat génération contenu"""
    homepage: Dict[str, Any] = Field(..., description="Contenu accueil")
    about: Dict[str, Any] = Field(..., description="Contenu à propos")
    services: Dict[str, Any] = Field(..., description="Contenu services")
    seo_metadata: Dict[str, Any] = Field(..., description="Métadonnées SEO")

class LogoResult(BaseModel):
    """Résultat création logo"""
    primary_logo: Dict[str, Any] = Field(..., description="Logo principal")
    alternatives: List[Dict[str, Any]] = Field(..., description="Alternatives")
    color_palette: List[str] = Field(..., description="Palette couleurs")
    brand_guidelines: Dict[str, Any] = Field(..., description="Guidelines marque")

# =============================================================================
# RÉPONSES API COMPLÈTES
# =============================================================================

class SessionCompleteResponse(BaseModel):
    """Réponse session coaching complète"""
    success: bool = Field(..., description="Succès session")
    session_id: str = Field(..., description="ID session")
    business_brief: BusinessBrief = Field(..., description="Brief business final")
    coaching_confidence: float = Field(..., description="Score confiance coaching")
    sub_agents_results: Dict[str, Any] = Field(..., description="Résultats sous-agents")
    website_ready: bool = Field(..., description="Site web prêt génération")
    next_steps: List[str] = Field(..., description="Étapes suivantes")

# =============================================================================
# EXEMPLES REQUÊTES/RÉPONSES
# =============================================================================

# Exemple requête démarrage coaching
COACHING_START_REQUEST = {
    "user_id": 123,
    "session_id": None,
    "user_response": None,
    "current_step": None
}

# Exemple réponse coaching étape vision
COACHING_VISION_RESPONSE = {
    "session_id": "sess_abc123",
    "current_step": "vision",
    "coach_message": "Parlons de votre vision entrepreneuriale...",
    "examples": [
        "Salon de coiffure moderne qui valorise beauté africaine",
        "Restaurant fusion cuisine locale et internationale"
    ],
    "next_questions": [
        "Quelle transformation souhaitez-vous apporter ?",
        "Comment voyez-vous votre business dans 5 ans ?"
    ],
    "progress": {"vision": False, "mission": False},
    "confidence_score": 0.0
}

# Exemple business brief complet
BUSINESS_BRIEF_EXAMPLE = {
    "business_name": "Afro Beauty Salon",
    "vision": "Devenir le salon de référence valorisant beauté africaine naturelle",
    "mission": "Offrir soins capillaires authentiques respectueux traditions",
    "target_audience": "Femmes africaines 25-45 ans soucieuses beauté naturelle", 
    "differentiation": "Expertise produits naturels locaux et techniques traditionnelles",
    "value_proposition": "Beauté authentique avec produits 100% naturels",
    "sector": "salon de coiffure",
    "location": {"city": "Dakar", "country": "Sénégal"}
}
