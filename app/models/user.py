"""User-related models for Genesis AI Service"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    """User model - synced from DigitalCloud360"""
    __tablename__ = "users"
    
    # Primary key matching DigitalCloud360
    dc360_user_id = Column(Integer, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    
    # Relationship to profile
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    coaching_sessions = relationship("CoachingSession", back_populates="user")

class UserProfile(BaseModel):
    """Extended user profile for Genesis AI coaching"""
    __tablename__ = "user_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Location data
    country = Column(String)
    city = Column(String)
    region = Column(String)
    
    # Business context
    sector = Column(String)
    experience_level = Column(String, default="débutant")
    business_stage = Column(String)
    
    # Coaching preferences
    preferred_language = Column(String, default="fr")
    coaching_style = Column(String)
    
    # Additional context as JSON
    cultural_context = Column(JSON)
    business_context = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="profile")
