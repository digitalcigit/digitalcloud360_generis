from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Any, Dict

from app.config.database import get_db
from app.models.module import UserModule
from app.models.user import User
from app.api.v1.dependencies import get_current_user

router = APIRouter()

@router.get("/my-modules", response_model=List[Dict[str, Any]])
async def get_my_modules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all modules for the current user.
    """
    result = await db.execute(
        select(UserModule).where(UserModule.user_id == current_user.id, UserModule.is_active == True)
    )
    modules = result.scalars().all()
    
    return [
        {
            "id": module.id,
            "module_type": module.module_type,
            "config": module.config,
            "is_active": module.is_active
        }
        for module in modules
    ]
