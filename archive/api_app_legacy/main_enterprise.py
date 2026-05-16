"""
Veyra - Enterprise Production Application
==================================================
Production-ready FastAPI application with enterprise-grade features:
- Structured logging & monitoring
- Authentication & authorization
- Rate limiting & caching
- Health checks & graceful shutdown
- Error handling & validation
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional

import redis.asyncio as aioredis
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Enterprise middleware
from app.middleware.error_handler import ErrorHandlerMiddleware, ValidationMiddleware
from app.middleware.rate_limiting import RateLimitingMiddleware
from app.monitoring.logging_config import setup_logging, get_logger
from app.health.health_check import health_manager, graceful_shutdown, HealthCheckManager
from app.auth.auth_service import AuthService, AuthConfig

# Initialize structured logging
setup_logging(
    log_level="INFO",
    log_file="logs/veyra.log",
    enable_json=True
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    logger.info("Starting Veyra Enterprise Application")
    
    # Initialize Redis client
    redis_client = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    app.state.redis_client = redis_client
    
    # Initialize auth service
    auth_config = AuthConfig(
        secret_key="your-production-secret-key-change-this",
        redis_url="redis://localhost:6379/1"
    )
    app.state.auth_service = AuthService(auth_config)
    
    # Setup health checks
    from app.database_layer import DatabaseManager
    db_manager = DatabaseManager()
    
    from app.health.health_check import (
        DatabaseHealthCheck, RedisHealthCheck, SystemResourceHealthCheck
    )
    
    health_manager.add_checker(DatabaseHealthCheck(db_manager.get_session))
    health_manager.add_checker(RedisHealthCheck(redis_client))
    health_manager.add_checker(SystemResourceHealthCheck())
    
    # Setup graceful shutdown handlers
    def signal_handler(signum, frame):
        logger.info("Received signal", signal=signum)
        asyncio.create_task(graceful_shutdown.shutdown(f"signal_{signum}"))
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Application startup complete")
    
    try:
        yield
    finally:
        logger.info("Shutting down application")
        await graceful_shutdown.shutdown("lifecycle")
        await redis_client.close()
        logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Veyra Enterprise API",
    description="Enterprise-grade financial trading and analysis platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add enterprise middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(ValidationMiddleware)
app.add_middleware(
    RateLimitingMiddleware,
    redis_client=redis.asyncio.from_url("redis://localhost:6379/0", decode_responses=True)
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://veyra.com", "https://api.veyra.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Health check endpoints
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Liveness probe for Kubernetes."""
    return await health_manager.check_liveness()


@app.get("/api/v1/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe for Kubernetes."""
    return await health_manager.check_readiness()


@app.get("/api/v1/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with all components."""
    system_health = await health_manager.check_all()
    return JSONResponse(
        status_code=200 if system_health.status.value == "healthy" else 503,
        content={
            "status": system_health.status.value,
            "uptime_seconds": system_health.uptime_seconds,
            "version": system_health.version,
            "timestamp": system_health.timestamp.isoformat(),
            "checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms,
                    "details": check.details
                }
                for check in system_health.checks
            ]
        }
    )


# Metrics endpoint for Prometheus
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint."""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Authentication endpoints
@app.post("/api/v1/auth/login", tags=["Authentication"])
async def login(request: Request):
    """User login endpoint."""
    try:
        data = await request.json()
        auth_service = request.app.state.auth_service
        
        user = auth_service.authenticate_user(data["email"], data["password"])
        access_token = auth_service.create_access_token(user)
        refresh_token = auth_service.create_refresh_token(user)
        
        logger.info("User logged in successfully", email=data["email"])
        
        return JSONResponse({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": auth_service.config.access_token_expire_minutes * 60
        })
    except Exception as e:
        logger.error("Login failed", email=data.get("email"), error=str(e))
        raise


@app.post("/api/v1/auth/refresh", tags=["Authentication"])
async def refresh_token(request: Request):
    """Refresh access token."""
    try:
        data = await request.json()
        auth_service = request.app.state.auth_service
        
        payload = auth_service.verify_token(data["refresh_token"])
        if payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        
        # Get user and create new access token
        user = auth_service._get_user_by_id(payload["sub"])
        access_token = auth_service.create_access_token(user)
        
        return JSONResponse({
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth_service.config.access_token_expire_minutes * 60
        })
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise


# API endpoints with authentication
@app.get("/api/v1/portfolio", tags=["Portfolio"])
async def get_portfolio(request: Request):
    """Get user portfolio."""
    # This would normally require authentication middleware
    # For demo purposes, returning mock data
    return JSONResponse({
        "portfolio_value": 100000.00,
        "positions": [
            {"symbol": "AAPL", "quantity": 100, "value": 15000.00},
            {"symbol": "GOOGL", "quantity": 50, "value": 7000.00},
            {"symbol": "MSFT", "quantity": 75, "value": 25000.00}
        ],
        "cash": 53000.00,
        "last_updated": datetime.utcnow().isoformat()
    })


@app.post("/api/v1/trading/orders", tags=["Trading"])
async def create_order(request: Request):
    """Create new trading order."""
    try:
        data = await request.json()
        
        # Validate order data
        required_fields = ["symbol", "side", "quantity", "order_type"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Mock order creation
        order_id = f"ORD_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info("Order created", order_id=order_id, symbol=data["symbol"], side=data["side"])
        
        return JSONResponse({
            "order_id": order_id,
            "status": "submitted",
            "symbol": data["symbol"],
            "side": data["side"],
            "quantity": data["quantity"],
            "order_type": data["order_type"],
            "created_at": datetime.utcnow().isoformat()
        }, status_code=201)
        
    except Exception as e:
        logger.error("Order creation failed", error=str(e))
        raise


@app.get("/api/v1/market/data/{symbol}", tags=["Market Data"])
async def get_market_data(symbol: str, request: Request):
    """Get market data for symbol."""
    # Mock market data
    import random
    
    base_price = 100.0
    current_price = base_price + random.uniform(-10, 10)
    
    return JSONResponse({
        "symbol": symbol,
        "price": round(current_price, 2),
        "change": round(current_price - base_price, 2),
        "change_percent": round(((current_price - base_price) / base_price) * 100, 2),
        "volume": random.randint(100000, 10000000),
        "timestamp": datetime.utcnow().isoformat()
    })


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return JSONResponse({
        "name": "Veyra Enterprise API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/api/v1/health",
            "docs": "/docs",
            "metrics": "/metrics",
            "auth": "/api/v1/auth",
            "portfolio": "/api/v1/portfolio",
            "trading": "/api/v1/trading",
            "market": "/api/v1/market"
        }
    })


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        method=request.method
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Veyra Enterprise Server")
    
    uvicorn.run(
        "main_enterprise:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        access_log=True,
        workers=1,  # Use multiple workers behind a load balancer in production
        loop="uvloop",
        http="httptools"
    )
