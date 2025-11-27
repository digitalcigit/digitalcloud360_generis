"""Module models for Genesis AI Service"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class UserModule(BaseModel):
    """User module model"""
    __tablename__ = "user_modules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_type = Column(String, nullable=False)
    config = Column(JSON, default={})
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", backref="modules")
