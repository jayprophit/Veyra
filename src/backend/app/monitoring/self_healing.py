"""Self-Healing System for Veyra."""
import asyncio
import logging
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import time

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    response_time_ms: float
    last_check: datetime
    error_message: str = ""

class SelfHealingSystem:
    """Autonomous error detection and recovery."""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.health_status: Dict[str, HealthCheck] = {}
        self.recovery_actions: Dict[str, List[Callable]] = {}
        self.running = False
    
    def register_check(self, name: str, check_fn: Callable, recovery_fns: List[Callable] = None):
        self.checks[name] = check_fn
        self.recovery_actions[name] = recovery_fns or []
    
    async def start_monitoring(self, interval: int = 30):
        self.running = True
        while self.running:
            await self._run_health_checks()
            await asyncio.sleep(interval)
    
    async def _run_health_checks(self):
        for name, check_fn in self.checks.items():
            start = time.time()
            try:
                result = await check_fn() if asyncio.iscoroutinefunction(check_fn) else check_fn()
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                error = "" if result else "Check failed"
            except Exception as e:
                status = HealthStatus.CRITICAL
                error = str(e)
            
            elapsed = (time.time() - start) * 1000
            
            self.health_status[name] = HealthCheck(
                name=name,
                status=status,
                response_time_ms=elapsed,
                last_check=datetime.now(),
                error_message=error
            )
            
            if status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                await self._execute_recovery(name)
    
    async def _execute_recovery(self, component: str):
        logger.warning(f"Executing recovery for {component}")
        for action in self.recovery_actions.get(component, []):
            try:
                if asyncio.iscoroutinefunction(action):
                    await action()
                else:
                    action()
            except Exception as e:
                logger.error(f"Recovery action failed: {e}")
    
    def get_health_report(self) -> Dict[str, Any]:
        return {
            'checks': {name: {
                'status': check.status.value,
                'response_time_ms': check.response_time_ms,
                'last_check': check.last_check.isoformat(),
                'error': check.error_message
            } for name, check in self.health_status.items()},
            'overall_status': self._get_overall_status().value,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_overall_status(self) -> HealthStatus:
        if not self.health_status:
            return HealthStatus.HEALTHY
        
        statuses = [check.status for check in self.health_status.values()]
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

self_healing = SelfHealingSystem()
