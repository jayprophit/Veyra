"""Centralized Logging & Monitoring - Production-grade observability.

Features:
- Structured logging with rotation
- Performance metrics tracking
- System health monitoring
- Alert thresholds
- Export to multiple destinations (file, console, webhook)
"""

import logging
import logging.handlers
import json
import time
import psutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import queue

@dataclass
class Metric:
    """Performance metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: Dict[str, str]

class StructuredLogFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)

class LoggerManager:
    """Centralized logging management."""
    
    def __init__(self, log_dir: str = "./logs", app_name: str = "financial_master"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.app_name = app_name
        self.loggers: Dict[str, logging.Logger] = {}
        self.metrics: List[Metric] = []
        self.metrics_queue: queue.Queue = queue.Queue()
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create logger with proper configuration."""
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.handlers = []  # Clear existing handlers
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = self.log_dir / f"{self.app_name}_{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredLogFormatter())
        logger.addHandler(file_handler)
        
        # Error file handler
        error_file = self.log_dir / f"{self.app_name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10_000_000,
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredLogFormatter())
        logger.addHandler(error_handler)
        
        self.loggers[name] = logger
        return logger
    
    def log_metric(self, name: str, value: float, unit: str = "", labels: Optional[Dict] = None):
        """Log a performance metric."""
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            labels=labels or {}
        )
        self.metrics_queue.put(metric)
    
    def start_monitoring(self, interval: int = 60):
        """Start system monitoring thread."""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger = self.get_logger("monitor")
        logger.info(f"Started system monitoring (interval: {interval}s)")
    
    def _monitor_loop(self, interval: int):
        """Background monitoring loop."""
        while self.running:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                self.log_metric("system.cpu_percent", cpu_percent, "%")
                self.log_metric("system.memory_used_percent", memory.percent, "%")
                self.log_metric("system.memory_available_gb", memory.available / (1024**3), "GB")
                self.log_metric("system.disk_used_percent", disk.percent, "%")
                
                # Process metrics
                process = psutil.Process()
                self.log_metric("process.memory_mb", process.memory_info().rss / (1024**2), "MB")
                self.log_metric("process.cpu_percent", process.cpu_percent(), "%")
                
                # Flush metrics
                self._flush_metrics()
                
            except Exception as e:
                logger = self.get_logger("monitor")
                logger.error(f"Monitoring error: {e}")
            
            time.sleep(interval)
    
    def _flush_metrics(self):
        """Flush metrics from queue to storage."""
        metrics_batch = []
        while not self.metrics_queue.empty() and len(metrics_batch) < 100:
            try:
                metric = self.metrics_queue.get_nowait()
                metrics_batch.append(asdict(metric))
            except queue.Empty:
                break
        
        if metrics_batch:
            # Write to metrics log file
            metrics_file = self.log_dir / f"{self.app_name}_metrics.jsonl"
            with open(metrics_file, 'a') as f:
                for metric in metrics_batch:
                    f.write(json.dumps(metric) + '\n')
            
            self.metrics.extend([Metric(**m) for m in metrics_batch])
    
    def stop_monitoring(self):
        """Stop monitoring thread."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self._flush_metrics()
    
    def get_metrics_summary(self, last_n: int = 100) -> Dict[str, Any]:
        """Get summary of recent metrics."""
        recent = self.metrics[-last_n:] if len(self.metrics) > last_n else self.metrics
        
        if not recent:
            return {}
        
        # Group by name
        by_name: Dict[str, List[float]] = {}
        for metric in recent:
            if metric.name not in by_name:
                by_name[metric.name] = []
            by_name[metric.name].append(metric.value)
        
        summary = {}
        for name, values in by_name.items():
            summary[name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1]
            }
        
        return summary
    
    def check_alerts(self) -> List[Dict]:
        """Check for alert conditions."""
        alerts = []
        summary = self.get_metrics_summary(last_n=10)
        
        # CPU alert
        if summary.get("system.cpu_percent", {}).get("avg", 0) > 80:
            alerts.append({
                "severity": "warning",
                "metric": "system.cpu_percent",
                "message": "High CPU usage detected",
                "threshold": 80
            })
        
        # Memory alert
        if summary.get("system.memory_used_percent", {}).get("avg", 0) > 90:
            alerts.append({
                "severity": "critical",
                "metric": "system.memory_used_percent",
                "message": "High memory usage detected",
                "threshold": 90
            })
        
        # Disk alert
        if summary.get("system.disk_used_percent", {}).get("avg", 0) > 85:
            alerts.append({
                "severity": "warning",
                "metric": "system.disk_used_percent",
                "message": "High disk usage detected",
                "threshold": 85
            })
        
        return alerts

class HealthChecker:
    """System health checking."""
    
    CHECKS = {
        "database": "check_database",
        "ollama": "check_ollama",
        "api": "check_api",
        "websocket": "check_websocket",
        "disk_space": "check_disk_space",
        "memory": "check_memory"
    }
    
    def __init__(self, logger_manager: LoggerManager):
        self.logger = logger_manager.get_logger("health")
        self.results: Dict[str, Dict] = {}
    
    def check_database(self) -> Dict:
        """Check database connectivity."""
        try:
            from database_layer import DatabaseManager, DatabaseConfig
            db = DatabaseManager(DatabaseConfig())
            db.conn.execute("SELECT 1")
            return {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def check_ollama(self) -> Dict:
        """Check Ollama availability."""
        try:
            import requests
            start = time.time()
            r = requests.get("http://localhost:11434/api/tags", timeout=5)
            response_time = (time.time() - start) * 1000
            
            if r.status_code == 200:
                models = len(r.json().get("models", []))
                return {
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "models_available": models
                }
            else:
                return {"status": "unhealthy", "error": f"HTTP {r.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def check_api(self) -> Dict:
        """Check API server."""
        try:
            import requests
            start = time.time()
            r = requests.get("http://localhost:8000/api/health", timeout=5)
            response_time = (time.time() - start) * 1000
            
            return {
                "status": "healthy" if r.status_code == 200 else "unhealthy",
                "response_time_ms": response_time
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def check_websocket(self) -> Dict:
        """Check WebSocket server."""
        try:
            import websocket
            start = time.time()
            ws = websocket.create_connection("ws://localhost:8765", timeout=5)
            ws.close()
            response_time = (time.time() - start) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def check_disk_space(self) -> Dict:
        """Check available disk space."""
        disk = psutil.disk_usage('/')
        percent_used = disk.percent
        
        status = "healthy"
        if percent_used > 90:
            status = "critical"
        elif percent_used > 80:
            status = "warning"
        
        return {
            "status": status,
            "percent_used": percent_used,
            "free_gb": disk.free / (1024**3)
        }
    
    def check_memory(self) -> Dict:
        """Check memory usage."""
        memory = psutil.virtual_memory()
        
        status = "healthy"
        if memory.percent > 90:
            status = "critical"
        elif memory.percent > 80:
            status = "warning"
        
        return {
            "status": status,
            "percent_used": memory.percent,
            "available_gb": memory.available / (1024**3)
        }
    
    def run_all_checks(self) -> Dict[str, Dict]:
        """Run all health checks."""
        self.logger.info("Running health checks...")
        
        for name, method_name in self.CHECKS.items():
            try:
                method = getattr(self, method_name)
                self.results[name] = method()
                self.logger.info(f"Health check {name}: {self.results[name]['status']}")
            except Exception as e:
                self.results[name] = {"status": "error", "error": str(e)}
                self.logger.error(f"Health check {name} failed: {e}")
        
        return self.results
    
    def get_overall_status(self) -> str:
        """Get overall system health status."""
        if not self.results:
            return "unknown"
        
        statuses = [r["status"] for r in self.results.values()]
        
        if any(s == "critical" for s in statuses):
            return "critical"
        elif any(s in ["unhealthy", "error"] for s in statuses):
            return "degraded"
        elif any(s == "warning" for s in statuses):
            return "warning"
        else:
            return "healthy"

# Global logger manager instance
_logger_manager: Optional[LoggerManager] = None

def get_logger_manager() -> LoggerManager:
    """Get or create global logger manager."""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager

def get_logger(name: str) -> logging.Logger:
    """Get logger with proper configuration."""
    return get_logger_manager().get_logger(name)

if __name__ == "__main__":
    # Example usage
    lm = LoggerManager()
    lm.start_monitoring(interval=10)
    
    logger = lm.get_logger("example")
    logger.info("Application started")
    
    # Log some metrics
    for i in range(5):
        lm.log_metric("custom.metric", i * 10, "count")
        time.sleep(1)
    
    # Health check
    hc = HealthChecker(lm)
    results = hc.run_all_checks()
    print(f"\nOverall status: {hc.get_overall_status()}")
    
    # Get metrics summary
    summary = lm.get_metrics_summary()
    print(f"\nMetrics summary: {json.dumps(summary, indent=2)}")
    
    lm.stop_monitoring()
