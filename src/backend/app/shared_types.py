
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class AgentType(Enum):
    ACCOUNTANT = "ai_accountant"
    LAWYER = "ai_lawyer"
    GOVERNANCE = "ai_governance"
    REGULATIONS = "ai_regulations"
    PROTOCOLS = "ai_protocols"
    CYBER_SECURITY = "ai_cyber_security"
    BLOCKCHAIN = "ai_blockchain"
    ANALYST = "ai_analyst"

@dataclass
class AgentDecision:
    """Standardized decision format from any agent"""
    agent_type: AgentType
    timestamp: datetime
    decision_id: str
    category: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    description: str
    recommended_action: str
    confidence_score: float  # 0.0 - 1.0
    supporting_data: Dict
    requires_approval: bool
    auto_executable: bool
    estimated_impact_gbp: Optional[float] = None
    compliance_check_passed: bool = True
    risk_level: str = "MEDIUM"

@dataclass
class SystemState:
    """Global system state shared across all agents"""
    timestamp: datetime
    portfolio_value: float
    cash_position: float
    active_positions: Dict[str, Dict]
    open_orders: List[Dict]
    pending_decisions: List[AgentDecision]
    alerts: List[Dict]
    phase: str
    risk_metrics: Dict
    compliance_status: Dict
    last_audit: datetime
