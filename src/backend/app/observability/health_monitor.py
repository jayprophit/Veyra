"""
Enterprise Health Monitor
=========================
Comprehensive health monitoring and dependency tracking
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import aiohttp
import psutil
import redis
import asyncpg
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class CheckType(Enum):
    LIVENESS = "liveness"
    READINESS = "readiness"
    STARTUP = "startup"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    check_type: CheckType
    duration_ms: float
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


@dataclass
class Dependency:
    name: str
    type: str  # database, cache, external_api, message_queue, etc.
    endpoint: str
    status: HealthStatus
    last_check: datetime
    response_time_ms: float
    error_message: Optional[str] = None


class HealthMonitor:
    """Enterprise health monitoring with dependency tracking"""
    
    def __init__(self, service_name: str = "financial-master"):
        self.service_name = service_name
        self.health_checks: Dict[str, HealthCheck] = {}
        self.dependencies: Dict[str, Dependency] = {}
        self.check_interval = 30  # seconds
        self.timeout = 10  # seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.custom_checks: Dict[str, Callable] = {}
        
    def add_dependency(self, name: str, dependency_type: str, endpoint: str):
        """Add a dependency to monitor"""
        self.dependencies[name] = Dependency(
            name=name,
            type=dependency_type,
            endpoint=endpoint,
            status=HealthStatus.UNKNOWN,
            last_check=datetime.now(),
            response_time_ms=0.0
        )
        
    def add_custom_check(self, name: str, check_func: Callable[[], bool]):
        """Add a custom health check function"""
        self.custom_checks[name] = check_func
        
    async def start(self):
        """Start health monitoring"""
        if self._running:
            return
            
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("Health monitoring started")
        
    async def stop(self):
        """Stop health monitoring"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitoring stopped")
        
    async def _monitor_loop(self):
        """Background monitoring loop"""
        while self._running:
            try:
                await self._run_health_checks()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(5)
                
    async def _run_health_checks(self):
        """Run all health checks"""
        # Check dependencies
        for dep in self.dependencies.values():
            await self._check_dependency(dep)
            
        # Run custom checks
        for name, check_func in self.custom_checks.items():
            await self._run_custom_check(name, check_func)
            
        # Run built-in checks
        await self._check_system_resources()
        await self._check_application_health()
        
    async def _check_dependency(self, dependency: Dependency):
        """Check a single dependency"""
        start_time = time.time()
        
        try:
            if dependency.type == "database":
                await self._check_database(dependency)
            elif dependency.type == "cache":
                await self._check_cache(dependency)
            elif dependency.type == "external_api":
                await self._check_external_api(dependency)
            elif dependency.type == "message_queue":
                await self._check_message_queue(dependency)
            else:
                await self._check_generic_endpoint(dependency)
                
            dependency.status = HealthStatus.HEALTHY
            dependency.error_message = None
            
        except Exception as e:
            dependency.status = HealthStatus.UNHEALTHY
            dependency.error_message = str(e)
            logger.error(f"Health check failed for {dependency.name}: {e}")
            
        finally:
            dependency.response_time_ms = (time.time() - start_time) * 1000
            dependency.last_check = datetime.now()
            
    async def _check_database(self, dependency: Dependency):
        """Check database connectivity"""
        # This would be implemented based on your database connection
        # Example for PostgreSQL
        try:
            conn = await asyncpg.connect(dependency.endpoint)
            await conn.execute("SELECT 1")
            await conn.close()
        except Exception as e:
            raise Exception(f"Database connection failed: {e}")
            
    async def _check_cache(self, dependency: Dependency):
        """Check cache connectivity"""
        # Example for Redis
        try:
            r = redis.from_url(dependency.endpoint)
            r.ping()
        except Exception as e:
            raise Exception(f"Cache connection failed: {e}")
            
    async def _check_external_api(self, dependency: Dependency):
        """Check external API availability"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(dependency.endpoint, timeout=self.timeout) as response:
                    if response.status >= 500:
                        raise Exception(f"API returned status {response.status}")
        except Exception as e:
            raise Exception(f"API check failed: {e}")
            
    async def _check_message_queue(self, dependency: Dependency):
        """Check message queue connectivity"""
        # This would be implemented based on your message queue system
        # Example for RabbitMQ
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{dependency.endpoint}/api/overview", timeout=self.timeout) as response:
                    if response.status != 200:
                        raise Exception(f"Message queue check failed: {response.status}")
        except Exception as e:
            raise Exception(f"Message queue check failed: {e}")
            
    async def _check_generic_endpoint(self, dependency: Dependency):
        """Check generic HTTP endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(dependency.endpoint, timeout=self.timeout) as response:
                    if response.status >= 400:
                        raise Exception(f"Endpoint returned status {response.status}")
        except Exception as e:
            raise Exception(f"Endpoint check failed: {e}")
            
    async def _run_custom_check(self, name: str, check_func: Callable):
        """Run a custom health check"""
        start_time = time.time()
        
        try:
            result = check_func()
            if asyncio.iscoroutine(result):
                result = await result
                
            status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
            message = "Custom check passed" if result else "Custom check failed"
            
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            message = str(e)
            
        duration_ms = (time.time() - start_time) * 1000
        
        self.health_checks[name] = HealthCheck(
            name=name,
            status=status,
            check_type=CheckType.LIVENESS,
            duration_ms=duration_ms,
            message=message,
            timestamp=datetime.now()
        )
        
    async def _check_system_resources(self):
        """Check system resource health"""
        start_time = time.time()
        
        try:
            # Check CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_healthy = cpu_percent < 80
            
            # Check memory
            memory = psutil.virtual_memory()
            memory_healthy = memory.percent < 85
            
            # Check disk
            disk = psutil.disk_usage('/')
            disk_healthy = (disk.used / disk.total) < 90
            
            overall_healthy = cpu_healthy and memory_healthy and disk_healthy
            status = HealthStatus.HEALTHY if overall_healthy else HealthStatus.DEGRADED
            
            message = f"CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%, Disk: {(disk.used/disk.total)*100:.1f}%"
            
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            message = str(e)
            
        duration_ms = (time.time() - start_time) * 1000
        
        self.health_checks["system_resources"] = HealthCheck(
            name="system_resources",
            status=status,
            check_type=CheckType.LIVENESS,
            duration_ms=duration_ms,
            message=message,
            timestamp=datetime.now(),
            details={
                "cpu_percent": cpu_percent if 'cpu_percent' in locals() else None,
                "memory_percent": memory.percent if 'memory' in locals() else None,
                "disk_percent": (disk.used/disk.total)*100 if 'disk' in locals() else None
            }
        )
        
    async def _check_application_health(self):
        """Check application-specific health"""
        start_time = time.time()
        
        try:
            # Check if we can access basic application resources
            checks = []
            
            # Check configuration
            try:
                # This would check your application configuration
                config_healthy = True  # Placeholder
                checks.append(("configuration", config_healthy))
            except Exception:
                checks.append(("configuration", False))
                
            # Check database connection pool
            try:
                # This would check your database connection pool
                pool_healthy = True  # Placeholder
                checks.append(("database_pool", pool_healthy))
            except Exception:
                checks.append(("database_pool", False))
                
            # Check cache connection
            try:
                # This would check your cache connection
                cache_healthy = True  # Placeholder
                checks.append(("cache", cache_healthy))
            except Exception:
                checks.append(("cache", False))
                
            # Determine overall health
            failed_checks = [name for name, healthy in checks if not healthy]
            if not failed_checks:
                status = HealthStatus.HEALTHY
                message = "All application checks passed"
            elif len(failed_checks) <= len(checks) / 2:
                status = HealthStatus.DEGRADED
                message = f"Some checks failed: {', '.join(failed_checks)}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Critical checks failed: {', '.join(failed_checks)}"
                
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            message = str(e)
            
        duration_ms = (time.time() - start_time) * 1000
        
        self.health_checks["application"] = HealthCheck(
            name="application",
            status=status,
            check_type=CheckType.READINESS,
            duration_ms=duration_ms,
            message=message,
            timestamp=datetime.now()
        )
        
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall health status"""
        if not self.health_checks and not self.dependencies:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health checks available",
                "timestamp": datetime.now().isoformat(),
                "checks": [],
                "dependencies": []
            }
            
        # Collect all statuses
        all_statuses = []
        
        # Health check statuses
        for check in self.health_checks.values():
            all_statuses.append(check.status)
            
        # Dependency statuses
        for dep in self.dependencies.values():
            all_statuses.append(dep.status)
            
        # Determine overall status
        if not all_statuses:
            overall_status = HealthStatus.UNKNOWN
        elif all(status == HealthStatus.HEALTHY for status in all_statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in all_statuses):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED
            
        return {
            "status": overall_status.value,
            "message": self._get_status_message(overall_status),
            "timestamp": datetime.now().isoformat(),
            "checks": [asdict(check) for check in self.health_checks.values()],
            "dependencies": [asdict(dep) for dep in self.dependencies.values()]
        }
        
    def _get_status_message(self, status: HealthStatus) -> str:
        """Get status message based on overall health"""
        messages = {
            HealthStatus.HEALTHY: "All systems operational",
            HealthStatus.DEGRADED: "Some systems experiencing issues",
            HealthStatus.UNHEALTHY: "Critical systems failing",
            HealthStatus.UNKNOWN: "Health status unknown"
        }
        return messages.get(status, "Unknown status")
        
    async def run_liveness_check(self) -> Dict[str, Any]:
        """Run liveness probe check"""
        # Quick check to see if the application is alive
        return {
            "status": HealthStatus.HEALTHY.value,
            "timestamp": datetime.now().isoformat(),
            "message": "Application is alive"
        }
        
    async def run_readiness_check(self) -> Dict[str, Any]:
        """Run readiness probe check"""
        # Check if the application is ready to serve traffic
        if not self.health_checks:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "timestamp": datetime.now().isoformat(),
                "message": "Health checks not ready"
            }
            
        # Check critical dependencies
        critical_deps = [dep for dep in self.dependencies.values() 
                         if dep.type in ["database", "cache"]]
        
        if critical_deps and any(dep.status == HealthStatus.UNHEALTHY for dep in critical_deps):
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "timestamp": datetime.now().isoformat(),
                "message": "Critical dependencies not ready"
            }
            
        return {
            "status": HealthStatus.HEALTHY.value,
            "timestamp": datetime.now().isoformat(),
            "message": "Application is ready"
        }
        
    async def run_startup_check(self) -> Dict[str, Any]:
        """Run startup probe check"""
        # Check if the application has started successfully
        startup_checks = [check for check in self.health_checks.values() 
                         if check.check_type == CheckType.STARTUP]
        
        if not startup_checks:
            return {
                "status": HealthStatus.HEALTHY.value,
                "timestamp": datetime.now().isoformat(),
                "message": "No startup checks configured"
            }
            
        failed_startup = [check for check in startup_checks if check.status == HealthStatus.UNHEALTHY]
        
        if failed_startup:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "timestamp": datetime.now().isoformat(),
                "message": f"Startup checks failed: {', '.join(check.name for check in failed_startup)}"
            }
            
        return {
            "status": HealthStatus.HEALTHY.value,
            "timestamp": datetime.now().isoformat(),
            "message": "Application started successfully"
        }


# Global health monitor instance
_health_monitor = None

def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


# FastAPI health endpoints
async def health_check():
    """Comprehensive health check endpoint"""
    monitor = get_health_monitor()
    return monitor.get_overall_health()

async def liveness_probe():
    """Liveness probe endpoint"""
    monitor = get_health_monitor()
    return await monitor.run_liveness_check()

async def readiness_probe():
    """Readiness probe endpoint"""
    monitor = get_health_monitor()
    return await monitor.run_readiness_check()

async def startup_probe():
    """Startup probe endpoint"""
    monitor = get_health_monitor()
    return await monitor.run_startup_probe()
