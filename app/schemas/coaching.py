"""Coaching-related Pydantic schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

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

class CoachingRequest(BaseModel):
    """Requête démarrage ou continuation coaching"""
    session_id: Optional[str] = Field(None, description="ID session existante")
    message: Optional[str] = Field(None, description="Message facultatif pour démarrer avec contexte")

class CoachingStepRequest(BaseModel):
    """Requête pour soumettre une réponse à une étape de coaching"""
    session_id: str = Field(..., description="ID de la session de coaching")
    user_response: str = Field(..., description="Réponse de l'utilisateur à l'étape en cours")

class CoachingResponse(BaseModel):
    """Réponse coaching intermédiaire"""
    session_id: str = Field(..., description="ID session coaching")
    current_step: CoachingStepEnum = Field(..., description="Étape courante")
    coach_message: str = Field(..., description="Message coach IA")
    examples: List[str] = Field(default_factory=list, description="Exemples sectoriels")
    next_questions: List[str] = Field(default_factory=list, description="Questions suivantes")
    progress: Dict[str, bool] = Field(default_factory=dict, description="Progression étapes")
    confidence_score: float = Field(0.0, description="Score confiance réponse")
    is_step_complete: bool = Field(False, description="Étape terminée")
    site_data: Optional[Dict[str, Any]] = Field(None, description="Données du site généré (si terminé)")
    clickable_choices: List[Dict[str, str]] = Field(default_factory=list, description="Pistes thématiques cliquables (Niveau Argent)")
    
class CoachingStepResponse(BaseModel):
    """Réponse détaillée d'une étape coaching"""
    step_name: CoachingStepEnum
    user_response: str
    coach_feedback: str
    validation_result: Dict[str, Any]
    confidence_score: float
    next_step: Optional[CoachingStepEnum] = None

class SessionCompleteResponse(BaseModel):
    """Réponse session coaching complète"""
    success: bool = Field(..., description="Succès session")
    session_id: str = Field(..., description="ID session")
    business_brief: Dict[str, Any] = Field(..., description="Brief business final")
    coaching_confidence: float = Field(..., description="Score confiance coaching")
    sub_agents_results: Dict[str, Any] = Field(..., description="Résultats sous-agents")
    website_ready: bool = Field(..., description="Site web prêt génération")
    next_steps: List[str] = Field(..., description="Étapes suivantes")
    conversation_summary: str = Field(..., description="Résumé conversation")

# --- NOUVEAUX SCHÉMAS NIVEAU ARGENT (Sprint 2) ---

class ClickableChoice(BaseModel):
    id: str
    text: str
    description: Optional[str] = None

class SocraticQuestion(BaseModel):
    question: str
    context_hint: Optional[str] = None
    choices: List[ClickableChoice] = Field(default_factory=list)

class CoachingHelpResponse(BaseModel):
    session_id: str
    current_step: CoachingStepEnum
    socratic_questions: List[SocraticQuestion]
    suggestion: str

class ReformulateRequest(BaseModel):
    session_id: str
    text: str
    target_step: Optional[CoachingStepEnum] = None

class ReformulateResponse(BaseModel):
    original_text: str
    reformulated_text: str
    is_better: bool
    suggestions: List[str] = Field(default_factory=list)

class Proposal(BaseModel):
    id: str
    title: str
    content: str
    justification: str

class GenerateProposalsResponse(BaseModel):
    session_id: str
    step: CoachingStepEnum
    proposals: List[Proposal]
    coach_advice: str
