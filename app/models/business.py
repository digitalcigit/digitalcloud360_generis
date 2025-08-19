"""Business-related models for Genesis AI Service"""

from sqlalchemy import Column, Integer, String, JSON, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Business(BaseModel):
    """Business entity created from coaching"""
    __tablename__ = "businesses"
    
    # Business identification
    business_name = Column(String, nullable=False, index=True)
    sector = Column(String, nullable=False, index=True)
    
    # Business owner
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Business details from coaching
    vision = Column(Text)
    mission = Column(Text)
    target_audience = Column(Text)
    differentiation = Column(Text)
    value_proposition = Column(Text)
    
    # Location and context
    location = Column(JSON)  # {"city": "Dakar", "country": "Sénégal"}
    cultural_context = Column(JSON)
    
    # Business status
    status = Column(String, default="draft")  # draft, active, paused
    
    # Relationships
    user = relationship("User")
    business_context = relationship("BusinessContext", back_populates="business", uselist=False)

class BusinessContext(BaseModel):
    """Extended business context and metadata"""
    __tablename__ = "business_contexts"
    
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Market analysis results
    market_size = Column(JSON)
    competitors = Column(JSON)
    opportunities = Column(JSON)
    pricing_insights = Column(JSON)
    
    # Generated assets
    logo_assets = Column(JSON)
    color_palette = Column(JSON)
    brand_guidelines = Column(JSON)
    
    # Content assets
    website_content = Column(JSON)
    seo_metadata = Column(JSON)
    marketing_content = Column(JSON)
    
    # Template and design
    selected_template = Column(String)
    customizations = Column(JSON)
    
    # Quality scores
    market_confidence = Column(Float, default=0.0)
    content_quality = Column(Float, default=0.0)
    brand_consistency = Column(Float, default=0.0)
    
    # Integration status
    dc360_integration_status = Column(String, default="pending")
    dc360_website_id = Column(Integer)
    
    # Relationships
    business = relationship("Business", back_populates="business_context")
