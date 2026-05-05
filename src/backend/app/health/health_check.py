"""
Enterprise Health Check System
==============================
Comprehensive health checks with dependency monitoring, graceful shutdown,
and circuit breaker patterns. Based on Kubernetes health check best practices.
"""

import asyncio
import time
import psutil
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import aiohttp
import asyncpg
import aioredis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

logger = structlog.get_logger(__name__)


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


@dataclass
class SystemHealth:
    """Overall system health status."""
    status: HealthStatus
    checks: List[HealthCheckResult]
    uptime_seconds: float
    version: str
    timestamp: datetime


class HealthChecker:
    """Base class for health checks."""
    
    def __init__(self, name: str, timeout: float = 5.0):
        self.name = name
        self.timeout = timeout
    
    async def check(self) -> HealthCheckResult:
        """Perform health check."""
        start_time = time.time()
        try:
            result = await asyncio.wait_for(self._check_internal(), timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000
            
            if isinstance(result, str):
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message=result,
                    response_time_ms=response_time,
                    timestamp=datetime.utcnow()
                )
            elif isinstance(result, tuple):
                status, message = result
                return HealthCheckResult(
                    name=self.name,
                    status=status,
                    message=message,
                    response_time_ms=response_time,
                    timestamp=datetime.utcnow()
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="OK",
                    response_time_ms=response_time,
                    timestamp=datetime.utcnow()
                )
        except asyncio.TimeoutError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Health check timeout",
                response_time_ms=self.timeout * 1000,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow()
            )
    
    async def _check_internal(self) -> Any:
        """Override this method in subclasses."""
        raise NotImplementedError


class DatabaseHealthCheck(HealthChecker):
    """Database health check."""
    
    def __init__(self, db_session_factory, timeout: float = 5.0):
        super().__init__("database", timeout)
        self.db_session_factory = db_session_factory
    
    async def _check_internal(self) -> str:
        """Check database connectivity."""
        async with self.db_session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            await session.commit()
            return "Database connection successful"


class RedisHealthCheck(HealthChecker):
    """Redis health check."""
    
    def __init__(self, redis_client: aioredis.Redis, timeout: float = 5.0):
        super().__init__("redis", timeout)
        self.redis_client = redis_client
    
    async def _check_internal(self) -> str:
        """Check Redis connectivity."""
        await self.redis_client.ping()
        return "Redis connection successful"


class ExternalAPIHealthCheck(HealthChecker):
    """External API health check."""
    
    def __init__(self, name: str, url: str, timeout: float = 5.0):
        super().__init__(name, timeout)
        self.url = url
    
    async def _check_internal(self) -> str:
        """Check external API connectivity."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                if response.status == 200:
                    return f"API {self.url} is healthy"
                else:
                    raise Exception(f"API returned status {response.status}")


class SystemResourceHealthCheck(HealthChecker):
    """System resource health check."""
    
    def __init__(self, cpu_threshold: float = 80.0, memory_threshold: float = 85.0, timeout: float = 2.0):
        super().__init__("system_resources", timeout)
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
    
    async def _check_internal(self) -> tuple[HealthStatus, str]:
        """Check system resources."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        details = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
        
        if cpu_percent > self.cpu_threshold or memory_percent > self.memory_threshold:
            return HealthStatus.DEGRADED, f"High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%"
        
        return HealthStatus.HEALTHY, f"Resource usage normal: CPU {cpu_percent}%, Memory {memory_percent}%", details


class CircuitBreaker:
    """Circuit breaker for health checks."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("Circuit breaker returning to CLOSED state")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.warning("Circuit breaker opened", failure_count=self.failure_count)
            
            raise e


class HealthCheckManager:
    """Manages all health checks and provides overall system health."""
    
    def __init__(self, start_time: datetime, version: str = "1.0.0"):
        self.start_time = start_time
        self.version = version
        self.checkers: List[HealthChecker] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def add_checker(self, checker: HealthChecker):
        """Add a health checker."""
        self.checkers.append(checker)
        self.circuit_breakers[checker.name] = CircuitBreaker()
    
    async def check_all(self) -> SystemHealth:
        """Run all health checks and return overall system health."""
        results = []
        overall_status = HealthStatus.HEALTHY
        
        for checker in self.checkers:
            circuit_breaker = self.circuit_breakers[checker.name]
            try:
                result = await circuit_breaker.call(checker.check)
                results.append(result)
                
                # Update overall status
                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                    
            except Exception as e:
                logger.error("Health check failed", checker=checker.name, error=str(e))
                results.append(HealthCheckResult(
                    name=checker.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Circuit breaker open: {str(e)}",
                    response_time_ms=0,
                    timestamp=datetime.utcnow()
                ))
                overall_status = HealthStatus.UNHEALTHY
        
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return SystemHealth(
            status=overall_status,
            checks=results,
            uptime_seconds=uptime,
            version=self.version,
            timestamp=datetime.utcnow()
        )
    
    async def check_liveness(self) -> Dict[str, Any]:
        """Simple liveness check for Kubernetes."""
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
        }
    
    async def check_readiness(self) -> Dict[str, Any]:
        """Readiness check for Kubernetes."""
        # Check critical dependencies
        critical_checks = ["database", "redis"]
        for checker in self.checkers:
            if checker.name in critical_checks:
                try:
                    result = await checker.check()
                    if result.status != HealthStatus.HEALTHY:
                        return {
                            "status": "not_ready",
                            "reason": f"Critical dependency {checker.name} is {result.status.value}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                except Exception as e:
                    return {
                        "status": "not_ready",
                        "reason": f"Critical dependency {checker.name} check failed: {str(e)}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }


class GracefulShutdown:
    """Handles graceful shutdown of the application."""
    
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.shutdown_handlers: List[Callable] = []
    
    def add_handler(self, handler: Callable):
        """Add a shutdown handler."""
        self.shutdown_handlers.append(handler)
    
    async def shutdown(self, signal: str = None):
        """Initiate graceful shutdown."""
        logger.info("Initiating graceful shutdown", signal=signal)
        self.shutdown_event.set()
        
        # Run shutdown handlers
        for handler in self.shutdown_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                logger.error("Error in shutdown handler", error=str(e))
        
        logger.info("Graceful shutdown completed")
    
    def is_shutting_down(self) -> bool:
        """Check if shutdown is in progress."""
        return self.shutdown_event.is_set()


# Global health check manager instance
health_manager = HealthCheckManager(
    start_time=datetime.utcnow(),
    version="1.0.0"
)

# Global graceful shutdown instance
graceful_shutdown = GracefulShutdown()
