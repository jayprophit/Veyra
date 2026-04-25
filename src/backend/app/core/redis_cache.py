"""
Redis Caching Layer
====================
High-performance caching for:
- Market data
- API responses
- AI predictions
- Session data
- Rate limiting
"""

import json
import pickle
import hashlib
from typing import Optional, Any, Dict, List, Union
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis-backed caching manager.
    Falls back to in-memory dict if Redis unavailable.
    """
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 300):
        self.redis_url = redis_url or "redis://localhost:6379"
        self.default_ttl = default_ttl
        self._redis = None
        self._local_cache: Dict[str, tuple] = {}  # Fallback cache
        self._connected = False
        
    async def connect(self) -> bool:
        """Connect to Redis."""
        try:
            import redis.asyncio as redis
            self._redis = redis.from_url(self.redis_url, decode_responses=False)
            await self._redis.ping()
            self._connected = True
            logger.info("Connected to Redis")
            return True
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using local cache")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._redis and self._connected:
            await self._redis.close()
            self._connected = False
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps({
            'args': args,
            'kwargs': sorted(kwargs.items())
        }, sort_keys=True)
        
        hash_part = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{prefix}:{hash_part}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if self._connected and self._redis:
                data = await self._redis.get(key)
                if data:
                    return pickle.loads(data)
            else:
                # Local cache
                if key in self._local_cache:
                    value, expiry = self._local_cache[key]
                    if expiry > datetime.now():
                        return value
                    else:
                        del self._local_cache[key]
            
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        try:
            ttl = ttl or self.default_ttl
            
            if self._connected and self._redis:
                serialized = pickle.dumps(value)
                await self._redis.setex(key, ttl, serialized)
            else:
                # Local cache
                expiry = datetime.now() + timedelta(seconds=ttl)
                self._local_cache[key] = (value, expiry)
            
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self._connected and self._redis:
                await self._redis.delete(key)
            else:
                self._local_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if self._connected and self._redis:
                return await self._redis.exists(key) > 0
            else:
                if key in self._local_cache:
                    _, expiry = self._local_cache[key]
                    return expiry > datetime.now()
                return False
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            if self._connected and self._redis:
                keys = await self._redis.keys(pattern)
                if keys:
                    await self._redis.delete(*keys)
                return len(keys)
            else:
                # Local cache - find matching keys
                matching = [k for k in self._local_cache.keys() if pattern.replace('*', '') in k]
                for k in matching:
                    del self._local_cache[k]
                return len(matching)
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    # Specialized cache methods
    
    async def cache_market_data(self, symbol: str, data: Dict, ttl: int = 60):
        """Cache market data with short TTL."""
        key = f"market:{symbol}"
        await self.set(key, data, ttl)
    
    async def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get cached market data."""
        key = f"market:{symbol}"
        return await self.get(key)
    
    async def cache_ai_prediction(
        self,
        model: str,
        symbol: str,
        prediction: Any,
        ttl: int = 600
    ):
        """Cache AI prediction results."""
        key = f"ai:{model}:{symbol}"
        await self.set(key, prediction, ttl)
    
    async def get_ai_prediction(self, model: str, symbol: str) -> Optional[Any]:
        """Get cached AI prediction."""
        key = f"ai:{model}:{symbol}"
        return await self.get(key)
    
    async def cache_api_response(
        self,
        endpoint: str,
        params: Dict,
        response: Any,
        ttl: int = 300
    ):
        """Cache API response."""
        key = self._make_key(f"api:{endpoint}", **params)
        await self.set(key, response, ttl)
    
    async def get_api_response(self, endpoint: str, params: Dict) -> Optional[Any]:
        """Get cached API response."""
        key = self._make_key(f"api:{endpoint}", **params)
        return await self.get(key)
    
    async def rate_limit_check(self, key: str, max_requests: int, window: int) -> bool:
        """Check rate limit using cache."""
        try:
            current = await self.get(key) or 0
            
            if current >= max_requests:
                return False
            
            await self.set(key, current + 1, window)
            return True
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True  # Allow on error
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            "connected": self._connected,
            "local_cache_size": len(self._local_cache),
            "redis_url": self.redis_url if self._connected else None
        }


# Cache decorator
def cached(prefix: str, ttl: Optional[int] = None):
    """Decorator to cache function results."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Create cache key
            key_parts = [prefix, func.__name__]
            key_parts.extend(str(a) for a in args[1:])  # Skip self
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


import functools

# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get or create global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        cache = get_cache()
        await cache.connect()
        
        # Test market data caching
        await cache.cache_market_data("AAPL", {
            "price": 150.25,
            "change": 1.5,
            "volume": 15000000
        })
        
        data = await cache.get_market_data("AAPL")
        print(f"Cached market data: {data}")
        
        # Test AI prediction caching
        await cache.cache_ai_prediction("lstm", "AAPL", {
            "prediction": 155.0,
            "confidence": 0.75
        })
        
        pred = await cache.get_ai_prediction("lstm", "AAPL")
        print(f"Cached prediction: {pred}")
        
        # Stats
        print(f"Cache stats: {cache.get_stats()}")
        
        await cache.disconnect()
    
    asyncio.run(test())
