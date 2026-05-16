"""
Enterprise Authentication & Authorization Service
===============================================
JWT-based authentication with RBAC, rate limiting, and security best practices.
Based on standards from Auth0, Firebase Auth, and enterprise security frameworks.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
import structlog

logger = structlog.get_logger(__name__)


class UserRole(Enum):
    """User roles with hierarchical permissions."""
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"
    GUEST = "guest"


class Permission(Enum):
    """System permissions."""
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    DELETE_DATA = "delete_data"
    MANAGE_USERS = "manage_users"
    TRADE_EXECUTION = "trade_execution"
    API_ACCESS = "api_access"
    ADMIN_PANEL = "admin_panel"


@dataclass
class User:
    """User model."""
    id: str
    email: str
    username: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None
    api_key: Optional[str] = None
    rate_limit: int = 1000  # requests per hour


@dataclass
class AuthConfig:
    """Authentication configuration."""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    redis_url: str = "redis://localhost:6379/1"
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15


class AuthService:
    """Enterprise authentication service."""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.redis_client = redis.from_url(config.redis_url, decode_responses=True)
        self.security = HTTPBearer()
        
        # Role-based permission mapping
        self.role_permissions = {
            UserRole.ADMIN: [
                Permission.READ_DATA, Permission.WRITE_DATA, Permission.DELETE_DATA,
                Permission.MANAGE_USERS, Permission.TRADE_EXECUTION, Permission.API_ACCESS,
                Permission.ADMIN_PANEL
            ],
            UserRole.TRADER: [
                Permission.READ_DATA, Permission.WRITE_DATA, Permission.TRADE_EXECUTION,
                Permission.API_ACCESS
            ],
            UserRole.VIEWER: [
                Permission.READ_DATA, Permission.API_ACCESS
            ],
            UserRole.GUEST: [
                Permission.READ_DATA
            ]
        }
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes)
        payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
    
    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=self.config.refresh_token_expire_days)
        payload = {
            "sub": user.id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with credentials."""
        # Check for login attempts
        attempts_key = f"login_attempts:{email}"
        attempts = int(self.redis_client.get(attempts_key) or 0)
        
        if attempts >= self.config.max_login_attempts:
            lockout_key = f"lockout:{email}"
            if self.redis_client.exists(lockout_key):
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account temporarily locked due to too many failed attempts"
                )
        
        # Get user from database (mock implementation)
        user = self._get_user_by_email(email)
        if not user or not self.verify_password(password, user.hashed_password):
            # Increment failed attempts
            self.redis_client.incr(attempts_key)
            self.redis_client.expire(attempts_key, self.config.lockout_duration_minutes * 60)
            
            # Lock account if max attempts reached
            if attempts + 1 >= self.config.max_login_attempts:
                lockout_key = f"lockout:{email}"
                self.redis_client.setex(lockout_key, self.config.lockout_duration_minutes * 60, "1")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Reset attempts on successful login
        self.redis_client.delete(attempts_key)
        user.last_login = datetime.utcnow()
        
        logger.info("User authenticated successfully", email=email, user_id=user.id)
        return user
    
    def check_rate_limit(self, user_id: str, api_key: Optional[str] = None) -> bool:
        """Check if user has exceeded rate limit."""
        key = f"rate_limit:{user_id}" if not api_key else f"rate_limit_api:{api_key}"
        current = int(self.redis_client.get(key) or 0)
        
        if current >= 1000:  # Default rate limit
            return False
        
        # Increment counter
        self.redis_client.incr(key)
        self.redis_client.expire(key, 3600)  # 1 hour
        return True
    
    def has_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has specific permission."""
        return permission in user.permissions
    
    def require_permission(self, permission: Permission):
        """Decorator to require specific permission."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                current_user = kwargs.get('current_user')
                if not current_user or not self.has_permission(current_user, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions"
                    )
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email (mock implementation)."""
        # In production, this would query your database
        # This is a mock implementation
        return None


class APIKeyAuth:
    """API Key authentication for service-to-service communication."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    def generate_api_key(self, user_id: str, name: str) -> str:
        """Generate new API key."""
        api_key = f"fm_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Store API key metadata
        self.redis_client.hset(
            f"api_key:{key_hash}",
            mapping={
                "user_id": user_id,
                "name": name,
                "created_at": datetime.utcnow().isoformat(),
                "last_used": None,
                "usage_count": "0"
            }
        )
        
        logger.info("API key generated", user_id=user_id, name=name)
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate API key and return user ID."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        data = self.redis_client.hgetall(f"api_key:{key_hash}")
        
        if not data:
            return None
        
        # Update usage
        self.redis_client.hincrby(f"api_key:{key_hash}", "usage_count", 1)
        self.redis_client.hset(f"api_key:{key_hash}", "last_used", datetime.utcnow().isoformat())
        
        return data.get("user_id")


# Dependency for FastAPI
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    auth_service: AuthService = Depends()
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Get user from database
    user = auth_service._get_user_by_id(payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user
