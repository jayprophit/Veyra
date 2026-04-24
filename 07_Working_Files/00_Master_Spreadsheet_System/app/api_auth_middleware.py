"""API Authentication Middleware - Production Ready

Integrates auth system with FastAPI endpoints:
- JWT validation on all protected routes
- Rate limiting per user
- Permission-based access control
- API key authentication for service accounts
"""

from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import redis
import json
from typing import Optional, List, Dict, Callable
import jwt

# Import auth system
from auth_security_system import (
    SSSSecurityManager, UserRole, Permission, 
    TokenData, get_security_manager
)

security = HTTPBearer()

class AuthMiddleware(BaseHTTPMiddleware):
    """Global authentication middleware"""
    
    def __init__(self, app: FastAPI, security_manager: SSSSecurityManager):
        super().__init__(app)
        self.security_manager = security_manager
        
        # Public paths that don't require auth
        self.public_paths = [
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/mfa/setup",
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Check if path is public
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)
        
        # Get authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        try:
            # Validate token
            token = auth_header.replace("Bearer ", "")
            token_data = self.security_manager.verify_token(token)
            
            # Check rate limit
            if not self.security_manager.check_rate_limit(
                token_data.user_id[:16], 
                "api"
            ):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Add user to request state
            request.state.user = token_data
            request.state.user_id = token_data.user_id
            
            # Log access
            self.security_manager.audit_log(
                user_id=token_data.user_id,
                action="api_access",
                details={
                    "path": request.url.path,
                    "method": request.method
                },
                ip_address=request.client.host if request.client else None
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        
        return await call_next(request)

def require_auth(security_manager: SSSSecurityManager = Depends(get_security_manager)):
    """Dependency to require authentication"""
    async def checker(credentials: HTTPAuthorizationCredentials = Security(security)):
        token = credentials.credentials
        return security_manager.verify_token(token)
    return checker

def require_permissions(*permissions: Permission):
    """Dependency to require specific permissions"""
    def permission_checker(user: TokenData = Depends(require_auth(get_security_manager()))):
        user_perms = set(user.permissions)
        required_perms = set(permissions)
        
        if not required_perms.issubset(user_perms):
            missing = [p.value for p in required_perms - user_perms]
            raise HTTPException(
                status_code=403,
                detail=f"Missing permissions: {missing}"
            )
        return user
    return permission_checker

def require_role(role: UserRole):
    """Dependency to require specific role"""
    def role_checker(user: TokenData = Depends(require_auth(get_security_manager()))):
        if user.role != role:
            raise HTTPException(
                status_code=403,
                detail=f"Required role: {role.value}"
            )
        return user
    return role_checker

# API Key authentication for service accounts
async def verify_api_key(request: Request):
    """Verify API key from header"""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    security_manager = get_security_manager()
    user = security_manager.verify_api_key(api_key)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return user

# Combined auth - JWT or API Key
async def get_current_user(request: Request):
    """Get current user from JWT or API key"""
    # Try API key first
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return await verify_api_key(request)
    
    # Fall back to JWT
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        security_manager = get_security_manager()
        return security_manager.verify_token(token)
    
    raise HTTPException(status_code=401, detail="Authentication required")

# Permission helper functions
def can_read_portfolio(user: TokenData = Depends(get_current_user)):
    if Permission.READ_PORTFOLIO not in user.permissions:
        raise HTTPException(status_code=403, detail="Cannot read portfolio")
    return user

def can_write_portfolio(user: TokenData = Depends(get_current_user)):
    if Permission.WRITE_PORTFOLIO not in user.permissions:
        raise HTTPException(status_code=403, detail="Cannot modify portfolio")
    return user

def can_trade(user: TokenData = Depends(get_current_user)):
    if Permission.EXECUTE_TRADES not in user.permissions:
        raise HTTPException(status_code=403, detail="Cannot execute trades")
    return user

def is_admin(user: TokenData = Depends(get_current_user)):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Rate limiting decorator
def rate_limit(requests: int, window: int):
    """Rate limit decorator for specific endpoints"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request and hasattr(request.state, 'user_id'):
                user_id = request.state.user_id
                security_manager = get_security_manager()
                
                if not security_manager.check_rate_limit(user_id, "custom"):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Setup function for FastAPI app
def setup_auth_middleware(app: FastAPI, security_manager: SSSSecurityManager = None):
    """Add auth middleware to FastAPI app"""
    if security_manager is None:
        security_manager = get_security_manager()
    
    # Add middleware
    app.add_middleware(AuthMiddleware, security_manager=security_manager)
    
    # Store security manager in app state
    app.state.security_manager = security_manager
    
    return app

# Example protected routes
if __name__ == "__main__":
    from fastapi import FastAPI
    
    app = FastAPI()
    security_mgr = SSSSecurityManager()
    
    # Setup middleware
    setup_auth_middleware(app, security_mgr)
    
    # Create test user
    admin = security_mgr.create_user(
        "admin@example.com",
        "SecurePass123!",
        UserRole.ADMIN
    )
    
    # Public route
    @app.get("/health")
    def health_check():
        return {"status": "healthy"}
    
    # Protected route - any authenticated user
    @app.get("/api/v1/portfolio")
    def get_portfolio(user: TokenData = Depends(can_read_portfolio)):
        return {
            "user_id": user.user_id,
            "message": "Portfolio data",
            "permissions": [p.value for p in user.permissions]
        }
    
    # Protected route - traders only
    @app.post("/api/v1/orders")
    def create_order(
        user: TokenData = Depends(can_trade),
        symbol: str = None,
        quantity: float = None
    ):
        return {
            "user_id": user.user_id,
            "order": {"symbol": symbol, "quantity": quantity},
            "status": "submitted"
        }
    
    # Admin only route
    @app.get("/api/v1/admin/users")
    def list_users(user: TokenData = Depends(is_admin)):
        return {"users": [], "admin": user.email}
    
    print("Auth middleware example loaded. Run with: uvicorn 41_API_Auth_Middleware:app")
