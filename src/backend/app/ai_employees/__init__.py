"""
AI Employees System for Financial Master
5 Core Financial AI Agents with multi-agent collaboration
"""

from .agent_factory import AgentFactory, AgentConfig
from .multi_agent_manager import MultiAgentManager
from .financial_agents import (
    FinancialAdvisorAI,
    TradingStrategistAI,
    TaxOptimizerAI,
    ComplianceOfficerAI,
    CustomerSupportAI
)
from .api import ai_employees_router

__all__ = [
    'AgentFactory',
    'AgentConfig',
    'MultiAgentManager',
    'FinancialAdvisorAI',
    'TradingStrategistAI',
    'TaxOptimizerAI',
    'ComplianceOfficerAI',
    'CustomerSupportAI',
    'ai_employees_router'
]
