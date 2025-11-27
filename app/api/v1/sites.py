from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Dict, Any

from app.config.database import get_db
from app.models.site import Site, SiteStatusEnum
from app.models.coaching import BusinessBrief
from app.models.user import User
from app.api.v1.dependencies import get_current_user
from app.services.transformer import BriefToSiteTransformer

router = APIRouter()

# Request/Response schemas
class GenerateSiteRequest(BaseModel):
    brief_id: int

class GenerateSiteResponse(BaseModel):
    site_id: int
    status: str

@router.post("/generate", response_model=GenerateSiteResponse)
async def generate_site(
    request: GenerateSiteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a site from a business brief.
    """
    # Fetch the brief
    result = await db.execute(
        select(BusinessBrief).where(BusinessBrief.id == request.brief_id)
    )
    brief = result.scalar_one_or_none()
    
    if not brief:
        raise HTTPException(status_code=404, detail="Business brief not found")
    
    # Transform brief to site definition
    transformer = BriefToSiteTransformer()
    try:
        site_definition = transformer.transform(brief)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transform brief: {str(e)}")
    
    # Create site record
    site = Site(
        user_id=current_user.id,
        brief_id=brief.id,
        definition=site_definition,
        status=SiteStatusEnum.READY
    )
    
    db.add(site)
    await db.commit()
    await db.refresh(site)
    
    return GenerateSiteResponse(
        site_id=site.id,
        status=site.status.value
    )

@router.get("/{site_id}", response_model=Dict[str, Any])
async def get_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a site definition by ID.
    """
    result = await db.execute(
        select(Site).where(Site.id == site_id, Site.user_id == current_user.id)
    )
    site = result.scalar_one_or_none()
    
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    return site.definition
