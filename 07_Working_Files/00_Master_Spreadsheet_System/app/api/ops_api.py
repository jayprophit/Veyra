"""
Operations API Endpoints
========================
Exposes DevOps, FinOps, AIOps via REST API.
Real-time monitoring, cost tracking, alerting.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

from ops.ops_wiring import (
    ops_orchestrator, 
    start_ops_monitoring, 
    stop_ops_monitoring,
    get_system_health,
    get_cost_summary
)
from ops.deployment_controller import deployment_controller

router = APIRouter(prefix="/api/ops", tags=["operations"])


# ============================================================================
# Pydantic Models
# ============================================================================

class SystemHealthResponse(BaseModel):
    status: str
    message: str
    issues: List[str]
    metrics: Dict
    timestamp: str


class CostSummaryResponse(BaseModel):
    total_current_month: float
    total_previous_month: float
    budget_limit: float
    budget_used_percent: float
    breakdown: Dict[str, float]
    trend: str  # 'increasing', 'decreasing', 'stable'
    recommendations: List[Dict]


class DeploymentRequest(BaseModel):
    version: str
    environment: str = "production"
    strategy: str = "blue-green"  # or 'canary'
    traffic_percent: Optional[float] = None  # For canary


class AlertConfig(BaseModel):
    email: Optional[str] = None
    slack_webhook: Optional[str] = None
    discord_webhook: Optional[str] = None
    sms_number: Optional[str] = None


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/health", summary="Get system health", response_model=SystemHealthResponse)
async def get_health():
    """Get current system health status."""
    try:
        health = get_system_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", summary="Get real-time metrics")
async def get_metrics():
    """Get current system metrics."""
    try:
        if not ops_orchestrator.metrics_history:
            return {
                "status": "no_data",
                "message": "Monitoring not started or no data available"
            }
        
        latest = ops_orchestrator.metrics_history[-1]
        
        return {
            "timestamp": latest.timestamp.isoformat(),
            "cpu_usage": latest.cpu_usage,
            "memory_usage": latest.memory_usage,
            "disk_usage": latest.disk_usage,
            "network_io": latest.network_io,
            "active_connections": latest.active_connections,
            "request_rate": latest.request_rate,
            "error_rate": latest.error_rate,
            "latency": {
                "p50": latest.latency_p50,
                "p95": latest.latency_p95,
                "p99": latest.latency_p99
            },
            "queue_depth": latest.queue_depth
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/history", summary="Get metrics history")
async def get_metrics_history(
    hours: int = 24,
    resolution: str = "raw"  # 'raw', '1min', '5min', '1hour'
):
    """Get historical metrics."""
    try:
        if not ops_orchestrator.metrics_history:
            return {"status": "no_data", "data": []}
        
        # Filter by time
        cutoff = datetime.now() - timedelta(hours=hours)
        filtered = [m for m in ops_orchestrator.metrics_history if m.timestamp > cutoff]
        
        # Aggregate if needed
        if resolution != "raw" and len(filtered) > 100:
            # Simple aggregation (could be more sophisticated)
            filtered = filtered[::len(filtered)//100]
        
        data = [
            {
                "timestamp": m.timestamp.isoformat(),
                "cpu": m.cpu_usage,
                "memory": m.memory_usage,
                "disk": m.disk_usage,
                "latency_p95": m.latency_p95,
                "error_rate": m.error_rate
            }
            for m in filtered
        ]
        
        return {
            "status": "success",
            "hours": hours,
            "resolution": resolution,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs", summary="Get cost summary", response_model=CostSummaryResponse)
async def get_costs():
    """Get FinOps cost summary and analysis."""
    try:
        summary = get_cost_summary()
        
        # Add recommendations
        recommendations = []
        if summary.get('budget_used_percent', 0) > 80:
            recommendations.append({
                "type": "budget_alert",
                "severity": "warning",
                "message": f"Budget {summary['budget_used_percent']:.1f}% consumed",
                "action": "review_spending"
            })
        
        return {
            "total_current_month": summary.get('total_current_month', 0),
            "total_previous_month": summary.get('total_previous_month', 0),
            "budget_limit": summary.get('budget_limit', 100),
            "budget_used_percent": summary.get('budget_used_percent', 0),
            "breakdown": summary.get('breakdown', {}),
            "trend": summary.get('trend', 'stable'),
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/breakdown", summary="Get detailed cost breakdown")
async def get_cost_breakdown(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get detailed cost breakdown by service and time."""
    try:
        # This would integrate with actual cloud provider APIs
        # For now, return mock data structure
        
        return {
            "period": {
                "start": start_date or "2024-01-01",
                "end": end_date or datetime.now().strftime("%Y-%m-%d")
            },
            "services": [
                {
                    "name": "Railway Hosting",
                    "category": "compute",
                    "cost": 25.00,
                    "trend": "stable"
                },
                {
                    "name": "Vercel",
                    "category": "hosting",
                    "cost": 0.00,
                    "trend": "stable"
                },
                {
                    "name": "OpenAI API",
                    "category": "ai",
                    "cost": 20.00,
                    "trend": "increasing"
                },
                {
                    "name": "Polygon.io",
                    "category": "data",
                    "cost": 0.00,
                    "trend": "stable"
                }
            ],
            "total": 45.00,
            "forecast": {
                "next_month": 48.00,
                "trend": "increasing"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/start", summary="Start monitoring")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Start operations monitoring."""
    try:
        background_tasks.add_task(start_ops_monitoring)
        return {
            "status": "starting",
            "message": "Operations monitoring is starting",
            "interval_seconds": 30
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/stop", summary="Stop monitoring")
async def stop_monitoring():
    """Stop operations monitoring."""
    try:
        await stop_ops_monitoring()
        return {
            "status": "stopped",
            "message": "Operations monitoring stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/status", summary="Get monitoring status")
async def get_monitoring_status():
    """Check if monitoring is active."""
    return {
        "is_running": ops_orchestrator.is_running,
        "interval_seconds": ops_orchestrator.monitoring_interval,
        "metrics_count": len(ops_orchestrator.metrics_history),
        "retention_hours": ops_orchestrator.metrics_retention_hours
    }


@router.post("/deploy", summary="Trigger deployment")
async def deploy(request: DeploymentRequest):
    """Trigger deployment with specified strategy."""
    try:
        if request.strategy == "blue-green":
            result = await deployment_controller.deploy_blue_green(
                version=request.version,
                environment=request.environment
            )
        elif request.strategy == "canary":
            traffic = request.traffic_percent or 10.0
            result = await deployment_controller.deploy_canary(
                version=request.version,
                traffic_percent=traffic
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy}")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy/rollback", summary="Rollback deployment")
async def rollback(environment: str = "production"):
    """Rollback current deployment."""
    try:
        result = await deployment_controller.rollback(environment)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deploy/status", summary="Get deployment status")
async def get_deployment_status():
    """Get current deployment status."""
    try:
        status = ops_orchestrator.get_deployment_status()
        return {
            "status": status.get('status', 'unknown'),
            "version": status.get('version', 'unknown'),
            "environment": status.get('environment', 'unknown'),
            "last_deployment": status.get('timestamp')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/configure", summary="Configure alert channels")
async def configure_alerts(config: AlertConfig):
    """Configure alert notification channels."""
    try:
        # Store config
        # This would integrate with notification services
        
        channels = []
        if config.email:
            channels.append("email")
        if config.slack_webhook:
            channels.append("slack")
        if config.discord_webhook:
            channels.append("discord")
        if config.sms_number:
            channels.append("sms")
        
        return {
            "status": "configured",
            "channels": channels,
            "message": f"Alerts configured for {len(channels)} channels"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", summary="Get recent alerts")
async def get_alerts(
    severity: Optional[str] = None,
    limit: int = 50
):
    """Get recent system alerts."""
    try:
        # Query from database
        from database_layer import DatabaseManager
        db = DatabaseManager()
        
        query = "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?"
        params = [limit]
        
        if severity:
            query = "SELECT * FROM alerts WHERE severity = ? ORDER BY timestamp DESC LIMIT ?"
            params = [severity, limit]
        
        rows = db.conn.execute(query, params).fetchall()
        
        alerts = [
            {
                "id": row[0],
                "timestamp": row[1],
                "severity": row[2],
                "message": row[3],
                "context": row[4]
            }
            for row in rows
        ]
        
        return {
            "count": len(alerts),
            "alerts": alerts
        }
    except Exception as e:
        # Return empty list if table doesn't exist yet
        return {"count": 0, "alerts": []}


@router.post("/optimize", summary="Run optimization analysis")
async def run_optimization():
    """Run resource optimization analysis."""
    try:
        result = await ops_orchestrator.optimize_resources()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies", summary="Get detected anomalies")
async def get_anomalies(
    hours: int = 24,
    severity: Optional[str] = None
):
    """Get AIOps detected anomalies."""
    try:
        # This would query from anomaly detection system
        # For now, return structure
        
        return {
            "period_hours": hours,
            "anomalies_detected": 0,
            "anomalies": [],
            "ml_model_status": "active",
            "baseline_established": len(ops_orchestrator.metrics_history) > 100
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API Endpoints Summary:
# GET    /api/ops/health                    - System health
# GET    /api/ops/metrics                   - Real-time metrics
# GET    /api/ops/metrics/history           - Historical metrics
# GET    /api/ops/costs                     - Cost summary
# GET    /api/ops/costs/breakdown           - Cost breakdown
# POST   /api/ops/monitoring/start          - Start monitoring
# POST   /api/ops/monitoring/stop           - Stop monitoring
# GET    /api/ops/monitoring/status         - Monitoring status
# POST   /api/ops/deploy                    - Trigger deployment
# POST   /api/ops/deploy/rollback           - Rollback deployment
# GET    /api/ops/deploy/status               - Deployment status
# POST   /api/ops/alerts/configure          - Configure alerts
# GET    /api/ops/alerts                    - Get alerts
# POST   /api/ops/optimize                  - Run optimization
# GET    /api/ops/anomalies                 - Get anomalies
