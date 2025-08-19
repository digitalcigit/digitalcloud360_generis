"""Business-related Pydantic schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

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

class BusinessBriefRequest(BaseModel):
    """Request schema for creating a business brief"""
    coaching_session_id: int
    business_brief: BusinessBrief

class BusinessBriefResponse(BaseModel):
    """Réponse avec brief business complet"""
    id: int
    coaching_session_id: int
    business_brief: BusinessBrief
    market_research: Optional[Dict[str, Any]] = None
    content_generation: Optional[Dict[str, Any]] = None
    logo_creation: Optional[Dict[str, Any]] = None
    seo_optimization: Optional[Dict[str, Any]] = None
    template_selection: Optional[Dict[str, Any]] = None
    overall_confidence: float
    is_ready_for_website: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class MarketResearchResult(BaseModel):
    """Résultat recherche marché"""
    market_size: Dict[str, Any] = Field(..., description="Taille marché")
    competitors: List[Dict[str, Any]] = Field(..., description="Concurrents")
    opportunities: List[Dict[str, Any]] = Field(..., description="Opportunités")
    pricing: Dict[str, Any] = Field(..., description="Données prix")
    cultural_insights: List[str] = Field(..., description="Insights culturels")

class ContentGenerationResult(BaseModel):
    """Résultat génération contenu"""
    homepage: Dict[str, Any] = Field(..., description="Contenu accueil")
    about: Dict[str, Any] = Field(..., description="Contenu à propos")
    services: Dict[str, Any] = Field(..., description="Contenu services")
    contact: Dict[str, Any] = Field(..., description="Contenu contact")
    seo_metadata: Dict[str, Any] = Field(..., description="Métadonnées SEO")
    languages_generated: List[str] = Field(..., description="Langues générées")

class LogoCreationResult(BaseModel):
    """Résultat création logo"""
    primary_logo: Dict[str, Any] = Field(..., description="Logo principal")
    alternatives: List[Dict[str, Any]] = Field(..., description="Alternatives")
    color_palette: List[str] = Field(..., description="Palette couleurs")
    brand_guidelines: Dict[str, Any] = Field(..., description="Guidelines marque")

class SEOOptimizationResult(BaseModel):
    """Résultat optimisation SEO"""
    primary_keywords: List[str] = Field(..., description="Mots-clés primaires")
    secondary_keywords: List[str] = Field(..., description="Mots-clés secondaires")
    local_seo_strategy: Dict[str, Any] = Field(..., description="Stratégie SEO local")
    meta_tags: Dict[str, str] = Field(..., description="Meta tags optimisées")

class TemplateSelectionResult(BaseModel):
    """Résultat sélection template"""
    primary_template: Dict[str, Any] = Field(..., description="Template principal")
    alternatives: List[Dict[str, Any]] = Field(..., description="Templates alternatifs")
    customizations: Dict[str, Any] = Field(..., description="Personnalisations recommandées")

class SubAgentResultsResponse(BaseModel):
    """Response with detailed results from all sub-agents"""
    market_research: Optional[MarketResearchResult] = None
    content_generation: Optional[ContentGenerationResult] = None
    logo_creation: Optional[LogoCreationResult] = None
    seo_optimization: Optional[SEOOptimizationResult] = None
    template_selection: Optional[TemplateSelectionResult] = None
