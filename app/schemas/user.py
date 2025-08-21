"""User-related Pydantic schemas"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr = Field(..., description="Email utilisateur")

class UserCreate(UserBase):
    """Schema for user creation"""
    name: str = Field(..., description="Nom de l'utilisateur")
    password: str = Field(..., min_length=8, description="Mot de passe")

class User(UserBase):
    """User schema for API responses"""
    id: int
    name: str

    model_config = {"from_attributes": True}

class UserProfile(BaseModel):
    """Profil utilisateur Genesis AI"""
    user_id: int = Field(..., description="ID utilisateur")
    
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

    model_config = {"from_attributes": True}

class UserResponse(User):
    """Response schema for user data, including profile"""
    profile: Optional[UserProfile] = None
