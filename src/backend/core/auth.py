"""
Authentication & Authorization System
Handles JWT tokens, password hashing, user sessions
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from fastapi import HTTPException

from src.backend.core.config import settings
from src.backend.app.database.models import User
from src.backend.app.database.session import get_db

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


class TokenData(BaseModel):
    """JWT token payload"""
    email: str
    user_id: Optional[int] = None
    exp: Optional[datetime] = None


class UserCredentials(BaseModel):
    """User login credentials"""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Authentication response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class AuthManager:
    """
    Centralized authentication management
    Handles JWT, password hashing, token validation
    """

    def __init__(self):
        """Initialize auth manager"""
        self.algorithm = settings.ALGORITHM
        self.secret_key = settings.SECRET_KEY
        self.access_token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = settings.REFRESH_TOKEN_EXPIRE_DAYS

        logger.info("✅ AuthManager initialized")

    # ========== PASSWORD HASHING ==========

    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        Args:
            password: Plain text password
        Returns:
            Hashed password
        """
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify that a plain password matches its hash
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against
        Returns:
            True if password matches, False otherwise
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False

    # ========== JWT TOKEN MANAGEMENT ==========

    def create_access_token(self, user_id: int, email: str) -> str:
        """
        Create JWT access token
        Args:
            user_id: User ID
            email: User email
        Returns:
            JWT token string
        """
        try:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire
            )
            to_encode = {
                "user_id": user_id,
                "email": email,
                "type": "access",
                "exp": expire
            }
            encoded_jwt = jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )
            logger.debug(f"Access token created for user: {email}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise

    def create_refresh_token(self, user_id: int, email: str) -> str:
        """
        Create JWT refresh token (longer expiration)
        Args:
            user_id: User ID
            email: User email
        Returns:
            JWT refresh token string
        """
        try:
            expire = datetime.utcnow() + timedelta(
                days=self.refresh_token_expire
            )
            to_encode = {
                "user_id": user_id,
                "email": email,
                "type": "refresh",
                "exp": expire
            }
            encoded_jwt = jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )
            logger.debug(f"Refresh token created for user: {email}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Refresh token creation failed: {e}")
            raise

    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verify and decode JWT token
        Args:
            token: JWT token string
        Returns:
            TokenData if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            email: str = payload.get("email")
            user_id: int = payload.get("user_id")

            if email is None:
                logger.warning("Token missing email claim")
                return None

            return TokenData(email=email, user_id=user_id)

        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with email and password against database
        Args:
            email: User email
            password: Plain text password
        Returns:
            Token data dict if authentication successful, None otherwise
        """
        logger.info(f"Authenticating user: {email}")
        
        try:
            # Get database session
            db = next(get_db())
            
            # Query user from database
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                logger.warning(f"Authentication failed: User not found - {email}")
                return None
            
            if not user.is_active:
                logger.warning(f"Authentication failed: User inactive - {email}")
                return None
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                logger.warning(f"Authentication failed: Invalid password - {email}")
                return None
            
            # Authentication successful - create tokens
            access_token = self.create_access_token(
                user_id=user.id,
                email=user.email
            )
            refresh_token = self.create_refresh_token(
                user_id=user.id,
                email=user.email
            )
            
            logger.info(f"Authentication successful: {user.email}")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
        finally:
            db.close()

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create new access token from refresh token
        Args:
            refresh_token: Valid refresh token
        Returns:
            New access token if successful, None if invalid
        """
        token_data = self.verify_token(refresh_token)
        if not token_data:
            logger.warning("Invalid refresh token")
            return None

        # Create new access token with same user info
        new_token = self.create_access_token(
            user_id=token_data.user_id,
            email=token_data.email
        )
        logger.info(f"Refresh token used by: {token_data.email}")
        return new_token

    def get_current_user_from_token(self, token: str) -> Optional[str]:
        """
        Extract email from valid token
        Args:
            token: JWT token
        Returns:
            Email if valid, None if invalid
        """
        token_data = self.verify_token(token)
        if not token_data:
            return None
        return token_data.email


# Create global auth manager instance
auth_manager = AuthManager()
