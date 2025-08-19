"""Coaching-related models for Genesis AI Service"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
import enum
from .base import BaseModel

class CoachingStepEnum(str, enum.Enum):
    """Étapes du coaching structurant"""
    VISION = "vision"
    MISSION = "mission"
    CLIENTELE = "clientele"
    DIFFERENTIATION = "differentiation"
    OFFRE = "offre"
    SYNTHESIS = "synthesis"

class SessionStatusEnum(str, enum.Enum):
    """Statuts de session coaching"""
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COACHING_COMPLETE = "coaching_complete"
    SUB_AGENTS_RUNNING = "sub_agents_running"
    BRIEF_READY = "brief_ready"
    COMPLETED = "completed"
    FAILED = "failed"

class CoachingSession(BaseModel):
    """Session de coaching complète"""
    __tablename__ = "coaching_sessions"
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, nullable=False, index=True)
    
    # Session state
    status = Column(Enum(SessionStatusEnum), default=SessionStatusEnum.INITIALIZED)
    current_step = Column(Enum(CoachingStepEnum), default=CoachingStepEnum.VISION)
    
    # Progress tracking
    step_completion = Column(JSON)  # {"vision": True, "mission": False, ...}
    coaching_confidence = Column(Float, default=0.0)
    retry_count = Column(Integer, default=0)
    
    # Context data
    cultural_context = Column(JSON)
    sector_context = Column(JSON)
    coaching_plan = Column(JSON)  # Liste des étapes personnalisées
    
    # Session metadata
    conversation_history = Column(JSON)  # Historique conversations
    coaching_duration = Column(Integer)  # Durée en secondes
    
    # Relationships
    user = relationship("User", back_populates="coaching_sessions")
    coaching_steps = relationship("CoachingStep", back_populates="session")
    business_brief = relationship("BusinessBrief", back_populates="coaching_session", uselist=False)

class CoachingStep(BaseModel):
    """Étape individuelle de coaching"""
    __tablename__ = "coaching_steps"
    
    # Session relationship
    session_id = Column(Integer, ForeignKey("coaching_sessions.id"), nullable=False)
    
    # Step details
    step_name = Column(Enum(CoachingStepEnum), nullable=False)
    step_order = Column(Integer, nullable=False)
    
    # Step content
    user_response = Column(Text)
    coach_message = Column(Text)
    examples_provided = Column(JSON)  # Exemples sectoriels utilisés
    
    # Step validation
    is_complete = Column(JSON)  # Boolean
    confidence_score = Column(Float, default=0.0)
    validation_criteria = Column(JSON)
    
    # Timing
    step_duration = Column(Integer)  # Durée étape en secondes
    
    # Relationships
    session = relationship("CoachingSession", back_populates="coaching_steps")

class BusinessBrief(BaseModel):
    """Brief business final généré par le coaching"""
    __tablename__ = "business_briefs"
    
    # Session relationship
    coaching_session_id = Column(Integer, ForeignKey("coaching_sessions.id"), nullable=False)
    
    # Brief components (résultats coaching)
    business_name = Column(String, nullable=False)
    vision = Column(Text, nullable=False)
    mission = Column(Text, nullable=False)
    target_audience = Column(Text, nullable=False)
    differentiation = Column(Text, nullable=False)
    value_proposition = Column(Text, nullable=False)
    
    # Business context
    sector = Column(String, nullable=False)
    location = Column(JSON)  # {"city": "Dakar", "country": "Sénégal"}
    
    # Sub-agents results
    market_research = Column(JSON)  # Résultats ResearchSubAgent
    content_generation = Column(JSON)  # Résultats ContentSubAgent
    logo_creation = Column(JSON)  # Résultats LogoSubAgent
    seo_optimization = Column(JSON)  # Résultats SEOSubAgent
    template_selection = Column(JSON)  # Résultats TemplateSubAgent
    
    # Quality metrics
    overall_confidence = Column(Float, default=0.0)
    brief_completeness = Column(Float, default=0.0)
    
    # Website creation readiness
    is_ready_for_website = Column(JSON, default=False)  # Boolean
    dc360_website_id = Column(Integer)  # ID site créé dans DigitalCloud360
    
    # Relationships
    coaching_session = relationship("CoachingSession", back_populates="business_brief")
