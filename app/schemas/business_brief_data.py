"""Pydantic model for BusinessBrief data from Redis.

Ce module définit un modèle Pydantic pour mapper les données BusinessBrief
stockées dans Redis vers un format utilisable par le Transformer.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ContentGenerationData(BaseModel):
    """Données générées par le ContentSubAgent"""
    hero_image: Optional[str] = None
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    about_text: Optional[str] = None
    services_descriptions: Optional[List[str]] = None


class LogoCreationData(BaseModel):
    """Données générées par le LogoSubAgent"""
    logo_url: Optional[str] = None
    logo_alt: Optional[str] = None


class SEOOptimizationData(BaseModel):
    """Données générées par le SEOSubAgent"""
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    keywords: Optional[List[str]] = None


class TemplateSelectionData(BaseModel):
    """Données générées par le TemplateSubAgent"""
    template_id: Optional[str] = None
    template_name: Optional[str] = None


class ServiceItem(BaseModel):
    """Un service individuel"""
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    price: Optional[str] = None


class BusinessBriefData(BaseModel):
    """
    Modèle Pydantic pour les données BusinessBrief depuis Redis.
    
    Utilisé par le BriefToSiteTransformer pour générer un SiteDefinition.
    """
    # Identité business
    business_name: str = Field(..., description="Nom de l'entreprise")
    sector: str = Field(default="default", description="Secteur d'activité")
    
    # Contenu stratégique (issu du coaching)
    mission: Optional[str] = Field(None, description="Mission de l'entreprise")
    vision: Optional[str] = Field(None, description="Vision de l'entreprise")
    value_proposition: Optional[str] = Field(None, description="Proposition de valeur")
    target_audience: Optional[str] = Field(None, description="Audience cible")
    differentiation: Optional[str] = Field(None, description="Différenciation")
    
    # Services
    services: List[ServiceItem] = Field(default_factory=list)
    
    # Contact
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    
    # Résultats sub-agents
    content_generation: Optional[ContentGenerationData] = None
    logo_creation: Optional[LogoCreationData] = None
    seo_optimization: Optional[SEOOptimizationData] = None
    template_selection: Optional[TemplateSelectionData] = None
    
    class Config:
        extra = "allow"  # Permet des champs additionnels
