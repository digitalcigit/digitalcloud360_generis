"""Site models for Genesis AI Service"""

from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class SiteStatusEnum(str, enum.Enum):
    """Site generation status"""
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"

class Site(BaseModel):
    """Generated site from business brief"""
    __tablename__ = "sites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brief_id = Column(Integer, ForeignKey("business_briefs.id"), nullable=False)
    
    # Site definition (JSON structure matching SiteDefinition interface)
    definition = Column(JSON, nullable=False)
    
    # Status tracking
    status = Column(Enum(SiteStatusEnum), default=SiteStatusEnum.GENERATING)
    
    # Relationships
    user = relationship("User", backref="sites")
    brief = relationship("BusinessBrief", backref="sites")
