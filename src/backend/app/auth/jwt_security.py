"""
JWT Authentication & Security System
=====================================
Secure authentication with JWT tokens, password hashing, and user management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import logging
from functools import wraps

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class UserLogin(BaseModel):
    """User login credentials"""
    username: str
    password: str


class UserCreate(BaseModel):
    """User registration"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User public data"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenPayload(BaseModel):
    """JWT payload"""
    sub: str  # user_id
    exp: datetime
    iat: datetime
    type: str  # access, refresh


# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN HANDLING
# ============================================================================

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    token = encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access token created for user {user_id}")
    return token


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    token = encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Refresh token created for user {user_id}")
    return token


def verify_token(token: str, token_type: str = "access") -> Optional[int]:
    """Verify JWT token and return user_id"""
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None
        
        user_id = int(payload.get("sub"))
        logger.debug(f"Token verified for user {user_id}")
        return user_id
        
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return None


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT token without verification (for debugging)"""
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Dependency to extract and verify current user from JWT token
    Returns user_id if valid, raises HTTPException if invalid
    """
    token = credentials.credentials
    
    user_id = verify_token(token, token_type="access")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security) if credentials else None
) -> Optional[int]:
    """
    Optional dependency to extract user_id if token provided
    Returns user_id or None
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    user_id = verify_token(token, token_type="access")
    return user_id


# ============================================================================
# DECORATORS
# ============================================================================

def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(*args, current_user: int = Depends(get_current_user), **kwargs):
        kwargs['current_user'] = current_user
        return await func(*args, **kwargs)
    return wrapper


def require_admin(func):
    """Decorator to require admin privileges"""
    @wraps(func)
    async def wrapper(*args, current_user: int = Depends(get_current_user), **kwargs):
        # In production, check user.is_admin from database
        # For now, just verify user exists
        kwargs['current_user'] = current_user
        return await func(*args, **kwargs)
    return wrapper


# ============================================================================
# SECURITY UTILITIES
# ============================================================================

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    import secrets
    return secrets.token_urlsafe(length)


def mask_sensitive_data(data: Dict[str, Any], fields_to_mask: list) -> Dict[str, Any]:
    """Mask sensitive fields in a dictionary for logging"""
    masked_data = data.copy()
    for field in fields_to_mask:
        if field in masked_data:
            masked_data[field] = "***MASKED***"
    return masked_data


# ============================================================================
# SECURITY HEADERS
# ============================================================================

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
}
