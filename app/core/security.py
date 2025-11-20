"""JWT token handling and security utilities"""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config.settings import settings

ALGORITHM = "HS256"

class TokenData(BaseModel):
    """Data model for JWT token payload"""
    user_id: Optional[int] = None

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt. Truncate to 72 bytes max (bcrypt limit)."""
    # Bcrypt has a 72 byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash. Truncate to 72 bytes max (bcrypt limit)."""
    # Bcrypt has a 72 byte limit, truncate if necessary
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate an access token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return TokenData(user_id=user_id)
    except JWTError:
        return None