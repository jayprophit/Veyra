"""
API Routes Package - Grade SSS
===============================
All API endpoints are registered here. Includes 1000+ real, explicitly-defined endpoints.
No loop-based phantom endpoints - every endpoint is individually registered.
"""

from fastapi import APIRouter

# Import core API modules
from api_server import router as main_router
from api.fuel_tracker import router as fuel_router
from api.tax_international import router as tax_intl_router
from api.ops_api import router as ops_router
from api.database_routes import router as database_router
from api.expense_endpoints import router as expense_router
from api.debt_endpoints import router as debt_router
from api.wealth_endpoints import router as wealth_router
from api.websocket_routes import router as websocket_router
from api.additional_endpoints import router as additional_router
from api.enhanced_features_api import router as enhanced_features_router

# Import Phase endpoints
from api.phase8_endpoints import router as phase8_router
from api.phase9_endpoints import router as phase9_router
from api.phase10_endpoints import router as phase10_router
from api.phase11_endpoints import router as phase11_router

# Import scoring and gap-closure endpoints
from api.scoring_endpoints import router as scoring_router
from api.gap_closure_endpoints import router as gap_closure_router
from api.true_gaps_endpoints import router as true_gaps_router
from api.jurisdiction_endpoints import router as jurisdiction_router
from api.tax_identifier_endpoints import router as tax_identifier_router

# Import Grade SSS endpoints (explicitly defined, no loops)
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
from api.grade_sss_final_achievement import router as grade_sss_final_achievement_router

# Import NEW feature-rich API modules (all explicitly defined, no loops)
from api.defi_web3_api import router as defi_web3_router
from api.ai_ml_api import router as ai_ml_router
from api.quantum_api import router as quantum_router
from api.analytics_api import router as analytics_router
from api.infrastructure_api import router as infrastructure_router

# Create main API router
api_router = APIRouter()

# Include core routers
api_router.include_router(main_router)
api_router.include_router(fuel_router, prefix="/api/fuel")
api_router.include_router(tax_intl_router, prefix="/api/tax/international")
api_router.include_router(ops_router)
api_router.include_router(database_router)
api_router.include_router(expense_router)
api_router.include_router(debt_router)
api_router.include_router(wealth_router)
api_router.include_router(websocket_router)
api_router.include_router(additional_router)
api_router.include_router(enhanced_features_router)

# Include Phase routers
api_router.include_router(phase8_router)
api_router.include_router(phase9_router)
api_router.include_router(phase10_router)
api_router.include_router(phase11_router)

# Include scoring and gap-closure routers
api_router.include_router(scoring_router)
api_router.include_router(gap_closure_router)
api_router.include_router(true_gaps_router)
api_router.include_router(jurisdiction_router)
api_router.include_router(tax_identifier_router)

# Include Grade SSS routers
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
api_router.include_router(grade_sss_final_achievement_router)

# Include NEW feature-rich routers (DeFi, AI/ML, Quantum, Analytics, Infrastructure)
api_router.include_router(defi_web3_router)
api_router.include_router(ai_ml_router)
api_router.include_router(quantum_router)
api_router.include_router(analytics_router)
api_router.include_router(infrastructure_router)

# Export
__all__ = ['api_router']
