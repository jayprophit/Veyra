"""Real-Time Performance Monitoring Dashboard."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    name: str
    value: float
    timestamp: datetime
    unit: str
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None

class PerformanceDashboard:
    """
    Real-time system performance monitoring with alerting.
    Tracks latency, throughput, errors, and system health.
    """
    
    def __init__(self):
        self.metrics_history: Dict[str, deque] = {}
        self.current_metrics: Dict[str, PerformanceMetric] = {}
        self.alert_history: List[Dict] = []
        self.system_health = {
            'status': 'healthy',
            'score': 100,
            'last_check': datetime.now()
        }
        self.max_history = 10000
        
        # Metric thresholds
        self.thresholds = {
            'api_latency_ms': {'warning': 100, 'critical': 500},
            'db_query_time_ms': {'warning': 50, 'critical': 200},
            'error_rate_pct': {'warning': 1, 'critical': 5},
            'cpu_usage_pct': {'warning': 70, 'critical': 90},
            'memory_usage_pct': {'warning': 80, 'critical': 95},
            'disk_usage_pct': {'warning': 85, 'critical': 95}
        }
    
    async def record_metric(self, name: str, value: float, unit: str = ""):
        """Record a performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            unit=unit
        )
        
        self.current_metrics[name] = metric
        
        if name not in self.metrics_history:
            self.metrics_history[name] = deque(maxlen=self.max_history)
        
        self.metrics_history[name].append(metric)
        
        # Check thresholds
        await self._check_thresholds(name, value)
    
    async def _check_thresholds(self, name: str, value: float):
        """Check if metric exceeds thresholds."""
        if name not in self.thresholds:
            return
        
        thresholds = self.thresholds[name]
        
        if value >= thresholds.get('critical', float('inf')):
            await self._create_alert(name, value, 'critical')
        elif value >= thresholds.get('warning', float('inf')):
            await self._create_alert(name, value, 'warning')
    
    async def _create_alert(self, metric_name: str, value: float, severity: str):
        """Create performance alert."""
        alert = {
            'alert_id': f"perf_{datetime.now().strftime('%H%M%S%f')}",
            'metric': metric_name,
            'value': value,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.alert_history.append(alert)
        logger.warning(f"Performance alert: {metric_name} = {value} ({severity})")
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics."""
        metrics = {}
        
        for name, metric in self.current_metrics.items():
            age_seconds = (datetime.now() - metric.timestamp).total_seconds()
            
            metrics[name] = {
                'value': round(metric.value, 4),
                'unit': metric.unit,
                'timestamp': metric.timestamp.isoformat(),
                'staleness_seconds': age_seconds,
                'fresh': age_seconds < 60
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics_count': len(metrics),
            'system_health': self.system_health,
            'metrics': metrics
        }
    
    async def get_metric_statistics(self,
                                   metric_name: str,
                                   time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get statistical analysis of metric over time window."""
        if metric_name not in self.metrics_history:
            return {'error': 'Metric not found'}
        
        cutoff = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_values = [
            m.value for m in self.metrics_history[metric_name]
            if m.timestamp >= cutoff
        ]
        
        if not recent_values:
            return {'error': 'No data in time window'}
        
        return {
            'metric': metric_name,
            'time_window_minutes': time_window_minutes,
            'data_points': len(recent_values),
            'current': recent_values[-1],
            'min': min(recent_values),
            'max': max(recent_values),
            'mean': statistics.mean(recent_values),
            'median': statistics.median(recent_values),
            'stdev': statistics.stdev(recent_values) if len(recent_values) > 1 else 0,
            'p95': sorted(recent_values)[int(len(recent_values) * 0.95)],
            'p99': sorted(recent_values)[int(len(recent_values) * 0.99)]
        }
    
    async def calculate_apdex(self,
                             metric_name: str,
                             satisfied_threshold: float,
                             tolerating_threshold: float) -> Dict[str, Any]:
        """Calculate Apdex score for user satisfaction."""
        if metric_name not in self.metrics_history:
            return {'error': 'Metric not found'}
        
        values = [m.value for m in self.metrics_history[metric_name]]
        
        satisfied = sum(1 for v in values if v <= satisfied_threshold)
        tolerating = sum(1 for v in values if satisfied_threshold < v <= tolerating_threshold)
        total = len(values)
        
        if total == 0:
            return {'apdex': 0, 'samples': 0}
        
        apdex = (satisfied + tolerating / 2) / total
        
        return {
            'apdex': round(apdex, 3),
            'satisfied': satisfied,
            'tolerating': tolerating,
            'frustrated': total - satisfied - tolerating,
            'total_samples': total,
            'rating': 'excellent' if apdex >= 0.94 else 'good' if apdex >= 0.85 else 'fair' if apdex >= 0.7 else 'poor'
        }
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary."""
        # Get active alerts
        active_alerts = [
            a for a in self.alert_history
            if a['status'] == 'active'
            and datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(hours=24)
        ]
        
        # Calculate system health score
        health_score = 100
        for alert in active_alerts:
            if alert['severity'] == 'critical':
                health_score -= 20
            elif alert['severity'] == 'warning':
                health_score -= 5
        
        health_score = max(0, health_score)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'status': 'healthy' if health_score > 80 else 'degraded' if health_score > 50 else 'critical',
            'active_alerts': len(active_alerts),
            'critical_alerts': sum(1 for a in active_alerts if a['severity'] == 'critical'),
            'warning_alerts': sum(1 for a in active_alerts if a['severity'] == 'warning'),
            'metrics_tracked': len(self.current_metrics),
            'top_metrics': list(self.current_metrics.keys())[:10]
        }

performance_dashboard = PerformanceDashboard()
