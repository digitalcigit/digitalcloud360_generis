"""Pydantic schemas for Genesis AI Service APIs"""

from .user import UserProfile, UserCreate, UserResponse
from .coaching import (
    CoachingRequest, 
    CoachingResponse, 
    CoachingStepResponse,
    SessionCompleteResponse
)
from .business import BusinessBrief, BusinessBriefResponse
from .responses import (
    HealthResponse,
    ErrorResponse,
    SuccessResponse
)

__all__ = [
    "UserProfile",
    "UserCreate", 
    "UserResponse",
    "CoachingRequest",
    "CoachingResponse",
    "CoachingStepResponse", 
    "SessionCompleteResponse",
    "BusinessBrief",
    "BusinessBriefResponse",
    "HealthResponse",
    "ErrorResponse",
    "SuccessResponse"
]
