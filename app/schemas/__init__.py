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
from .site_definition import (
    SiteDefinition,
    SiteSection,
    SitePage,
    SiteMetadata,
    SiteTheme,
    BlockType,
    HeaderSectionContent,
    HeroSectionContent,
    AboutSectionContent,
    ServicesSectionContent,
    FeaturesSectionContent,
    TestimonialsSectionContent,
    ContactSectionContent,
    GallerySectionContent,
    CTASectionContent,
    FooterSectionContent,
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
    "SuccessResponse",
    "SiteDefinition",
    "SiteSection",
    "SitePage",
    "SiteMetadata",
    "SiteTheme",
    "BlockType",
    "HeaderSectionContent",
    "HeroSectionContent",
    "AboutSectionContent",
    "ServicesSectionContent",
    "FeaturesSectionContent",
    "TestimonialsSectionContent",
    "ContactSectionContent",
    "GallerySectionContent",
    "CTASectionContent",
    "FooterSectionContent",
]
