"""
Enterprise Rate Limiting & Caching Middleware
=============================================
Advanced rate limiting with Redis, sliding windows, and intelligent caching.
Based on patterns from Cloudflare, AWS API Gateway, and enterprise CDN solutions.
"""

import time
import json
import hashlib
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import redis
import aioredis
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class RateLimitType(Enum):
    """Rate limit types."""
    IP_BASED = "ip"
    USER_BASED = "user"
    API_KEY_BASED = "api_key"
    ENDPOINT_BASED = "endpoint"


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10
    penalty_seconds: int = 60


@dataclass
class CacheConfig:
    """Cache configuration."""
    default_ttl: int = 300  # 5 minutes
    max_ttl: int = 3600  # 1 hour
    cacheable_status_codes: List[int] = None
    cache_key_prefix: str = "fm_cache"
    
    def __post_init__(self):
        if self.cacheable_status_codes is None:
            self.cacheable_status_codes = [200, 301, 302, 404]


class RateLimiter:
    """Advanced rate limiter with sliding window algorithm."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.configs = {
            RateLimitType.IP_BASED: RateLimitConfig(
                requests_per_minute=30,
                requests_per_hour=500,
                requests_per_day=5000
            ),
            RateLimitType.USER_BASED: RateLimitConfig(
                requests_per_minute=100,
                requests_per_hour=2000,
                requests_per_day=20000
            ),
            RateLimitType.API_KEY_BASED: RateLimitConfig(
                requests_per_minute=1000,
                requests_per_hour=10000,
                requests_per_day=100000
            ),
            RateLimitType.ENDPOINT_BASED: RateLimitConfig(
                requests_per_minute=200,
                requests_per_hour=5000,
                requests_per_day=50000
            )
        }
    
    def _get_key(self, identifier: str, limit_type: RateLimitType, window: str) -> str:
        """Generate Redis key for rate limiting."""
        return f"rate_limit:{limit_type.value}:{identifier}:{window}"
    
    def _is_allowed(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int,
        burst_size: int = 0
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed using sliding window."""
        now = time.time()
        window_start = now - window_seconds
        
        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_count = self.redis_client.zcard(key)
        
        # Check burst limit
        if burst_size > 0 and current_count >= burst_size:
            # Check if we're still in burst window
            oldest_request = self.redis_client.zrange(key, 0, 0, withscores=True)
            if oldest_request and now - oldest_request[0][1] < 1:  # 1 second burst window
                return False, {
                    "current": current_count,
                    "limit": limit,
                    "window": window_seconds,
                    "retry_after": 1
                }
        
        # Check rate limit
        if current_count >= limit:
            # Calculate retry after
            oldest_request = self.redis_client.zrange(key, 0, 0, withscores=True)
            retry_after = 0
            if oldest_request:
                retry_after = int(window_seconds - (now - oldest_request[0][1]))
            
            return False, {
                "current": current_count,
                "limit": limit,
                "window": window_seconds,
                "retry_after": max(retry_after, 1)
            }
        
        # Add current request
        pipe = self.redis_client.pipeline()
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window_seconds)
        pipe.execute()
        
        return True, {
            "current": current_count + 1,
            "limit": limit,
            "window": window_seconds,
            "remaining": limit - current_count - 1
        }
    
    def check_rate_limit(
        self,
        identifier: str,
        limit_type: RateLimitType,
        request_time: datetime = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit for identifier."""
        config = self.configs[limit_type]
        now = request_time or datetime.utcnow()
        
        # Check minute limit
        minute_key = self._get_key(identifier, limit_type, "minute")
        allowed, info = self._is_allowed(minute_key, config.requests_per_minute, 60, config.burst_size)
        
        if not allowed:
            logger.warning(
                "Rate limit exceeded (minute)",
                identifier=identifier,
                limit_type=limit_type.value,
                current=info["current"],
                limit=info["limit"]
            )
            return False, info
        
        # Check hour limit
        hour_key = self._get_key(identifier, limit_type, "hour")
        allowed, info = self._is_allowed(hour_key, config.requests_per_hour, 3600)
        
        if not allowed:
            logger.warning(
                "Rate limit exceeded (hour)",
                identifier=identifier,
                limit_type=limit_type.value,
                current=info["current"],
                limit=info["limit"]
            )
            return False, info
        
        # Check day limit
        day_key = self._get_key(identifier, limit_type, "day")
        allowed, info = self._is_allowed(day_key, config.requests_per_day, 86400)
        
        if not allowed:
            logger.warning(
                "Rate limit exceeded (day)",
                identifier=identifier,
                limit_type=limit_type.value,
                current=info["current"],
                limit=info["limit"]
            )
            return False, info
        
        return True, info


class CacheManager:
    """Intelligent caching manager."""
    
    def __init__(self, redis_client: redis.Redis, config: CacheConfig):
        self.redis_client = redis_client
        self.config = config
    
    def _generate_cache_key(
        self,
        request: Request,
        user_id: Optional[str] = None
    ) -> str:
        """Generate cache key for request."""
        # Include method, path, and relevant query parameters
        key_parts = [
            self.config.cache_key_prefix,
            request.method.lower(),
            request.url.path
        ]
        
        # Add user context for personalized responses
        if user_id:
            key_parts.append(f"user:{user_id}")
        
        # Add relevant query parameters (exclude pagination, timestamps)
        query_params = []
        for param, value in request.query_params.items():
            if param not in ["page", "limit", "offset", "timestamp", "_t"]:
                query_params.append(f"{param}={value}")
        
        if query_params:
            key_parts.append("&".join(sorted(query_params)))
        
        key = ":".join(key_parts)
        # Hash long keys
        if len(key) > 200:
            key = hashlib.md5(key.encode()).hexdigest()
        
        return key
    
    def should_cache(
        self,
        request: Request,
        response: Response,
        ttl: Optional[int] = None
    ) -> bool:
        """Determine if response should be cached."""
        # Only cache GET requests
        if request.method.upper() != "GET":
            return False
        
        # Check status code
        if response.status_code not in self.config.cacheable_status_codes:
            return False
        
        # Check cache control headers
        cache_control = response.headers.get("cache-control", "")
        if "no-cache" in cache_control or "private" in cache_control:
            return False
        
        # Check content type (cache only JSON and text)
        content_type = response.headers.get("content-type", "")
        if not any(ct in content_type for ct in ["application/json", "text/"]):
            return False
        
        return True
    
    def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                logger.debug("Cache hit", key=cache_key)
                return data
        except Exception as e:
            logger.error("Cache get error", key=cache_key, error=str(e))
        
        logger.debug("Cache miss", key=cache_key)
        return None
    
    def cache_response(
        self,
        cache_key: str,
        response_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """Cache response data."""
        try:
            ttl = ttl or self.config.default_ttl
            ttl = min(ttl, self.config.max_ttl)
            
            cached_data = json.dumps(response_data, default=str)
            self.redis_client.setex(cache_key, ttl, cached_data)
            
            logger.debug("Response cached", key=cache_key, ttl=ttl)
        except Exception as e:
            logger.error("Cache set error", key=cache_key, error=str(e))
    
    def invalidate_cache_pattern(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern."""
        try:
            keys = self.redis_client.keys(f"{self.config.cache_key_prefix}:{pattern}*")
            if keys:
                self.redis_client.delete(*keys)
                logger.info("Cache invalidated", pattern=pattern, count=len(keys))
        except Exception as e:
            logger.error("Cache invalidation error", pattern=pattern, error=str(e))


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Rate limiting and caching middleware."""
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.rate_limiter = RateLimiter(redis_client)
        self.cache_manager = CacheManager(redis_client, CacheConfig())
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting and caching."""
        # Get client identifier
        client_ip = self._get_client_ip(request)
        user_id = getattr(request.state, "user_id", None)
        api_key = request.headers.get("X-API-Key")
        
        # Check rate limits
        await self._check_rate_limits(request, client_ip, user_id, api_key)
        
        # Check cache for GET requests
        if request.method.upper() == "GET":
            cache_key = self.cache_manager._generate_cache_key(request, user_id)
            cached_response = self.cache_manager.get_cached_response(cache_key)
            
            if cached_response:
                return JSONResponse(
                    content=cached_response["content"],
                    status_code=cached_response["status_code"],
                    headers=cached_response["headers"]
                )
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Cache response if applicable
        if request.method.upper() == "GET":
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            response_data = {
                "content": json.loads(response_body.decode()) if response_body else {},
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
            
            if self.cache_manager.should_cache(request, response):
                self.cache_manager.cache_response(cache_key, response_data)
        
        # Add rate limit headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _check_rate_limits(
        self,
        request: Request,
        client_ip: str,
        user_id: Optional[str],
        api_key: Optional[str]
    ):
        """Check all applicable rate limits."""
        # IP-based rate limiting
        allowed, info = self.rate_limiter.check_rate_limit(client_ip, RateLimitType.IP_BASED)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["retry_after"]),
                    "Retry-After": str(info["retry_after"])
                }
            )
        
        # User-based rate limiting
        if user_id:
            allowed, info = self.rate_limiter.check_rate_limit(user_id, RateLimitType.USER_BASED)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="User rate limit exceeded",
                    headers={"Retry-After": str(info["retry_after"])}
                )
        
        # API key rate limiting
        if api_key:
            allowed, info = self.rate_limiter.check_rate_limit(api_key, RateLimitType.API_KEY_BASED)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="API key rate limit exceeded",
                    headers={"Retry-After": str(info["retry_after"])}
                )
        
        # Endpoint-based rate limiting
        endpoint_key = f"{request.method}:{request.url.path}"
        allowed, info = self.rate_limiter.check_rate_limit(endpoint_key, RateLimitType.ENDPOINT_BASED)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Endpoint rate limit exceeded",
                headers={"Retry-After": str(info["retry_after"])}
            )
