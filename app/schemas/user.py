"""User-related Pydantic schemas"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr = Field(..., description="Email utilisateur")
    name: str = Field(..., description="Nom complet")

class UserCreate(UserBase):
    """Schema for user creation"""
    dc360_user_id: int = Field(..., description="ID utilisateur DigitalCloud360")
    
class UserProfile(BaseModel):
    """Profil utilisateur Genesis AI"""
    user_id: int = Field(..., description="ID utilisateur")
    email: EmailStr = Field(..., description="Email utilisateur")
    name: str = Field(..., description="Nom complet")
    
    # Location
    country: Optional[str] = Field(None, description="Pays")
    city: Optional[str] = Field(None, description="Ville")
    region: Optional[str] = Field(None, description="Région")
    
    # Business context
    sector: Optional[str] = Field(None, description="Secteur d'activité")
    experience_level: str = Field("débutant", description="Niveau expérience")
    business_stage: Optional[str] = Field(None, description="Stade business")
    
    # Preferences
    preferred_language: str = Field("fr", description="Langue préférée")
    coaching_style: Optional[str] = Field(None, description="Style coaching préféré")
    
    # Context
    cultural_context: Optional[Dict[str, Any]] = Field(None, description="Contexte culturel")
    business_context: Optional[Dict[str, Any]] = Field(None, description="Contexte business")

class UserResponse(BaseModel):
    """Response schema for user data"""
    id: int
    dc360_user_id: int
    email: str
    name: str
    created_at: datetime
    profile: Optional[UserProfile] = None
    
    class Config:
        from_attributes = True
