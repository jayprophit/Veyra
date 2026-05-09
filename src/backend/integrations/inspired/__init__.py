"""
FactSet-Inspired Integration Modules
Free open-source alternatives to FactSet recipes using free data sources
"""

from .wealth_management import get_wealth_management_module
from .portfolio_analytics import get_portfolio_analytics_module
from .visualization_integrations import get_visualization_integrations_module
from .realtime_streaming import get_realtime_streaming_module
from .crm_integration import get_crm_integration_module
from .risk_compliance import get_risk_compliance_module
from .automated_reporting import get_automated_reporting_module
from .ai_ml_integration import get_ai_ml_integration_module

__all__ = [
    'get_wealth_management_module',
    'get_portfolio_analytics_module',
    'get_visualization_integrations_module',
    'get_realtime_streaming_module',
    'get_crm_integration_module',
    'get_risk_compliance_module',
    'get_automated_reporting_module',
    'get_ai_ml_integration_module'
]
