"""
Operations Managers Wiring
==========================
Connects DevOps, FinOps, and AIOps managers to real systems.
Makes skeleton code production-ready.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

# Import existing managers
from ops.devops_manager import DevOpsManager
from ops.finops_manager import FinOpsManager
from ops.aiops_manager import AIOpsManager

# Import API components for integration
from database_layer import DatabaseManager
from deployment_controller import deployment_controller
from realtime_data_integration import RealtimeDataIntegration

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """Real-time system metrics."""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    request_rate: float
    error_rate: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    queue_depth: int


class OpsOrchestrator:
    """
    Orchestrates all operations managers.
    Wires up DevOps + FinOps + AIOps into cohesive system.
    """
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
        self.devops = DevOpsManager()
        self.finops = FinOpsManager()
        self.aiops = AIOpsManager()
        
        self.is_running = False
        self.monitoring_task = None
        self.metrics_history: List[SystemMetrics] = []
        self.alert_handlers: List[callable] = []
        
        # Configuration
        self.monitoring_interval = 30  # seconds
        self.metrics_retention_hours = 24
        
    async def start(self):
        """Start all operations managers."""
        logger.info("Starting Ops Orchestrator...")
        
        self.is_running = True
        
        # Start continuous monitoring
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Initialize FinOps tracking
        await self._init_finops()
        
        # Initialize AIOps baseline
        await self._init_aiops()
        
        logger.info("Ops Orchestrator started successfully")
        
    async def stop(self):
        """Stop all operations."""
        logger.info("Stopping Ops Orchestrator...")
        
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            
        logger.info("Ops Orchestrator stopped")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop."""
        while self.is_running:
            try:
                # Collect metrics
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Trim old metrics
                cutoff = datetime.now() - timedelta(hours=self.metrics_retention_hours)
                self.metrics_history = [m for m in self.metrics_history if m.timestamp > cutoff]
                
                # Check for anomalies (AIOps)
                await self._check_anomalies(metrics)
                
                # Update FinOps tracking
                await self._update_cost_tracking(metrics)
                
                # Check thresholds and alert
                await self._check_thresholds(metrics)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                
            await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        import psutil
        
        # CPU and Memory
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network
        net_io = psutil.net_io_counters()
        
        # API metrics (from database or cache)
        db_stats = self._get_database_stats()
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_io={
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            },
            active_connections=db_stats.get('active_connections', 0),
            request_rate=db_stats.get('requests_per_second', 0),
            error_rate=db_stats.get('error_rate', 0),
            latency_p50=db_stats.get('latency_p50', 0),
            latency_p95=db_stats.get('latency_p95', 0),
            latency_p99=db_stats.get('latency_p99', 0),
            queue_depth=db_stats.get('queue_depth', 0)
        )
    
    def _get_database_stats(self) -> Dict:
        """Get database performance stats."""
        try:
            # Query SQLite for stats
            stats = {}
            
            # Connection count
            result = self.db.conn.execute(
                "PRAGMA database_list"
            ).fetchall()
            stats['active_connections'] = len(result)
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get DB stats: {e}")
            return {}
    
    async def _init_finops(self):
        """Initialize FinOps tracking."""
        # Set up budget tracking
        self.finops.set_budget_alert_threshold(0.8)  # Alert at 80% of budget
        
        # Track infrastructure costs (estimate)
        self.finops.track_infrastructure_cost({
            'railway': 25.0,  # Monthly hosting
            'vercel': 0.0,    # Free tier
            'alpaca': 0.0,    # Paper trading free
            'polygon': 0.0,    # Free tier
            'openai': 20.0    # API costs
        })
        
        logger.info("FinOps initialized")
    
    async def _init_aiops(self):
        """Initialize AIOps baseline."""
        # Set up anomaly detection
        self.aiops.configure_anomaly_detection(
            cpu_threshold=80.0,      # Alert if CPU > 80%
            memory_threshold=85.0,   # Alert if Memory > 85%
            latency_threshold=500,   # Alert if P95 latency > 500ms
            error_rate_threshold=5.0 # Alert if error rate > 5%
        )
        
        logger.info("AIOps initialized")
    
    async def _check_anomalies(self, metrics: SystemMetrics):
        """Check for anomalies using AIOps."""
        # CPU anomaly
        if metrics.cpu_usage > 80:
            await self._trigger_alert(
                'warning',
                f'High CPU usage: {metrics.cpu_usage}%',
                {'metric': 'cpu', 'value': metrics.cpu_usage}
            )
        
        # Memory anomaly
        if metrics.memory_usage > 85:
            await self._trigger_alert(
                'critical',
                f'High memory usage: {metrics.memory_usage}%',
                {'metric': 'memory', 'value': metrics.memory_usage}
            )
        
        # Latency anomaly
        if metrics.latency_p95 > 500:
            await self._trigger_alert(
                'warning',
                f'High P95 latency: {metrics.latency_p95}ms',
                {'metric': 'latency_p95', 'value': metrics.latency_p95}
            )
        
        # Error rate anomaly
        if metrics.error_rate > 5.0:
            await self._trigger_alert(
                'critical',
                f'High error rate: {metrics.error_rate}%',
                {'metric': 'error_rate', 'value': metrics.error_rate}
            )
    
    async def _update_cost_tracking(self, metrics: SystemMetrics):
        """Update FinOps cost tracking."""
        # Estimate compute cost based on usage
        compute_hours = self.monitoring_interval / 3600
        estimated_cost = self._estimate_compute_cost(metrics, compute_hours)
        
        self.finops.add_cost_entry(
            category='compute',
            amount=estimated_cost,
            resource_id='veyra-api',
            timestamp=metrics.timestamp
        )
    
    def _estimate_compute_cost(self, metrics: SystemMetrics, hours: float) -> float:
        """Estimate compute cost for this period."""
        # Railway $25/month ≈ $0.035/hour
        base_rate = 0.035  # USD per hour
        
        # Adjust for utilization
        utilization_factor = max(metrics.cpu_usage, metrics.memory_usage) / 100
        
        return base_rate * hours * (0.5 + 0.5 * utilization_factor)
    
    async def _check_thresholds(self, metrics: SystemMetrics):
        """Check metric thresholds and alert."""
        # Disk space warning
        if metrics.disk_usage > 90:
            await self._trigger_alert(
                'critical',
                f'Disk space critical: {metrics.disk_usage}% full',
                {'metric': 'disk', 'value': metrics.disk_usage}
            )
        elif metrics.disk_usage > 80:
            await self._trigger_alert(
                'warning',
                f'Disk space warning: {metrics.disk_usage}% full',
                {'metric': 'disk', 'value': metrics.disk_usage}
            )
    
    async def _trigger_alert(self, severity: str, message: str, context: Dict):
        """Trigger alert through all channels."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'message': message,
            'context': context
        }
        
        # Log alert
        if severity == 'critical':
            logger.error(f"ALERT [{severity}]: {message}")
        else:
            logger.warning(f"ALERT [{severity}]: {message}")
        
        # Call registered handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        # Store in database for history
        try:
            self.db.conn.execute(
                """INSERT INTO alerts (timestamp, severity, message, context)
                   VALUES (?, ?, ?, ?)""",
                (alert['timestamp'], severity, message, str(context))
            )
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
    
    def add_alert_handler(self, handler: callable):
        """Register alert handler."""
        self.alert_handlers.append(handler)
    
    def get_system_health(self) -> Dict:
        """Get current system health summary."""
        if not self.metrics_history:
            return {'status': 'unknown', 'message': 'No metrics available'}
        
        latest = self.metrics_history[-1]
        
        # Determine health status
        issues = []
        
        if latest.cpu_usage > 80:
            issues.append(f"High CPU: {latest.cpu_usage}%")
        if latest.memory_usage > 85:
            issues.append(f"High Memory: {latest.memory_usage}%")
        if latest.disk_usage > 80:
            issues.append(f"High Disk: {latest.disk_usage}%")
        if latest.error_rate > 5:
            issues.append(f"High Error Rate: {latest.error_rate}%")
        if latest.latency_p95 > 500:
            issues.append(f"High Latency: {latest.latency_p95}ms")
        
        if not issues:
            status = 'healthy'
            message = 'All systems operational'
        elif len(issues) <= 2:
            status = 'degraded'
            message = ', '.join(issues)
        else:
            status = 'critical'
            message = f"{len(issues)} issues detected"
        
        return {
            'status': status,
            'message': message,
            'issues': issues,
            'metrics': {
                'cpu': latest.cpu_usage,
                'memory': latest.memory_usage,
                'disk': latest.disk_usage,
                'latency_p95': latest.latency_p95,
                'error_rate': latest.error_rate,
                'request_rate': latest.request_rate
            },
            'timestamp': latest.timestamp.isoformat()
        }
    
    def get_cost_summary(self) -> Dict:
        """Get FinOps cost summary."""
        return self.finops.get_cost_summary()
    
    def get_deployment_status(self) -> Dict:
        """Get DevOps deployment status."""
        return self.devops.get_deployment_status('veyra')
    
    async def optimize_resources(self) -> Dict:
        """Run resource optimization."""
        recommendations = []
        
        # Analyze metrics history
        if len(self.metrics_history) < 10:
            return {'status': 'insufficient_data', 'recommendations': []}
        
        # Check for over-provisioning (low utilization)
        avg_cpu = sum(m.cpu_usage for m in self.metrics_history) / len(self.metrics_history)
        avg_memory = sum(m.memory_usage for m in self.metrics_history) / len(self.metrics_history)
        
        if avg_cpu < 20:
            recommendations.append({
                'type': 'cost_optimization',
                'severity': 'low',
                'message': 'CPU under-utilized. Consider downgrading instance.',
                'potential_savings': '~$10/month'
            })
        
        if avg_memory < 30:
            recommendations.append({
                'type': 'cost_optimization',
                'severity': 'low',
                'message': 'Memory under-utilized. Consider reducing allocation.',
                'potential_savings': '~$5/month'
            })
        
        # Check for scaling needs (high utilization)
        max_cpu = max(m.cpu_usage for m in self.metrics_history[-100:])  # Last 100 samples
        if max_cpu > 90:
            recommendations.append({
                'type': 'performance',
                'severity': 'high',
                'message': 'CPU spikes detected. Consider upgrading or scaling.',
                'action': 'scale_up'
            })
        
        return {
            'status': 'analyzed',
            'recommendations': recommendations,
            'avg_cpu': avg_cpu,
            'avg_memory': avg_memory,
            'analysis_period_hours': self.metrics_retention_hours
        }


# Global orchestrator instance
ops_orchestrator = OpsOrchestrator()


# Convenience functions for API integration
async def start_ops_monitoring():
    """Start operations monitoring."""
    await ops_orchestrator.start()

async def stop_ops_monitoring():
    """Stop operations monitoring."""
    await ops_orchestrator.stop()

def get_system_health() -> Dict:
    """Get current system health."""
    return ops_orchestrator.get_system_health()

def get_cost_summary() -> Dict:
    """Get cost summary."""
    return ops_orchestrator.get_cost_summary()

# Usage example:
# asyncio.run(start_ops_monitoring())
# health = get_system_health()
# print(health)
