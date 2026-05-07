"""
Observability API Endpoints
=============================
Enterprise observability and monitoring API
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from ..observability import (
    get_observability_manager,
    get_metrics_collector,
    get_tracer,
    get_log_aggregator,
    get_health_monitor,
    get_performance_monitor,
    get_alerting_system
)
from ..observability.log_aggregator import LogLevel
from ..observability.alerting_system import AlertSeverity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/status")
async def get_observability_status():
    """Get observability system status"""
    manager = get_observability_manager()
    return manager.get_status()


@router.get("/health")
async def get_comprehensive_health():
    """Get comprehensive health and observability status"""
    manager = get_observability_manager()
    return await manager.get_comprehensive_health()


@router.get("/metrics")
async def get_metrics(
    name: Optional[str] = Query(None, description="Filter by metric name"),
    since: Optional[datetime] = Query(None, description="Filter by timestamp since")
):
    """Get performance metrics"""
    collector = get_metrics_collector()
    metrics = collector.get_metrics(name_filter=name, since=since)
    
    return {
        "metrics": [
            {
                "name": m.name,
                "value": m.value,
                "type": m.metric_type.value,
                "unit": m.unit,
                "timestamp": m.timestamp.isoformat(),
                "labels": m.labels
            }
            for m in metrics
        ],
        "count": len(metrics)
    }


@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get metrics in Prometheus format"""
    collector = get_metrics_collector()
    return Response(
        content=collector.get_prometheus_metrics(),
        media_type="text/plain"
    )


@router.get("/traces")
async def get_traces(
    trace_id: Optional[str] = Query(None, description="Filter by trace ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of traces")
):
    """Get distributed traces"""
    tracer = get_tracer()
    
    if trace_id:
        traces = [tracer.get_trace(trace_id)]
    else:
        # Get recent traces
        traces = []
        for span in tracer.spans.values():
            if len(traces) >= limit:
                break
            traces.append([span])
    
    return {
        "traces": [
            {
                "trace_id": trace[0].trace_id if trace else "",
                "spans": [
                    {
                        "span_id": span.span_id,
                        "parent_span_id": span.parent_span_id,
                        "name": span.name,
                        "kind": span.kind.value,
                        "start_time": span.start_time.isoformat(),
                        "end_time": span.end_time.isoformat() if span.end_time else None,
                        "duration_ms": span.duration_ms,
                        "status_code": span.status_code.value,
                        "status_message": span.status_message,
                        "attributes": span.attributes,
                        "events": [
                            {
                                "timestamp": event.timestamp.isoformat(),
                                "name": event.name,
                                "attributes": event.attributes
                            }
                            for event in span.events
                        ]
                    }
                    for span in trace
                ]
            }
            for trace in traces
        ],
        "count": len(traces)
    }


@router.get("/logs")
async def get_logs(
    level: Optional[LogLevel] = Query(None, description="Filter by log level"),
    service: Optional[str] = Query(None, description="Filter by service name"),
    trace_id: Optional[str] = Query(None, description="Filter by trace ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    since: Optional[datetime] = Query(None, description="Filter by timestamp since"),
    until: Optional[datetime] = Query(None, description="Filter by timestamp until"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs")
):
    """Get log entries"""
    aggregator = get_log_aggregator()
    logs = aggregator.query_logs(
        level=level,
        service=service,
        trace_id=trace_id,
        user_id=user_id,
        since=since,
        until=until,
        limit=limit
    )
    
    return {
        "logs": [
            {
                "timestamp": log.timestamp.isoformat(),
                "level": log.level.value,
                "message": log.message,
                "service": log.service,
                "trace_id": log.trace_id,
                "span_id": log.span_id,
                "user_id": log.user_id,
                "request_id": log.request_id,
                "source_file": log.source_file,
                "source_line": log.source_line,
                "function_name": log.function_name,
                "exception": log.exception,
                "stack_trace": log.stack_trace,
                "tags": log.tags,
                "fields": log.fields
            }
            for log in logs
        ],
        "count": len(logs)
    }


@router.get("/health/checks")
async def get_health_checks():
    """Get detailed health checks"""
    monitor = get_health_monitor()
    return monitor.get_overall_health()


@router.get("/health/liveness")
async def get_liveness():
    """Get liveness probe status"""
    monitor = get_health_monitor()
    return await monitor.run_liveness_check()


@router.get("/health/readiness")
async def get_readiness():
    """Get readiness probe status"""
    monitor = get_health_monitor()
    return await monitor.run_readiness_check()


@router.get("/health/startup")
async def get_startup():
    """Get startup probe status"""
    monitor = get_health_monitor()
    return await monitor.run_startup_check()


@router.get("/performance")
async def get_performance_metrics(
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    since: Optional[datetime] = Query(None, description="Filter by timestamp since")
):
    """Get performance metrics"""
    monitor = get_performance_monitor()
    
    if endpoint:
        profile = monitor.get_profile(endpoint, since=since)
        return {
            "profile": {
                "endpoint": profile.endpoint,
                "method": profile.method,
                "avg_response_time": profile.avg_response_time,
                "p95_response_time": profile.p95_response_time,
                "p99_response_time": profile.p99_response_time,
                "requests_per_second": profile.requests_per_second,
                "error_rate": profile.error_rate,
                "timestamp": profile.timestamp.isoformat(),
                "sample_count": profile.sample_count
            }
        } if profile else {"error": "Profile not found"}
    else:
        summary = monitor.get_performance_summary(since=since)
        return summary


@router.get("/performance/slow-endpoints")
async def get_slow_endpoints(
    limit: int = Query(10, ge=1, le=100, description="Number of endpoints to return"),
    since: Optional[datetime] = Query(None, description="Filter by timestamp since")
):
    """Get slowest endpoints"""
    monitor = get_performance_monitor()
    profiles = monitor.get_top_slow_endpoints(limit=limit, since=since)
    
    return {
        "slow_endpoints": [
            {
                "endpoint": profile.endpoint,
                "method": profile.method,
                "avg_response_time": profile.avg_response_time,
                "p95_response_time": profile.p95_response_time,
                "p99_response_time": profile.p99_response_time,
                "requests_per_second": profile.requests_per_second,
                "error_rate": profile.error_rate,
                "timestamp": profile.timestamp.isoformat(),
                "sample_count": profile.sample_count
            }
            for profile in profiles
        ]
    }


@router.get("/performance/errors")
async def get_error_summary(
    since: Optional[datetime] = Query(None, description="Filter by timestamp since")
):
    """Get error rate summary"""
    monitor = get_performance_monitor()
    return monitor.get_error_summary(since=since)


@router.get("/alerts")
async def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    since: Optional[datetime] = Query(None, description="Filter by timestamp since")
):
    """Get alerts"""
    alerting = get_alerting_system()
    
    if status == "active":
        alerts = alerting.get_active_alerts()
    else:
        alerts = alerting.get_alert_history(since=since)
    
    # Filter by severity if specified
    if severity:
        alerts = [alert for alert in alerts if alert.severity == severity]
    
    return {
        "alerts": [
            {
                "name": alert.name,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "message": alert.message,
                "description": alert.description,
                "timestamp": alert.timestamp.isoformat(),
                "start_time": alert.start_time.isoformat(),
                "end_time": alert.end_time.isoformat() if alert.end_time else None,
                "labels": alert.labels,
                "annotations": alert.annotations,
                "fingerprint": alert.fingerprint
            }
            for alert in alerts
        ],
        "count": len(alerts)
    }


@router.post("/alerts/trigger")
async def trigger_alert(
    name: str,
    severity: AlertSeverity,
    message: str,
    description: str = "",
    labels: Optional[Dict[str, str]] = None,
    annotations: Optional[Dict[str, str]] = None
):
    """Trigger a manual alert"""
    from ..observability.alerting_system import trigger_alert
    
    await trigger_alert(
        name=name,
        severity=severity,
        message=message,
        description=description,
        labels=labels,
        annotations=annotations
    )
    
    return {"message": "Alert triggered successfully"}


@router.post("/alerts/resolve")
async def resolve_alert(
    name: str,
    labels: Optional[Dict[str, str]] = None
):
    """Resolve a manual alert"""
    from ..observability.alerting_system import resolve_alert
    
    await resolve_alert(name=name, labels=labels)
    
    return {"message": "Alert resolved successfully"}


@router.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    manager = get_observability_manager()
    health = await manager.get_comprehensive_health()
    
    return {
        "overview": {
            "status": health["health"]["status"],
            "message": health["health"]["message"],
            "timestamp": health["health"]["timestamp"]
        },
        "metrics": health["observability"]["metrics_summary"],
        "alerts": {
            "active": health["observability"]["active_alerts"],
            "recent": len(get_alerting_system().get_alert_history(
                since=datetime.now() - timedelta(hours=24)
            ))
        },
        "system": health["observability"]["system_metrics"]
    }


# Import Response for Prometheus metrics
from fastapi.responses import Response
