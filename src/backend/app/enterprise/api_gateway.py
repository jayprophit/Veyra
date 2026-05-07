"""
Enterprise API Gateway
=====================
Kong/Tyk-style API Gateway with rate limiting, authentication, and routing
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import hashlib
import aiohttp
from fastapi import HTTPException, Request, Response
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RateLimitType(Enum):
    """Rate limit types"""
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    CONCURRENT_REQUESTS = "concurrent_requests"


@dataclass
class RateLimitRule:
    """Rate limit rule definition"""
    name: str
    limit_type: RateLimitType
    limit: int
    window_seconds: int
    scope: str  # global, user, ip, api_key
    conditions: Optional[Dict[str, Any]] = None


@dataclass
class RouteConfig:
    """Route configuration"""
    path: str
    methods: List[str]
    upstream_url: str
    timeout: int
    retries: int
    rate_limits: List[RateLimitRule]
    authentication_required: bool
    plugins: List[str]


@dataclass
class APIKey:
    """API key configuration"""
    key_id: str
    key_hash: str
    user_id: str
    permissions: List[str]
    rate_limits: List[RateLimitRule]
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool


class APIGateway:
    """Enterprise API Gateway with advanced features"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client: Optional[redis.Redis] = None
        self.routes: Dict[str, RouteConfig] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.rate_limit_counters: Dict[str, Dict] = {}
        self.request_logs: List[Dict] = []
        
        # Initialize default routes
        self._initialize_default_routes()
        
    async def initialize(self):
        """Initialize the API gateway"""
        try:
            self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
            await self.redis_client.ping()
            logger.info("API Gateway initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize API Gateway: {e}")
            raise
            
    def _initialize_default_routes(self):
        """Initialize default routes"""
        self.routes = {
            "/api/v1/trading": RouteConfig(
                path="/api/v1/trading",
                methods=["GET", "POST", "PUT", "DELETE"],
                upstream_url="http://trading-service:8001",
                timeout=30,
                retries=3,
                rate_limits=[
                    RateLimitRule(
                        name="trading_requests_per_minute",
                        limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                        limit=100,
                        window_seconds=60,
                        scope="user"
                    ),
                    RateLimitRule(
                        name="trading_concurrent",
                        limit_type=RateLimitType.CONCURRENT_REQUESTS,
                        limit=10,
                        window_seconds=1,
                        scope="user"
                    )
                ],
                authentication_required=True,
                plugins=["request_validation", "response_transformation"]
            ),
            "/api/v1/portfolio": RouteConfig(
                path="/api/v1/portfolio",
                methods=["GET", "POST", "PUT", "DELETE"],
                upstream_url="http://portfolio-service:8002",
                timeout=15,
                retries=2,
                rate_limits=[
                    RateLimitRule(
                        name="portfolio_requests_per_minute",
                        limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                        limit=200,
                        window_seconds=60,
                        scope="user"
                    )
                ],
                authentication_required=True,
                plugins=["caching", "compression"]
            ),
            "/api/v1/market-data": RouteConfig(
                path="/api/v1/market-data",
                methods=["GET"],
                upstream_url="http://market-data-service:8003",
                timeout=10,
                retries=2,
                rate_limits=[
                    RateLimitRule(
                        name="market_data_requests_per_minute",
                        limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                        limit=1000,
                        window_seconds=60,
                        scope="global"
                    )
                ],
                authentication_required=False,
                plugins=["caching", "compression"]
            ),
            "/api/v1/auth": RouteConfig(
                path="/api/v1/auth",
                methods=["POST"],
                upstream_url="http://auth-service:8004",
                timeout=5,
                retries=1,
                rate_limits=[
                    RateLimitRule(
                        name="auth_requests_per_minute",
                        limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                        limit=50,
                        window_seconds=60,
                        scope="ip"
                    )
                ],
                authentication_required=False,
                plugins=["request_validation"]
            )
        }
        
    async def process_request(self, request: Request) -> Response:
        """Process incoming request through gateway"""
        try:
            start_time = time.time()
            
            # Find matching route
            route = self._find_route(request)
            if not route:
                raise HTTPException(status_code=404, detail="Route not found")
                
            # Apply authentication if required
            user_context = await self._authenticate_request(request, route)
            
            # Apply rate limiting
            await self._check_rate_limits(request, route, user_context)
            
            # Apply plugins
            request = await self._apply_request_plugins(request, route)
            
            # Forward to upstream service
            response = await self._forward_request(request, route)
            
            # Apply response plugins
            response = await self._apply_response_plugins(response, route)
            
            # Log request
            await self._log_request(request, response, route, user_context, start_time)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
            
    def _find_route(self, request: Request) -> Optional[RouteConfig]:
        """Find matching route for request"""
        path = request.url.path
        method = request.method
        
        # Exact match first
        if path in self.routes and method in self.routes[path].methods:
            return self.routes[path]
            
        # Pattern matching
        for route_path, route_config in self.routes.items():
            if self._path_matches(path, route_path) and method in route_config.methods:
                return route_config
                
        return None
        
    def _path_matches(self, request_path: str, route_path: str) -> bool:
        """Check if request path matches route pattern"""
        # Simple pattern matching - in production would use regex
        if route_path.endswith("*"):
            return request_path.startswith(route_path[:-1])
        return request_path == route_path
        
    async def _authenticate_request(self, request: Request, route: RouteConfig) -> Optional[Dict[str, Any]]:
        """Authenticate request if required"""
        if not route.authentication_required:
            return None
            
        # Check API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return await self._authenticate_api_key(api_key)
            
        # Check JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return await self._authenticate_jwt_token(token)
            
        raise HTTPException(status_code=401, detail="Authentication required")
        
    async def _authenticate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Authenticate API key"""
        try:
            # Hash the provided key
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Find matching API key
            for key_id, key_config in self.api_keys.items():
                if key_config.key_hash == key_hash and key_config.is_active:
                    # Check expiration
                    if key_config.expires_at and key_config.expires_at < datetime.now():
                        raise HTTPException(status_code=401, detail="API key expired")
                        
                    return {
                        "user_id": key_config.user_id,
                        "key_id": key_id,
                        "permissions": key_config.permissions
                    }
                    
            raise HTTPException(status_code=401, detail="Invalid API key")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating API key: {e}")
            raise HTTPException(status_code=500, detail="Authentication error")
            
    async def _authenticate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Authenticate JWT token"""
        try:
            # Mock JWT validation - in production would use proper JWT library
            import jwt
            
            # Decode token (mock implementation)
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
            
            return {
                "user_id": payload.get("user_id"),
                "permissions": payload.get("permissions", [])
            }
            
        except Exception as e:
            logger.error(f"Error authenticating JWT token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
            
    async def _check_rate_limits(self, request: Request, route: RouteConfig, user_context: Optional[Dict[str, Any]]):
        """Check rate limits"""
        try:
            for rule in route.rate_limits:
                await self._check_single_rate_limit(request, rule, user_context)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            raise HTTPException(status_code=500, detail="Rate limiting error")
            
    async def _check_single_rate_limit(self, request: Request, rule: RateLimitRule, user_context: Optional[Dict[str, Any]]):
        """Check single rate limit rule"""
        # Determine scope key
        if rule.scope == "global":
            scope_key = f"global:{rule.name}"
        elif rule.scope == "user" and user_context:
            scope_key = f"user:{user_context['user_id']}:{rule.name}"
        elif rule.scope == "ip":
            scope_key = f"ip:{request.client.host}:{rule.name}"
        elif rule.scope == "api_key" and user_context:
            scope_key = f"api_key:{user_context.get('key_id')}:{rule.name}"
        else:
            return  # Skip if scope cannot be determined
            
        if self.redis_client:
            # Use Redis for distributed rate limiting
            await self._check_redis_rate_limit(scope_key, rule)
        else:
            # Use in-memory rate limiting
            await self._check_memory_rate_limit(scope_key, rule)
            
    async def _check_redis_rate_limit(self, scope_key: str, rule: RateLimitRule):
        """Check rate limit using Redis"""
        try:
            current_time = int(time.time())
            window_start = current_time - rule.window_seconds
            
            # Use sliding window algorithm
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(scope_key, 0, window_start)
            
            # Count current requests
            pipe.zcard(scope_key)
            
            # Add current request
            pipe.zadd(scope_key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(scope_key, rule.window_seconds)
            
            results = await pipe.execute()
            current_count = results[1]
            
            if current_count >= rule.limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {rule.limit} requests per {rule.window_seconds} seconds"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking Redis rate limit: {e}")
            
    async def _check_memory_rate_limit(self, scope_key: str, rule: RateLimitRule):
        """Check rate limit using in-memory storage"""
        try:
            current_time = time.time()
            window_start = current_time - rule.window_seconds
            
            # Initialize counter if not exists
            if scope_key not in self.rate_limit_counters:
                self.rate_limit_counters[scope_key] = {"requests": [], "count": 0}
                
            counter = self.rate_limit_counters[scope_key]
            
            # Remove old requests
            counter["requests"] = [req_time for req_time in counter["requests"] if req_time > window_start]
            counter["count"] = len(counter["requests"])
            
            # Check limit
            if counter["count"] >= rule.limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {rule.limit} requests per {rule.window_seconds} seconds"
                )
                
            # Add current request
            counter["requests"].append(current_time)
            counter["count"] += 1
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking memory rate limit: {e}")
            
    async def _apply_request_plugins(self, request: Request, route: RouteConfig) -> Request:
        """Apply request plugins"""
        for plugin_name in route.plugins:
            request = await self._apply_plugin(plugin_name, "request", request)
        return request
        
    async def _apply_response_plugins(self, response: Response, route: RouteConfig) -> Response:
        """Apply response plugins"""
        for plugin_name in route.plugins:
            response = await self._apply_plugin(plugin_name, "response", response)
        return response
        
    async def _apply_plugin(self, plugin_name: str, phase: str, data) -> Any:
        """Apply specific plugin"""
        try:
            if plugin_name == "request_validation":
                return await self._plugin_request_validation(data)
            elif plugin_name == "caching":
                return await self._plugin_caching(data, phase)
            elif plugin_name == "compression":
                return await self._plugin_compression(data, phase)
            elif plugin_name == "response_transformation":
                return await self._plugin_response_transformation(data)
            else:
                return data
        except Exception as e:
            logger.error(f"Error applying plugin {plugin_name}: {e}")
            return data
            
    async def _plugin_request_validation(self, request: Request) -> Request:
        """Request validation plugin"""
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=413, detail="Request too large")
            
        # Validate content type
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith(("application/json", "application/x-www-form-urlencoded", "multipart/form-data")):
                raise HTTPException(status_code=415, detail="Unsupported media type")
                
        return request
        
    async def _plugin_caching(self, data: Any, phase: str) -> Any:
        """Caching plugin"""
        if phase == "request":
            # Check cache for GET requests
            if isinstance(data, Request) and data.method == "GET":
                cache_key = f"cache:{data.url.path}:{data.url.query}"
                if self.redis_client:
                    cached_response = await self.redis_client.get(cache_key)
                    if cached_response:
                        return Response(content=cached_response, status_code=200)
        return data
        
    async def _plugin_compression(self, data: Any, phase: str) -> Any:
        """Compression plugin"""
        if phase == "response":
            # Compress response if client accepts gzip
            if isinstance(data, Response):
                accept_encoding = data.headers.get("accept-encoding", "")
                if "gzip" in accept_encoding:
                    # In production, would actually compress the content
                    data.headers["content-encoding"] = "gzip"
        return data
        
    async def _plugin_response_transformation(self, data: Any) -> Any:
        """Response transformation plugin"""
        if isinstance(data, Response):
            # Add standard headers
            data.headers["X-Gateway-Request-ID"] = str(int(time.time()))
            data.headers["X-Gateway-Processing-Time"] = "0.05"
        return data
        
    async def _forward_request(self, request: Request, route: RouteConfig) -> Response:
        """Forward request to upstream service"""
        try:
            # Build upstream URL
            upstream_url = f"{route.upstream_url}{request.url.path}"
            if request.url.query:
                upstream_url += f"?{request.url.query}"
                
            # Prepare headers
            headers = dict(request.headers)
            headers.pop("host", None)  # Remove host header
            
            # Make request to upstream
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=route.timeout)) as session:
                if request.method == "GET":
                    async with session.get(upstream_url, headers=headers) as response:
                        content = await response.read()
                        return Response(
                            content=content,
                            status_code=response.status,
                            headers=dict(response.headers)
                        )
                elif request.method == "POST":
                    content = await request.body()
                    async with session.post(upstream_url, headers=headers, data=content) as response:
                        content = await response.read()
                        return Response(
                            content=content,
                            status_code=response.status,
                            headers=dict(response.headers)
                        )
                # Add other methods as needed
                
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Gateway timeout")
        except Exception as e:
            logger.error(f"Error forwarding request: {e}")
            raise HTTPException(status_code=502, detail="Bad gateway")
            
    async def _log_request(self, request: Request, response: Response, route: RouteConfig, 
                          user_context: Optional[Dict[str, Any]], start_time: float):
        """Log request for monitoring and analytics"""
        try:
            processing_time = time.time() - start_time
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "query": request.url.query,
                "status_code": response.status_code,
                "processing_time": processing_time,
                "upstream": route.upstream_url,
                "user_id": user_context.get("user_id") if user_context else None,
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "content_length": response.headers.get("content-length")
            }
            
            self.request_logs.append(log_entry)
            
            # Keep only last 10000 logs in memory
            if len(self.request_logs) > 10000:
                self.request_logs = self.request_logs[-10000:]
                
            # Log to file or monitoring system
            logger.info(f"Request processed: {request.method} {request.url.path} - {response.status_code} ({processing_time:.3f}s)")
            
        except Exception as e:
            logger.error(f"Error logging request: {e}")
            
    def add_api_key(self, key_id: str, api_key: str, user_id: str, permissions: List[str], 
                   expires_at: Optional[datetime] = None):
        """Add new API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        self.api_keys[key_id] = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            user_id=user_id,
            permissions=permissions,
            rate_limits=[],
            created_at=datetime.now(),
            expires_at=expires_at,
            is_active=True
        )
        
    def revoke_api_key(self, key_id: str):
        """Revoke API key"""
        if key_id in self.api_keys:
            self.api_keys[key_id].is_active = False
            
    def get_gateway_stats(self) -> Dict[str, Any]:
        """Get gateway statistics"""
        recent_logs = [log for log in self.request_logs if 
                      datetime.fromisoformat(log["timestamp"]) > datetime.now() - timedelta(hours=1)]
        
        return {
            "total_requests": len(self.request_logs),
            "requests_last_hour": len(recent_logs),
            "active_routes": len(self.routes),
            "active_api_keys": len([k for k in self.api_keys.values() if k.is_active]),
            "average_response_time": sum(log["processing_time"] for log in recent_logs) / len(recent_logs) if recent_logs else 0,
            "status_codes": {log["status_code"]: recent_logs.count(log["status_code"]) for log in recent_logs}
        }


# Global API gateway instance
_api_gateway = None

def get_api_gateway() -> APIGateway:
    """Get the global API gateway instance"""
    global _api_gateway
    if _api_gateway is None:
        _api_gateway = APIGateway()
    return _api_gateway
