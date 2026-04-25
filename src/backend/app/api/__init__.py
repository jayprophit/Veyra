"""
API Routes Package
=================
All API endpoints are registered here.
"""

from fastapi import APIRouter

# Import all API modules
from api_server import router as main_router
from api.fuel_tracker import router as fuel_router
from api.tax_international import router as tax_intl_router
from api.ops_api import router as ops_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(main_router)
api_router.include_router(fuel_router, prefix="/api/fuel")
api_router.include_router(tax_intl_router, prefix="/api/tax/international")
api_router.include_router(ops_router)

# Export
__all__ = ['api_router']
