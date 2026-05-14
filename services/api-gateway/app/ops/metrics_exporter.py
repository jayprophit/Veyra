"""
Prometheus Metrics Exporter
============================
Exports system metrics for monitoring:
- Application metrics (requests, latency)
- Business metrics (orders, trades, P&L)
- System metrics (memory, CPU, connections)
- Custom trading metrics
"""

from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server, generate_latest
from prometheus_client.core import CollectorRegistry
from typing import Dict, Optional
import time
import functools
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Central metrics collection for Veyra.
    """
    
    def __init__(self, port: int = 9090):
        self.port = port
        self.registry = CollectorRegistry()
        
        # Application metrics
        self.http_requests_total = Counter(
            'fm_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'fm_http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry
        )
        
        # Trading metrics
        self.orders_total = Counter(
            'fm_orders_total',
            'Total orders submitted',
            ['symbol', 'side', 'status'],
            registry=self.registry
        )
        
        self.trades_total = Counter(
            'fm_trades_total',
            'Total trades executed',
            ['symbol', 'side'],
            registry=self.registry
        )
        
        self.trade_volume = Counter(
            'fm_trade_volume_shares',
            'Trade volume in shares',
            ['symbol'],
            registry=self.registry
        )
        
        self.pnl_gauge = Gauge(
            'fm_pnl_dollars',
            'Realized and unrealized P&L',
            ['type'],
            registry=self.registry
        )
        
        # WebSocket metrics
        self.ws_connections = Gauge(
            'fm_websocket_connections',
            'Active WebSocket connections',
            registry=self.registry
        )
        
        self.ws_messages = Counter(
            'fm_websocket_messages_total',
            'Total WebSocket messages',
            ['direction'],
            registry=self.registry
        )
        
        # AI/ML metrics
        self.ai_predictions = Counter(
            'fm_ai_predictions_total',
            'Total AI predictions made',
            ['model_type'],
            registry=self.registry
        )
        
        self.ai_latency = Histogram(
            'fm_ai_prediction_duration_seconds',
            'AI prediction latency',
            ['model_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
            registry=self.registry
        )
        
        # Risk metrics
        self.portfolio_var = Gauge(
            'fm_portfolio_var_dollars',
            'Portfolio Value at Risk',
            registry=self.registry
        )
        
        self.margin_utilization = Gauge(
            'fm_margin_utilization_percent',
            'Margin utilization percentage',
            registry=self.registry
        )
        
        # System info
        self.system_info = Info(
            'fm_system',
            'System information',
            registry=self.registry
        )
        
        # Module health
        self.module_health = Gauge(
            'fm_module_health',
            'Module health score (0-1)',
            ['module_name'],
            registry=self.registry
        )
        
        # Market data latency
        self.market_data_latency = Histogram(
            'fm_market_data_latency_seconds',
            'Market data feed latency',
            ['source'],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0],
            registry=self.registry
        )
        
    def start_server(self):
        """Start Prometheus HTTP server."""
        start_http_server(self.port, registry=self.registry)
        logger.info(f"Metrics server started on port {self.port}")
    
    def record_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_order(self, symbol: str, side: str, status: str):
        """Record order submission."""
        self.orders_total.labels(
            symbol=symbol,
            side=side,
            status=status
        ).inc()
    
    def record_trade(self, symbol: str, side: str, quantity: int):
        """Record executed trade."""
        self.trades_total.labels(
            symbol=symbol,
            side=side
        ).inc()
        
        self.trade_volume.labels(symbol=symbol).inc(quantity)
    
    def update_pnl(self, realized: float, unrealized: float):
        """Update P&L metrics."""
        self.pnl_gauge.labels(type='realized').set(realized)
        self.pnl_gauge.labels(type='unrealized').set(unrealized)
    
    def update_ws_connections(self, count: int):
        """Update WebSocket connection count."""
        self.ws_connections.set(count)
    
    def record_ws_message(self, direction: str):
        """Record WebSocket message."""
        self.ws_messages.labels(direction=direction).inc()
    
    def record_ai_prediction(self, model_type: str, latency: float):
        """Record AI prediction metrics."""
        self.ai_predictions.labels(model_type=model_type).inc()
        self.ai_latency.labels(model_type=model_type).observe(latency)
    
    def update_var(self, var_amount: float):
        """Update VaR metric."""
        self.portfolio_var.set(var_amount)
    
    def update_margin_utilization(self, percentage: float):
        """Update margin utilization."""
        self.margin_utilization.set(percentage)
    
    def update_module_health(self, module_name: str, score: float):
        """Update module health score."""
        self.module_health.labels(module_name=module_name).set(score)
    
    def record_market_data_latency(self, source: str, latency: float):
        """Record market data latency."""
        self.market_data_latency.labels(source=source).observe(latency)
    
    def set_system_info(self, version: str, environment: str):
        """Set system information."""
        self.system_info.info({
            'version': version,
            'environment': environment
        })
    
    def get_metrics(self) -> bytes:
        """Get current metrics for scraping."""
        return generate_latest(self.registry)


# Decorator for timing functions
def timed(metric_name: str):
    """Decorator to time function execution."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                # Record metric if collector available
                if hasattr(async_wrapper, '_metrics_collector'):
                    async_wrapper._metrics_collector.ai_latency.observe(duration)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                if hasattr(sync_wrapper, '_metrics_collector'):
                    sync_wrapper._metrics_collector.ai_latency.observe(duration)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Global instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# FastAPI middleware integration
class MetricsMiddleware:
    """FastAPI middleware for automatic metrics collection."""
    
    def __init__(self, app):
        self.app = app
        self.collector = get_metrics_collector()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        method = scope.get("method", "GET")
        path = scope.get("path", "/")
        
        # Wrap send to capture status code
        status_code = 200
        
        async def wrapped_send(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
            await send(message)
        
        await self.app(scope, receive, wrapped_send)
        
        duration = time.time() - start_time
        self.collector.record_http_request(method, path, status_code, duration)


# Example usage
if __name__ == "__main__":
    # Start metrics server
    collector = get_metrics_collector()
    collector.start_server()
    
    # Simulate some metrics
    collector.set_system_info("2.50.0", "production")
    
    while True:
        # Record sample metrics
        collector.record_order("AAPL", "buy", "filled")
        collector.record_trade("AAPL", "buy", 100)
        collector.update_pnl(500.0, 1200.0)
        collector.update_ws_connections(42)
        collector.update_var(2500.0)
        collector.update_module_health("market_data", 0.98)
        
        time.sleep(10)
