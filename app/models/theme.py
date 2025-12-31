"""Theme model for Genesis AI Service"""

from sqlalchemy import Column, String, JSON, Boolean, Text
from .base import BaseModel

class Theme(BaseModel):
    """Theme entity for website generation templates"""
    __tablename__ = "themes"

    # Theme identification
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False) # ex: "savor-pro"
    description = Column(Text)
    
    # Classification
    category = Column(String, nullable=False, index=True) # restaurant, real_estate, generic, etc.
    compatibility_tags = Column(JSON) # List of tags for matching ["luxury", "dark-mode", "visual"]
    
    # Features and Assets
    features = Column(JSON) # List of key features
    thumbnail_url = Column(String) # Preview image URL
    preview_url = Column(String) # Live preview URL (optional)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "category": self.category,
            "compatibility_tags": self.compatibility_tags,
            "features": self.features,
            "thumbnail_url": self.thumbnail_url,
            "preview_url": self.preview_url,
            "is_active": self.is_active,
            "is_premium": self.is_premium,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
