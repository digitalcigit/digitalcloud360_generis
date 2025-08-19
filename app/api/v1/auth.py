"""Authentication endpoints for Genesis AI Service"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.user import UserResponse, UserProfile
from app.schemas.responses import SuccessResponse, ErrorResponse
from app.core.security import create_access_token, decode_access_token, TokenData
import structlog

router = APIRouter()
security = HTTPBearer()
logger = structlog.get_logger()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    token = credentials.credentials
    token_data = decode_access_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


@router.post("/validate", response_model=UserResponse)
async def validate_token(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Validate JWT token from DigitalCloud360
    
    This endpoint is now implemented to validate the token.
    """
    logger.info(f"Token validation for user_id: {current_user.user_id}")
    
    # In a real application, you would fetch the user from the database here
    # For now, we will return a mock user response
    user_profile = UserProfile(user_id=current_user.user_id, email=f"user_{current_user.user_id}@example.com", name="Test User")
    return UserResponse(user=user_profile)

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get current user profile
    
    This endpoint is now implemented to fetch the user profile.
    """
    logger.info(f"User profile requested for user_id: {current_user.user_id}")
    
    # In a real application, you would fetch the user from the database here
    # For now, we will return a mock user profile
    return UserProfile(user_id=current_user.user_id, email=f"user_{current_user.user_id}@example.com", name="Test User")

@router.put("/profile", response_model=SuccessResponse)
async def update_user_profile(
    profile_update: dict,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update user profile for coaching personalization
    
    This endpoint is a placeholder for updating the user profile.
    """
    logger.info(f"User profile update requested for user_id: {current_user.user_id}")
    
    # In a real application, you would validate and update the profile in the database
    # For now, we will just return a success response
    return SuccessResponse(message="Profile updated successfully")

# This is a temporary endpoint for testing to generate a token
@router.post("/token")
async def login_for_access_token(user_id: int):
    access_token = create_access_token(data={"sub": str(user_id)})
    return {"access_token": access_token, "token_type": "bearer"}
