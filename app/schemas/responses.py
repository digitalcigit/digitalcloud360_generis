"""Common response schemas"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment")
    timestamp: float = Field(..., description="Response timestamp")

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = Field(True, description="Operation success")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: float = Field(..., description="Response timestamp")

class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: float = Field(..., description="Error timestamp")

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: list = Field(..., description="List of items")
    total: int = Field(..., description="Total items count")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")
