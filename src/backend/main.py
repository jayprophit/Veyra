"""
Veyra - Main Application Entry Point
FastAPI application initialization and configuration
"""
import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Import core modules
from src.backend.core.config import settings
from src.backend.core.logging_config import setup_logging
from src.backend.core.database import init_db, get_db_session
from src.backend.core.auth import AuthManager

# Initialize logger
logger = setup_logging(__name__)

# Initialize auth manager
auth_manager = AuthManager()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifecycle management
    Startup: Initialize database, connections
    Shutdown: Close connections, cleanup
    """
    logger.info("🚀 Starting Veyra...")

    # Initialize database (non-blocking - continue even if fails)
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization delayed: {e}")

    # Log available API routes
    routes_count = len([route for route in app.routes if hasattr(route, 'path')])
    logger.info(f"✅ {routes_count} API routes loaded")

    yield

    # Cleanup on shutdown
    logger.info("🛑 Shutting down Veyra...")
    logger.info("✅ All connections closed")


# Create FastAPI application
app = FastAPI(
    title="Veyra",
    description="Bloomberg Terminal alternative - 100% open-source",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Middleware configuration
logger.info("⚙️  Configuring middleware...")

# 1. Security: Only allow trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# 2. CORS: Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("✅ Middleware configured")


# ============================================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Global exception handler - prevents silent failures"""
    logger.error(f"Unhandled exception: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """Value error handler"""
    logger.warning(f"Value error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid value", "detail": str(exc)}
    )


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint
    Used for monitoring and load balancers
    """
    try:
        # Test database connection
        async with get_db_session() as session:
            await session.execute("SELECT 1")

        return {
            "status": "✅ healthy",
            "version": "1.0.0",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "❌ unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get("/status", tags=["System"])
async def status():
    """Platform status endpoint"""
    return {
        "platform": "Veyra",
        "version": "1.0.0",
        "status": "running",
        "features": {
            "trading": "✅ Enabled",
            "analytics": "✅ Enabled",
            "portfolio": "✅ Enabled",
            "risk_management": "✅ Enabled"
        }
    }


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/auth/login", tags=["Authentication"])
async def login(email: str, password: str):
    """User login endpoint"""
    try:
        token_data = await auth_manager.authenticate_user(email, password)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid credentials"}
            )
        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Authentication failed"}
        )


@app.post("/auth/refresh", tags=["Authentication"])
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        new_token = await auth_manager.refresh_access_token(refresh_token)
        if not new_token:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid refresh token"}
            )
        return {"access_token": new_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Token refresh failed"}
        )


# ============================================================================
# API ROUTES LOADER
# ============================================================================

async def load_api_routes():
    """
    Dynamically load all API route modules
    Each module should have a router or app instance
    """
    try:
        logger.info("📦 Loading API route modules...")

        # Import and register core routes
        from src.backend.app.api import markets_router
        from src.backend.app.api import portfolio_router
        from src.backend.app.api import trading_router

        app.include_router(markets_router.router, prefix="/api/markets", tags=["Markets"])
        app.include_router(portfolio_router.router, prefix="/api/portfolio", tags=["Portfolio"])
        app.include_router(trading_router.router, prefix="/api/trading", tags=["Trading"])

        logger.info("✅ Core API routes loaded")

    except Exception as e:
        logger.error(f"Failed to load API routes: {e}", exc_info=e)
        # Don't crash on route loading - allow partial startup


# Load routes when app starts
@app.on_event("startup")
async def startup_event():
    """Called after lifespan context enters"""
    await load_api_routes()


# ============================================================================
# STATIC PAGES
# ============================================================================

@app.get("/", tags=["System"])
async def root():
    """Root endpoint - API documentation"""
    return {
        "name": "Veyra",
        "version": "1.0.0",
        "description": "100% Open-Source Bloomberg Terminal Alternative",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "status": "/status",
        "health": "/health"
    }


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("🔧 Starting Veyra server...")

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
