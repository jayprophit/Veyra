"""
Enterprise Performance Monitor
==============================
Advanced performance monitoring and profiling
"""

import asyncio
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import logging
import statistics
import functools

logger = logging.getLogger(__name__)


class PerformanceMetricType(Enum):
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DATABASE_QUERIES = "database_queries"
    CACHE_HIT_RATE = "cache_hit_rate"
    API_CALLS = "api_calls"


@dataclass
class PerformanceMetric:
    name: str
    metric_type: PerformanceMetricType
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str]
    threshold: Optional[float] = None


@dataclass
class PerformanceProfile:
    endpoint: str
    method: str
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    timestamp: datetime
    sample_count: int


class PerformanceMonitor:
    """Enterprise performance monitoring with real-time analytics"""
    
    def __init__(self, service_name: str = "financial-master"):
        self.service_name = service_name
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.profiles: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.active_requests: Dict[str, float] = {}
        self.request_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.total_requests: Dict[str, int] = defaultdict(int)
        self.collection_interval = 60  # seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
    async def start(self):
        """Start performance monitoring"""
        if self._running:
            return
            
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("Performance monitoring started")
        
    async def stop(self):
        """Stop performance monitoring"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
        
    async def _monitor_loop(self):
        """Background monitoring loop"""
        while self._running:
            try:
                await self._collect_system_metrics()
                await self._calculate_profiles()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(5)
                
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self._add_metric("system_cpu", PerformanceMetricType.CPU_USAGE, 
                           cpu_percent, "percent", {"source": "psutil"})
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self._add_metric("system_memory", PerformanceMetricType.MEMORY_USAGE,
                           memory.percent, "percent", {"source": "psutil"})
            
            # Process-specific metrics
            process = psutil.Process()
            self._add_metric("process_cpu", PerformanceMetricType.CPU_USAGE,
                           process.cpu_percent(), "percent", {"source": "psutil", "process": "financial-master"})
            self._add_metric("process_memory", PerformanceMetricType.MEMORY_USAGE,
                           process.memory_percent(), "percent", {"source": "psutil", "process": "financial-master"})
            
            # Active requests
            self._add_metric("active_requests", PerformanceMetricType.THROUGHPUT,
                           len(self.active_requests), "count", {"source": "internal"})
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            
    async def _calculate_profiles(self):
        """Calculate performance profiles for endpoints"""
        for endpoint, times in self.request_times.items():
            if not times:
                continue
                
            try:
                times_list = list(times)
                avg_time = statistics.mean(times_list)
                p95_time = self._percentile(times_list, 95)
                p99_time = self._percentile(times_list, 99)
                
                # Calculate requests per second
                recent_time = datetime.now() - timedelta(minutes=1)
                recent_requests = sum(1 for t in times_list if t >= recent_time.timestamp())
                rps = recent_requests / 60.0
                
                # Calculate error rate
                total_req = self.total_requests[endpoint]
                error_count = self.error_counts[endpoint]
                error_rate = (error_count / total_req * 100) if total_req > 0 else 0
                
                profile = PerformanceProfile(
                    endpoint=endpoint,
                    method="GET",  # This would be tracked per method
                    avg_response_time=avg_time,
                    p95_response_time=p95_time,
                    p99_response_time=p99_time,
                    requests_per_second=rps,
                    error_rate=error_rate,
                    timestamp=datetime.now(),
                    sample_count=len(times_list)
                )
                
                self.profiles[endpoint].append(profile)
                
            except Exception as e:
                logger.error(f"Error calculating profile for {endpoint}: {e}")
                
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
        
    def _add_metric(self, name: str, metric_type: PerformanceMetricType, 
                    value: float, unit: str, tags: Dict[str, str]):
        """Add a performance metric"""
        metric = PerformanceMetric(
            name=name,
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            tags=tags
        )
        self.metrics[name].append(metric)
        
    def record_request_start(self, request_id: str, endpoint: str):
        """Record the start of a request"""
        with self._lock:
            self.active_requests[request_id] = time.time()
            
    def record_request_end(self, request_id: str, endpoint: str, 
                          status_code: int = 200):
        """Record the end of a request"""
        with self._lock:
            if request_id in self.active_requests:
                start_time = self.active_requests[request_id]
                duration = time.time() - start_time
                
                # Record response time
                self.request_times[endpoint].append(duration)
                self.total_requests[endpoint] += 1
                
                # Record error if applicable
                if status_code >= 400:
                    self.error_counts[endpoint] += 1
                    
                # Add response time metric
                self._add_metric(f"{endpoint}_response_time", 
                               PerformanceMetricType.RESPONSE_TIME,
                               duration * 1000, "ms", 
                               {"endpoint": endpoint, "status": str(status_code)})
                
                del self.active_requests[request_id]
                
    def record_database_query(self, query: str, duration: float, success: bool = True):
        """Record database query performance"""
        self._add_metric("database_query_duration", PerformanceMetricType.DATABASE_QUERIES,
                       duration * 1000, "ms", 
                       {"query_type": self._classify_query(query), "success": str(success)})
                       
    def _classify_query(self, query: str) -> str:
        """Classify query type"""
        query_upper = query.upper().strip()
        if query_upper.startswith("SELECT"):
            return "SELECT"
        elif query_upper.startswith("INSERT"):
            return "INSERT"
        elif query_upper.startswith("UPDATE"):
            return "UPDATE"
        elif query_upper.startswith("DELETE"):
            return "DELETE"
        else:
            return "OTHER"
            
    def record_cache_operation(self, operation: str, hit: bool):
        """Record cache operation"""
        hit_rate = 0.0
        if "cache_hits" not in self.metrics or "cache_misses" not in self.metrics:
            cache_hits = 0
            cache_misses = 0
        else:
            cache_hits = len(self.metrics["cache_hits"])
            cache_misses = len(self.metrics["cache_misses"])
            total = cache_hits + cache_misses
            hit_rate = (cache_hits / total * 100) if total > 0 else 0
            
        if hit:
            self._add_metric("cache_hits", PerformanceMetricType.CACHE_HIT_RATE,
                           1, "count", {"operation": operation})
        else:
            self._add_metric("cache_misses", PerformanceMetricType.CACHE_HIT_RATE,
                           1, "count", {"operation": operation})
                           
        self._add_metric("cache_hit_rate", PerformanceMetricType.CACHE_HIT_RATE,
                       hit_rate, "percent", {"operation": operation})
                       
    def get_metrics(self, name: Optional[str] = None, 
                  since: Optional[datetime] = None) -> List[PerformanceMetric]:
        """Get performance metrics with optional filtering"""
        results = []
        
        for metric_name, metric_queue in self.metrics.items():
            if name and name not in metric_name:
                continue
                
            for metric in metric_queue:
                if since and metric.timestamp < since:
                    continue
                results.append(metric)
                
        return sorted(results, key=lambda x: x.timestamp)
        
    def get_profile(self, endpoint: str, 
                   since: Optional[datetime] = None) -> Optional[PerformanceProfile]:
        """Get performance profile for an endpoint"""
        if endpoint not in self.profiles:
            return None
            
        profiles = self.profiles[endpoint]
        if since:
            profiles = [p for p in profiles if p.timestamp >= since]
            
        if not profiles:
            return None
            
        # Return the most recent profile
        return max(profiles, key=lambda x: x.timestamp)
        
    def get_top_slow_endpoints(self, limit: int = 10, 
                              since: Optional[datetime] = None) -> List[PerformanceProfile]:
        """Get top slowest endpoints"""
        all_profiles = []
        
        for endpoint_profiles in self.profiles.values():
            if since:
                endpoint_profiles = [p for p in endpoint_profiles if p.timestamp >= since]
            all_profiles.extend(endpoint_profiles)
            
        # Sort by average response time
        return sorted(all_profiles, key=lambda x: x.avg_response_time, reverse=True)[:limit]
        
    def get_error_summary(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get error rate summary"""
        error_summary = {}
        
        for endpoint, error_count in self.error_counts.items():
            total_count = self.total_requests[endpoint]
            if total_count > 0:
                error_rate = (error_count / total_count) * 100
                error_summary[endpoint] = {
                    "error_count": error_count,
                    "total_requests": total_count,
                    "error_rate": error_rate
                }
                
        return error_summary
        
    def get_performance_summary(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get overall performance summary"""
        # Get recent metrics
        recent_time = since or (datetime.now() - timedelta(hours=1))
        
        # System metrics
        cpu_metrics = self.get_metrics("system_cpu", since=recent_time)
        memory_metrics = self.get_metrics("system_memory", since=recent_time)
        
        avg_cpu = statistics.mean([m.value for m in cpu_metrics]) if cpu_metrics else 0
        avg_memory = statistics.mean([m.value for m in memory_metrics]) if memory_metrics else 0
        
        # Request metrics
        response_time_metrics = [m for m in self.get_metrics(since=recent_time) 
                               if m.metric_type == PerformanceMetricType.RESPONSE_TIME]
        
        avg_response_time = statistics.mean([m.value for m in response_time_metrics]) if response_time_metrics else 0
        
        # Error rate
        error_summary = self.get_error_summary(since=recent_time)
        total_errors = sum(summary["error_count"] for summary in error_summary.values())
        total_requests = sum(summary["total_requests"] for summary in error_summary.values())
        overall_error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "period": str(datetime.now() - recent_time),
            "system_metrics": {
                "avg_cpu_percent": avg_cpu,
                "avg_memory_percent": avg_memory
            },
            "request_metrics": {
                "avg_response_time_ms": avg_response_time,
                "total_requests": total_requests,
                "error_rate_percent": overall_error_rate
            },
            "top_errors": dict(sorted(error_summary.items(), 
                                    key=lambda x: x[1]["error_rate"], 
                                    reverse=True)[:5])
        }


# Performance monitoring decorator
def monitor_performance(endpoint: Optional[str] = None):
    """Decorator to monitor function performance"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            request_id = f"{func.__name__}_{time.time()}"
            endpoint_name = endpoint or f"function:{func.__name__}"
            
            monitor.record_request_start(request_id, endpoint_name)
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                monitor.record_request_end(request_id, endpoint_name, 200)
                return result
            except Exception as e:
                monitor.record_request_end(request_id, endpoint_name, 500)
                raise
                
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            request_id = f"{func.__name__}_{time.time()}"
            endpoint_name = endpoint or f"function:{func.__name__}"
            
            monitor.record_request_start(request_id, endpoint_name)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                monitor.record_request_end(request_id, endpoint_name, 200)
                return result
            except Exception as e:
                monitor.record_request_end(request_id, endpoint_name, 500)
                raise
                
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


# FastAPI middleware
async def performance_middleware(request, call_next):
    """FastAPI middleware for performance monitoring"""
    monitor = get_performance_monitor()
    request_id = f"{request.method}_{request.url.path}_{time.time()}"
    endpoint = f"{request.method} {request.url.path}"
    
    monitor.record_request_start(request_id, endpoint)
    
    try:
        response = await call_next(request)
        monitor.record_request_end(request_id, endpoint, response.status_code)
        return response
    except Exception as e:
        monitor.record_request_end(request_id, endpoint, 500)
        raise


# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
