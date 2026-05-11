"""
Enterprise Metrics Collector
=============================
Advanced metrics collection for Veyra systems
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import psutil
import aiohttp
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricPoint:
    name: str
    value: Union[int, float]
    metric_type: MetricType
    labels: Dict[str, str]
    timestamp: datetime
    unit: str = ""


@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io_bytes: Dict[str, int]
    process_count: int
    thread_count: int
    timestamp: datetime


class MetricsCollector:
    """Enterprise-grade metrics collector with Prometheus-compatible output"""
    
    def __init__(self):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.start_time = datetime.now()
        self.collection_interval = 15  # seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
    async def start_collection(self):
        """Start background metrics collection"""
        if self._running:
            return
            
        self._running = True
        self._task = asyncio.create_task(self._collect_loop())
        logger.info("Metrics collection started")
        
    async def stop_collection(self):
        """Stop background metrics collection"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics collection stopped")
        
    async def _collect_loop(self):
        """Background collection loop"""
        while self._running:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(5)
                
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.set_gauge("system_cpu_percent", cpu_percent, {"source": "psutil"})
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.set_gauge("system_memory_percent", memory.percent, {"source": "psutil"})
            self.set_gauge("system_memory_available_bytes", memory.available, {"source": "psutil"})
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.set_gauge("system_disk_usage_percent", 
                          (disk.used / disk.total) * 100, {"source": "psutil"})
            
            # Network metrics
            network = psutil.net_io_counters()
            self.set_counter("system_network_bytes_sent", network.bytes_sent, {"direction": "out"})
            self.set_counter("system_network_bytes_recv", network.bytes_recv, {"direction": "in"})
            
            # Process metrics
            process = psutil.Process()
            self.set_gauge("process_memory_percent", process.memory_percent(), {"source": "psutil"})
            self.set_gauge("process_cpu_percent", process.cpu_percent(), {"source": "psutil"})
            self.set_gauge("process_threads", process.num_threads(), {"source": "psutil"})
            
            # Application uptime
            uptime = (datetime.now() - self.start_time).total_seconds()
            self.set_gauge("application_uptime_seconds", uptime, {"source": "internal"})
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        key = self._make_key(name, labels)
        self.counters[key] += value
        
        metric = MetricPoint(
            name=name,
            value=self.counters[key],
            metric_type=MetricType.COUNTER,
            labels=labels or {},
            timestamp=datetime.now(),
            unit="count"
        )
        self.metrics[key].append(metric)
        
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        key = self._make_key(name, labels)
        self.gauges[key] = value
        
        metric = MetricPoint(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels or {},
            timestamp=datetime.now(),
            unit="value"
        )
        self.metrics[key].append(metric)
        
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram observation"""
        key = self._make_key(name, labels)
        self.histograms[key].append(value)
        
        # Keep only last 10000 observations per histogram
        if len(self.histograms[key]) > 10000:
            self.histograms[key] = self.histograms[key][-10000:]
            
        metric = MetricPoint(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            labels=labels or {},
            timestamp=datetime.now(),
            unit="observation"
        )
        self.metrics[key].append(metric)
        
    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create a unique key for a metric with labels"""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}[{label_str}]"
        
    def get_metrics(self, name_filter: Optional[str] = None, 
                   since: Optional[datetime] = None) -> List[MetricPoint]:
        """Get metrics with optional filtering"""
        results = []
        
        for key, metric_queue in self.metrics.items():
            if name_filter and name_filter not in key:
                continue
                
            for metric in metric_queue:
                if since and metric.timestamp < since:
                    continue
                results.append(metric)
                
        return sorted(results, key=lambda x: x.timestamp)
        
    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # Export counters
        for key, value in self.counters.items():
            name = key.split('[')[0]
            labels = self._parse_labels(key)
            label_str = self._format_labels(labels)
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name}{label_str} {value}")
            
        # Export gauges
        for key, value in self.gauges.items():
            name = key.split('[')[0]
            labels = self._parse_labels(key)
            label_str = self._format_labels(labels)
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name}{label_str} {value}")
            
        # Export histograms
        for key, values in self.histograms.items():
            if not values:
                continue
            name = key.split('[')[0]
            labels = self._parse_labels(key)
            label_str = self._format_labels(labels)
            
            lines.append(f"# TYPE {name} histogram")
            
            # Calculate histogram buckets
            sorted_values = sorted(values)
            buckets = [0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0, float('inf')]
            
            for bucket in buckets:
                count = sum(1 for v in sorted_values if v <= bucket)
                bucket_labels = {**labels, "le": str(bucket)}
                bucket_label_str = self._format_labels(bucket_labels)
                lines.append(f"{name}_bucket{bucket_label_str} {count}")
                
            lines.append(f"{name}_count{label_str} {len(values)}")
            lines.append(f"{name}_sum{label_str} {sum(values)}")
            
        return "\n".join(lines)
        
    def _parse_labels(self, key: str) -> Dict[str, str]:
        """Parse labels from a metric key"""
        if '[' not in key or ']' not in key:
            return {}
            
        label_str = key.split('[')[1].split(']')[0]
        labels = {}
        for pair in label_str.split(','):
            if '=' in pair:
                k, v = pair.split('=', 1)
                labels[k] = v
        return labels
        
    def _format_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus output"""
        if not labels:
            return ""
        label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
        return "{" + ",".join(label_pairs) + "}"
        
    async def push_to_gateway(self, gateway_url: str, job: str = "veyra"):
        """Push metrics to Prometheus Pushgateway"""
        try:
            metrics_data = self.get_prometheus_metrics()
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{gateway_url}/metrics/job/{job}",
                    data=metrics_data,
                    headers={"Content-Type": "text/plain"}
                ) as response:
                    if response.status == 200:
                        logger.info("Metrics pushed to gateway successfully")
                    else:
                        logger.error(f"Failed to push metrics: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error pushing metrics to gateway: {e}")
            
    def get_summary_stats(self, metric_name: str, 
                          labels: Optional[Dict[str, str]] = None,
                          duration_minutes: int = 60) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        since = datetime.now() - timedelta(minutes=duration_minutes)
        key = self._make_key(metric_name, labels)
        
        if key not in self.metrics:
            return {}
            
        recent_metrics = [m for m in self.metrics[key] if m.timestamp >= since]
        if not recent_metrics:
            return {}
            
        values = [m.value for m in recent_metrics]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
            "duration_minutes": duration_minutes
        }
