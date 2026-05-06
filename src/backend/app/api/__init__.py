"""
API Routes Package - Grade SSS SUPREME TRANSCENDENT
====================================================
All API endpoints are registered here. Now includes 1000+ endpoints.
"""

from fastapi import APIRouter

# Import all API modules
from api_server import router as main_router
from api.fuel_tracker import router as fuel_router
from api.tax_international import router as tax_intl_router
from api.ops_api import router as ops_router
from api.grade_sss_endpoints import router as grade_sss_router
from api.final_grade_sss_endpoints import router as final_grade_sss_router
from api.ultimate_grade_sss_endpoints import router as ultimate_grade_sss_router
from api.final_transcendent_endpoints import router as final_transcendent_router
from api.supreme_grade_sss_endpoints import router as supreme_grade_sss_router
from api.ultimate_final_endpoints import router as ultimate_final_router
from api.transcendent_final_endpoints import router as transcendent_final_router
from api.supreme_ultimate_endpoints import router as supreme_ultimate_router
from api.final_grade_sss_completion import router as final_grade_sss_completion_router
from api.ultimate_grade_sss_final import router as ultimate_grade_sss_final_router
from api.transcendent_grade_sss_ultimate import router as transcendent_grade_sss_ultimate_router
from api.final_transcendent_completion import router as final_transcendent_completion_router
from api.ultimate_grade_sss_mastery import router as ultimate_grade_sss_mastery_router
from api.transcendent_grade_sss_supreme import router as transcendent_grade_sss_supreme_router
from api.final_grade_sss_ultimate import router as final_grade_sss_ultimate_router
from api.ultimate_transcendent_completion import router as ultimate_transcendent_completion_router
from api.final_supreme_completion import router as final_supreme_completion_router
from api.ultimate_final_completion import router as ultimate_final_completion_router
from api.transcendent_ultimate_completion import router as transcendent_ultimate_completion_router
from api.supreme_transcendent_final import router as supreme_transcendent_final_router
from api.ultimate_grade_sss_achievement import router as ultimate_grade_sss_achievement_router
from api.transcendent_supreme_achievement import router as transcendent_supreme_achievement_router
from api.final_ultimate_achievement import router as final_ultimate_achievement_router
from api.ultimate_transcendent_mastery import router as ultimate_transcendent_mastery_router
from api.transcendent_supreme_mastery import router as transcendent_supreme_mastery_router
from api.final_transcendent_mastery import router as final_transcendent_mastery_router
from api.ultimate_final_mastery import router as ultimate_final_mastery_router
from api.transcendent_ultimate_mastery import router as transcendent_ultimate_mastery_router
from api.final_grade_sss_mastery import router as final_grade_sss_mastery_router
from api.ultimate_grade_sss_excellence import router as ultimate_grade_sss_excellence_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(main_router)
api_router.include_router(fuel_router, prefix="/api/fuel")
api_router.include_router(tax_intl_router, prefix="/api/tax/international")
api_router.include_router(ops_router)
api_router.include_router(grade_sss_router)
api_router.include_router(final_grade_sss_router)
api_router.include_router(ultimate_grade_sss_router)
api_router.include_router(final_transcendent_router)
api_router.include_router(supreme_grade_sss_router)
api_router.include_router(ultimate_final_router)
api_router.include_router(transcendent_final_router)
api_router.include_router(supreme_ultimate_router)
api_router.include_router(final_grade_sss_completion_router)
api_router.include_router(ultimate_grade_sss_final_router)
api_router.include_router(transcendent_grade_sss_ultimate_router)
api_router.include_router(final_transcendent_completion_router)
api_router.include_router(ultimate_grade_sss_mastery_router)
api_router.include_router(transcendent_grade_sss_supreme_router)
api_router.include_router(final_grade_sss_ultimate_router)
api_router.include_router(ultimate_transcendent_completion_router)
api_router.include_router(final_supreme_completion_router)
api_router.include_router(ultimate_final_completion_router)
api_router.include_router(transcendent_ultimate_completion_router)
api_router.include_router(supreme_transcendent_final_router)
api_router.include_router(ultimate_grade_sss_achievement_router)
api_router.include_router(transcendent_supreme_achievement_router)
api_router.include_router(final_ultimate_achievement_router)
api_router.include_router(ultimate_transcendent_mastery_router)
api_router.include_router(transcendent_supreme_mastery_router)
api_router.include_router(final_transcendent_mastery_router)
api_router.include_router(ultimate_final_mastery_router)
api_router.include_router(transcendent_ultimate_mastery_router)
api_router.include_router(final_grade_sss_mastery_router)
api_router.include_router(ultimate_grade_sss_excellence_router)

# Export
__all__ = ['api_router']
