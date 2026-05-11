"""
Observability Manager
=====================
Unified observability management for Veyra
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .metrics_collector import MetricsCollector
from .distributed_tracing import DistributedTracing, get_tracer
from .log_aggregator import LogAggregator, get_log_aggregator
from .health_monitor import HealthMonitor, get_health_monitor
from .performance_monitor import PerformanceMonitor, get_performance_monitor
from .alerting_system import AlertingSystem, get_alerting_system, AlertSeverity

logger = logging.getLogger(__name__)


class ObservabilityManager:
    """Unified observability management"""
    
    def __init__(self, service_name: str = "veyra"):
        self.service_name = service_name
        self.metrics_collector = MetricsCollector()
        self.tracer = get_tracer()
        self.log_aggregator = get_log_aggregator()
        self.health_monitor = get_health_monitor()
        self.performance_monitor = get_performance_monitor()
        self.alerting_system = get_alerting_system()
        self._started = False
        
    async def start(self):
        """Start all observability components"""
        if self._started:
            return
            
        logger.info("Starting observability manager...")
        
        # Start all components
        await self.metrics_collector.start_collection()
        await self.log_aggregator.start()
        await self.health_monitor.start()
        await self.performance_monitor.start()
        await self.alerting_system.start()
        
        self._started = True
        logger.info("Observability manager started successfully")
        
    async def stop(self):
        """Stop all observability components"""
        if not self._started:
            return
            
        logger.info("Stopping observability manager...")
        
        # Stop all components
        await self.metrics_collector.stop_collection()
        await self.log_aggregator.stop()
        await self.health_monitor.stop()
        await self.performance_monitor.stop()
        await self.alerting_system.stop()
        
        self._started = False
        logger.info("Observability manager stopped")
        
    def get_status(self) -> Dict[str, Any]:
        """Get status of all observability components"""
        return {
            "service": self.service_name,
            "started": self._started,
            "components": {
                "metrics_collector": "running" if self.metrics_collector._running else "stopped",
                "distributed_tracing": "available",
                "log_aggregator": "running" if self.log_aggregator._running else "stopped",
                "health_monitor": "running" if self.health_monitor._running else "stopped",
                "performance_monitor": "running" if self.performance_monitor._running else "stopped",
                "alerting_system": "running" if self.alerting_system._running else "stopped"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health and observability status"""
        health = self.health_monitor.get_overall_health()
        metrics_summary = self.performance_monitor.get_performance_summary()
        
        return {
            "health": health,
            "observability": {
                "status": self.get_status(),
                "metrics_summary": metrics_summary,
                "active_alerts": len(self.alerting_system.get_active_alerts()),
                "system_metrics": {
                    "cpu_usage": self.metrics_collector.gauges.get("system_cpu_percent", 0),
                    "memory_usage": self.metrics_collector.gauges.get("system_memory_percent", 0),
                    "uptime": self.metrics_collector.gauges.get("application_uptime_seconds", 0)
                }
            }
        }


# Global observability manager instance
_observability_manager = None

def get_observability_manager() -> ObservabilityManager:
    """Get the global observability manager instance"""
    global _observability_manager
    if _observability_manager is None:
        _observability_manager = ObservabilityManager()
    return _observability_manager
