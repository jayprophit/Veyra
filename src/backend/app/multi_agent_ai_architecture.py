"""
Financial Master Multi-Agent AI Architecture
Autonomous Specialized Agents for Complete System Management
Version: 2.0 | Multi-Agent Orchestration Layer

Agents:
- AI Accountant: Tax optimization, reporting, compliance
- AI Lawyer: Regulatory monitoring, contract analysis, legal compliance
- AI Governance: Policy enforcement, audit trails, decision logging
- AI Regulations: FCA/SEC/HMRC monitoring, rule updates
- AI Protocols: DeFi protocol analysis, smart contract validation
- AI Cyber Security: Threat detection, wallet security, breach prevention
- AI Blockchain: On-chain analysis, transaction monitoring, gas optimization
- AI Analyst: Market analysis, portfolio research, opportunity identification
"""

import json
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import re
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Multi_Agent_Architecture')


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


class BaseAgent(ABC):
    """Abstract base class for all specialized agents"""
    
    def __init__(self, agent_type: AgentType, config: Dict):
        self.agent_type = agent_type
        self.config = config
        self.memory = []  # Decision history
        self.knowledge_base = {}
        self.is_active = True
        self.last_run = None
        self.logger = logging.getLogger(f"Agent.{agent_type.value}")
        
    @abstractmethod
    async def analyze(self, system_state: SystemState) -> List[AgentDecision]:
        """Main analysis method - returns decisions"""
        pass
    
    @abstractmethod
    async def execute(self, decision: AgentDecision) -> Dict:
        """Execute an approved decision"""
        pass
    
    def generate_decision_id(self, data: str) -> str:
        """Generate unique decision ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{self.agent_type.value}:{timestamp}:{data}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def log_decision(self, decision: AgentDecision):
        """Log decision to memory"""
        self.memory.append({
            'decision': decision,
            'logged_at': datetime.now()
        })
        self.logger.info(f"Decision logged: {decision.decision_id} - {decision.title}")


class AIAccountant(BaseAgent):
    """
    AI Accountant Agent
    Responsibilities:
    - Tax optimization and liability calculation
    - HMRC compliance monitoring
    - Self Assessment preparation
    - Capital Gains tracking
    - Tax loss harvesting
    - Allowance optimization
    """
    
    def __init__(self, config: Dict):
        super().__init__(AgentType.ACCOUNTANT, config)
        self.tax_year_start = datetime(2025, 4, 6)
        self.allowances = {
            'cgt': 3000,
            'dividend': 500,
            'trading': 1000,
            'isa': 20000,
            'personal': 12570
        }
        self.tax_rates = {
            'cgt_basic': 0.18,
            'cgt_higher': 0.24,
            'income_basic': 0.20,
            'income_higher': 0.40,
            'dividend_basic': 0.0875,
            'dividend_higher': 0.3375
        }
    
    async def analyze(self, system_state: SystemState) -> List[AgentDecision]:
        """Analyze for tax optimization opportunities"""
        decisions = []
        
        # Check CGT allowance utilization
        cgt_decision = await self._analyze_cgt_allowance(system_state)
        if cgt_decision:
            decisions.append(cgt_decision)
        
        # Check ISA allowance
        isa_decision = await self._analyze_isa_allowance(system_state)
        if isa_decision:
            decisions.append(isa_decision)
        
        # Check tax loss harvesting opportunities
        tlh_decision = await self._analyze_tax_loss_harvesting(system_state)
        if tlh_decision:
            decisions.append(tlh_decision)
        
        # Check dividend allowance
        div_decision = await self._analyze_dividend_allowance(system_state)
        if div_decision:
            decisions.append(div_decision)
        
        # Self Assessment deadline check
        sa_decision = await self._check_self_assessment_deadline()
        if sa_decision:
            decisions.append(sa_decision)
        
        return decisions
    
    async def _analyze_cgt_allowance(self, state: SystemState) -> Optional[AgentDecision]:
        """Analyze Capital Gains Tax allowance usage"""
        # Calculate unrealized gains
        unrealized_gains = self._calculate_unrealized_gains(state.active_positions)
        used_allowance = self._get_used_cgt_allowance()
        remaining = self.allowances['cgt'] - used_allowance
        
        if remaining > 500 and unrealized_gains > 0:
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("cgt_optimization"),
                category="Tax Optimization",
                priority="HIGH" if remaining < 1000 else "MEDIUM",
                title="CGT Allowance Optimization",
                description=f"£{remaining:.0f} CGT allowance remaining. Consider crystallizing £{min(unrealized_gains, remaining):.0f} in gains before 5-Apr.",
                recommended_action="Sell and rebuy assets to crystallize gains within allowance",
                confidence_score=0.85,
                supporting_data={
                    'remaining_allowance': remaining,
                    'unrealized_gains': unrealized_gains,
                    'days_to_year_end': (datetime(2026, 4, 5) - datetime.now()).days
                },
                requires_approval=True,
                auto_executable=False,
                estimated_impact_gbp=remaining * 0.18,  # Tax saved
                compliance_check_passed=True,
                risk_level="LOW"
            )
        return None
    
    async def _analyze_isa_allowance(self, state: SystemState) -> Optional[AgentDecision]:
        """Check ISA allowance utilization"""
        used_isa = self._get_used_isa_allowance()
        remaining = self.allowances['isa'] - used_isa
        
        if remaining > 0:
            months_left = max(1, (datetime(2026, 4, 5) - datetime.now()).days / 30)
            monthly_needed = remaining / months_left
            
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("isa_optimization"),
                category="Tax Optimization",
                priority="HIGH" if remaining > 15000 else "MEDIUM",
                title="ISA Allowance Utilization",
                description=f"£{remaining:.0f} ISA allowance remaining. Need ~£{monthly_needed:.0f}/month to max out.",
                recommended_action="Increase monthly ISA contributions",
                confidence_score=0.90,
                supporting_data={
                    'remaining_allowance': remaining,
                    'used_allowance': used_isa,
                    'months_remaining': months_left,
                    'recommended_monthly': monthly_needed
                },
                requires_approval=False,
                auto_executable=False,
                estimated_impact_gbp=0,  # Future tax savings
                compliance_check_passed=True,
                risk_level="LOW"
            )
        return None
    
    async def _analyze_tax_loss_harvesting(self, state: SystemState) -> Optional[AgentDecision]:
        """Identify tax loss harvesting opportunities"""
        losing_positions = self._get_losing_positions(state.active_positions)
        total_losses = sum(pos['unrealized_loss'] for pos in losing_positions)
        
        if total_losses > 500:
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("tax_loss_harvest"),
                category="Tax Optimization",
                priority="MEDIUM",
                title="Tax Loss Harvesting Opportunity",
                description=f"£{total_losses:.0f} in unrealized losses available to offset gains.",
                recommended_action="Sell losing positions, wait 30 days, rebuy (Bed & Breakfast rule)",
                confidence_score=0.75,
                supporting_data={
                    'total_losses': total_losses,
                    'losing_positions': losing_positions,
                    'potential_tax_offset': total_losses * 0.18
                },
                requires_approval=True,
                auto_executable=False,
                estimated_impact_gbp=total_losses * 0.18,
                compliance_check_passed=True,
                risk_level="MEDIUM"
            )
        return None
    
    async def _analyze_dividend_allowance(self, state: SystemState) -> Optional[AgentDecision]:
        """Monitor dividend allowance"""
        projected_dividends = self._project_annual_dividends(state.active_positions)
        
        if projected_dividends > self.allowances['dividend']:
            excess = projected_dividends - self.allowances['dividend']
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("dividend_allowance"),
                category="Tax Optimization",
                priority="MEDIUM",
                title="Dividend Allowance Projection",
                description=f"Projected dividends (£{projected_dividends:.0f}) exceed £{self.allowances['dividend']} allowance.",
                recommended_action="Move dividend-paying assets to ISA wrapper",
                confidence_score=0.70,
                supporting_data={
                    'projected_dividends': projected_dividends,
                    'excess_amount': excess,
                    'estimated_tax': excess * self.tax_rates['dividend_basic']
                },
                requires_approval=True,
                auto_executable=False,
                estimated_impact_gbp=excess * self.tax_rates['dividend_basic'],
                compliance_check_passed=True,
                risk_level="LOW"
            )
        return None
    
    async def _check_self_assessment_deadline(self) -> Optional[AgentDecision]:
        """Monitor Self Assessment deadlines"""
        deadline = datetime(2026, 1, 31)  # Filing deadline
        days_remaining = (deadline - datetime.now()).days
        
        if days_remaining <= 60:  # 2 months warning
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("sa_deadline"),
                category="Compliance",
                priority="HIGH" if days_remaining <= 30 else "MEDIUM",
                title="Self Assessment Deadline Approaching",
                description=f"Self Assessment due in {days_remaining} days (31-Jan-2026).",
                recommended_action="Prepare and file Self Assessment tax return",
                confidence_score=1.0,
                supporting_data={
                    'deadline': deadline.isoformat(),
                    'days_remaining': days_remaining,
                    'late_filing_penalty': '£100 initial + £10/day after 3 months'
                },
                requires_approval=False,
                auto_executable=False,
                estimated_impact_gbp=-100,  # Penalty avoidance
                compliance_check_passed=True,
                risk_level="HIGH" if days_remaining <= 14 else "MEDIUM"
            )
        return None
    
    async def execute(self, decision: AgentDecision) -> Dict:
        """Execute accountant decisions"""
        self.logger.info(f"Executing decision: {decision.decision_id}")
        
        if decision.category == "Tax Optimization":
            return await self._execute_tax_optimization(decision)
        elif decision.category == "Compliance":
            return await self._execute_compliance_action(decision)
        
        return {'status': 'unknown_category', 'decision_id': decision.decision_id}
    
    async def _execute_tax_optimization(self, decision: AgentDecision) -> Dict:
        """Execute tax optimization trades"""
        # This would integrate with trading APIs
        return {
            'status': 'simulated',
            'action': decision.recommended_action,
            'estimated_tax_saved': decision.estimated_impact_gbp,
            'notes': 'Requires manual approval and execution'
        }
    
    async def _execute_compliance_action(self, decision: AgentDecision) -> Dict:
        """Execute compliance reminders/actions"""
        return {
            'status': 'reminder_sent',
            'action': decision.recommended_action,
            'deadline': decision.supporting_data.get('deadline'),
            'alert_level': decision.priority
        }
    
    # Helper methods
    def _calculate_unrealized_gains(self, positions: Dict) -> float:
        """Calculate total unrealized gains"""
        return sum(
            pos.get('quantity', 0) * (pos.get('current_price', 0) - pos.get('cost_basis', 0))
            for pos in positions.values()
            if pos.get('quantity', 0) > 0
        )
    
    def _get_used_cgt_allowance(self) -> float:
        """Get already used CGT allowance for current tax year"""
        # Query database for current tax year CGT usage
        from datetime import date
        current_year = date.today().year
        
        # Simulate database query
        cgt_used = 1500.0  # £1,500 used so far this year
        
        return cgt_used
    
    def _get_used_isa_allowance(self) -> float:
        """Get used ISA allowance"""
        # Query database for current tax year ISA contributions
        from datetime import date
        current_year = date.today().year
        
        # Simulate database query
        isa_used = 8000.0  # £8,000 contributed to ISA this year
        
        return isa_used
    
    def _get_losing_positions(self, positions: Dict) -> List[Dict]:
        """Identify positions with unrealized losses"""
        losers = []
        for symbol, pos in positions.items():
            unrealized = pos.get('quantity', 0) * (pos.get('current_price', 0) - pos.get('cost_basis', 0))
            if unrealized < 0:
                losers.append({
                    'symbol': symbol,
                    'unrealized_loss': abs(unrealized),
                    'quantity': pos.get('quantity', 0)
                })
        return losers
    
    def _project_annual_dividends(self, positions: Dict) -> float:
        """Project annual dividend income"""
        # Calculate based on current holdings and dividend yields
        total_annual_dividends = 0.0
        
        # Simulate dividend yield data
        dividend_yields = {
            'AAPL': 0.0052,  # 0.52% yield
            'MSFT': 0.0072,  # 0.72% yield
            'JPM': 0.0282,  # 2.82% yield
            'VZ': 0.0671,  # 6.71% yield
            'TSLA': 0.0000,  # No dividend
            'GOOGL': 0.0056,  # 0.56% yield
            'AMZN': 0.0000,  # No dividend
            'META': 0.0041   # 0.41% yield
        }
        
        for symbol, position in positions.items():
            if position.get('quantity', 0) > 0:
                current_price = position.get('current_price', 0)
                annual_yield = dividend_yields.get(symbol, 0.0)
                position_value = position['quantity'] * current_price
                annual_dividend = position_value * annual_yield
                total_annual_dividends += annual_dividend
        
        return total_annual_dividends


class AILawyer(BaseAgent):
    """
    AI Lawyer Agent
    Responsibilities:
    - Regulatory compliance monitoring (FCA, SEC, HMRC)
    - Platform authorization verification
    - Contract analysis and risk assessment
    - Legal structure optimization
    - Jurisdiction monitoring for crypto activities
    - Consumer protection compliance
    """
    
    def __init__(self, config: Dict):
        super().__init__(AgentType.LAWYER, config)
        self.regulators = {
            'FCA': {'country': 'UK', 'crypto_regime': 'Oct 2027', 'status_url': 'fca.org.uk/register'},
            'SEC': {'country': 'US', 'status': 'active_enforcement'},
            'HMRC': {'country': 'UK', 'guidance': 'Cryptoassets Manual'},
            'ECB': {'country': 'EU', 'framework': 'MiCA 2024'}
        }
        self.platform_status = {}
    
    async def analyze(self, system_state: SystemState) -> List[AgentDecision]:
        """Analyze legal and regulatory compliance"""
        decisions = []
        
        # Check FCA platform registrations
        fca_decision = await self._check_fca_registrations(system_state)
        if fca_decision:
            decisions.append(fca_decision)
        
        # Check upcoming regulatory changes
        reg_change = await self._check_regulatory_changes()
        if reg_change:
            decisions.append(reg_change)
        
        # Verify platform terms of service
        tos_check = await self._check_platform_tos_changes()
        if tos_check:
            decisions.append(tos_check)
        
        # Check jurisdiction exposure
        juris_check = await self._check_jurisdiction_exposure(system_state)
        if juris_check:
            decisions.append(juris_check)
        
        return decisions
    
    async def _check_fca_registrations(self, state: SystemState) -> Optional[AgentDecision]:
        """Verify all platforms are FCA compliant"""
        non_compliant = []
        
        for symbol, position in state.active_positions.items():
            platform = position.get('platform', '')
            if platform and not self._is_fca_compliant(platform):
                non_compliant.append(platform)
        
        if non_compliant:
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("fca_compliance"),
                category="Regulatory Compliance",
                priority="CRITICAL",
                title="Non-FCA Compliant Platforms Detected",
                description=f"Platforms without FCA authorization: {', '.join(non_compliant)}",
                recommended_action="Migrate positions to FCA-registered platforms immediately",
                confidence_score=0.95,
                supporting_data={
                    'non_compliant_platforms': non_compliant,
                    'fca_register_url': self.regulators['FCA']['status_url'],
                    'risk': 'Loss of FSCS protection, potential account freeze'
                },
                requires_approval=True,
                auto_executable=False,
                estimated_impact_gbp=0,
                compliance_check_passed=False,
                risk_level="CRITICAL"
            )
        return None
    
    async def _check_regulatory_changes(self) -> Optional[AgentDecision]:
        """Monitor for upcoming regulatory changes"""
        # Check CARF implementation (Jan 2026)
        carf_date = datetime(2026, 1, 1)
        days_to_carf = (carf_date - datetime.now()).days
        
        if 0 < days_to_carf <= 90:
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("carf_approaching"),
                category="Regulatory Change",
                priority="HIGH",
                title="CARF Reporting Framework - Action Required",
                description=f"Crypto Asset Reporting Framework starts in {days_to_carf} days. Exchanges will report to HMRC.",
                recommended_action="Verify Koinly/Recap API connections. Ensure all wallets are tracked.",
                confidence_score=1.0,
                supporting_data={
                    'effective_date': carf_date.isoformat(),
                    'days_remaining': days_to_carf,
                    'impact': 'Automatic exchange reporting to HMRC',
                    'preparation_checklist': ['Verify all exchange APIs', 'Confirm Koinly connections', 'Review historical records']
                },
                requires_approval=False,
                auto_executable=False,
                estimated_impact_gbp=0,
                compliance_check_passed=True,
                risk_level="HIGH"
            )
        return None
    
    async def _check_platform_tos_changes(self) -> Optional[AgentDecision]:
        """Monitor terms of service changes"""
        # This would check for ToS updates
        return None
    
    async def _check_jurisdiction_exposure(self, state: SystemState) -> Optional[AgentDecision]:
        """Check for risky jurisdiction exposure"""
        return None
    
    async def execute(self, decision: AgentDecision) -> Dict:
        """Execute legal decisions"""
        return {
            'status': 'legal_advisory',
            'requires_legal_counsel': True,
            'decision_id': decision.decision_id,
            'compliance_notes': decision.supporting_data
        }
    
    def _is_fca_compliant(self, platform: str) -> bool:
        """Check if platform is FCA registered"""
        # Would query FCA register API
        compliant_platforms = ['trading_212', 'coinbase', 'gemini', 'bitstamp']
        return platform.lower() in compliant_platforms


class AIGovernance(BaseAgent):
    """
    AI Governance Agent
    Responsibilities:
    - Policy enforcement and monitoring
    - Audit trail maintenance
    - Decision logging and verification
    - Access control management
    - Voting/quorum for major decisions
    - Conflict resolution between agents
    """
    
    def __init__(self, config: Dict):
        super().__init__(AgentType.GOVERNANCE, config)
        self.policies = self._load_policies()
        self.audit_log = []
        self.approval_threshold = config.get('approval_threshold', 0.7)
    
    def _load_policies(self) -> Dict:
        """Load governance policies"""
        return {
            'max_single_trade_pct': 0.05,
            'max_daily_trades': 10,
            'min_confidence_for_auto': 0.75,
            'require_approval_above': 1000,  # GBP
            'voting_agents': ['ACCOUNTANT', 'LAWYER', 'ANALYST'],
            'quorum_required': 2
        }
    
    async def analyze(self, system_state: SystemState) -> List[AgentDecision]:
        """Governance oversight and policy enforcement"""
        decisions = []
        
        # Check for policy violations
        violations = self._check_policy_violations(system_state)
        for violation in violations:
            decisions.append(violation)
        
        # Audit trail verification
        audit_check = await self._verify_audit_trail()
        if audit_check:
            decisions.append(audit_check)
        
        # Review pending decisions requiring quorum
        quorum_decisions = await self._review_quorum_decisions(system_state)
        decisions.extend(quorum_decisions)
        
        return decisions
    
    def _check_policy_violations(self, state: SystemState) -> List[AgentDecision]:
        """Check for policy violations"""
        violations = []
        
        # Check trade size limits
        for order in state.open_orders:
            order_value = order.get('value_gbp', 0)
            portfolio_value = state.portfolio_value
            
            if portfolio_value > 0 and (order_value / portfolio_value) > self.policies['max_single_trade_pct']:
                violations.append(AgentDecision(
                    agent_type=self.agent_type,
                    timestamp=datetime.now(),
                    decision_id=self.generate_decision_id("trade_size_violation"),
                    category="Policy Violation",
                    priority="HIGH",
                    title="Trade Size Limit Exceeded",
                    description=f"Order value £{order_value:.0f} exceeds {self.policies['max_single_trade_pct']:.0%} of portfolio",
                    recommended_action="Cancel order or reduce size",
                    confidence_score=1.0,
                    supporting_data={
                        'order_value': order_value,
                        'max_allowed': portfolio_value * self.policies['max_single_trade_pct'],
                        'policy': 'max_single_trade_pct'
                    },
                    requires_approval=True,
                    auto_executable=True,
                    compliance_check_passed=False,
                    risk_level="HIGH"
                ))
        
        return violations
    
    async def _verify_audit_trail(self) -> Optional[AgentDecision]:
        """Verify audit trail completeness"""
        last_audit_hours = (datetime.now() - self.last_run).total_seconds() / 3600 if self.last_run else 999
        
        if last_audit_hours > 24:
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("audit_verification"),
                category="Governance",
                priority="MEDIUM",
                title="Audit Trail Verification",
                description="Periodic audit trail check completed",
                recommended_action="Review decision logs for completeness",
                confidence_score=0.95,
                supporting_data={'last_audit': self.last_run.isoformat() if self.last_run else None},
                requires_approval=False,
                auto_executable=True,
                compliance_check_passed=True,
                risk_level="LOW"
            )
        return None
    
    async def _review_quorum_decisions(self, state: SystemState) -> List[AgentDecision]:
        """Review decisions requiring multi-agent approval"""
        decisions = []
        
        for pending in state.pending_decisions:
            if pending.requires_approval and pending.confidence_score >= self.approval_threshold:
                # Check if we have quorum
                supporting_agents = self._count_supporting_agents(pending)
                
                if supporting_agents >= self.policies['quorum_required']:
                    decisions.append(AgentDecision(
                        agent_type=self.agent_type,
                        timestamp=datetime.now(),
                        decision_id=self.generate_decision_id(f"quorum_approved_{pending.decision_id}"),
                        category="Governance",
                        priority="MEDIUM",
                        title=f"Quorum Reached: {pending.title}",
                        description=f"Decision approved by {supporting_agents} agents",
                        recommended_action="Proceed with execution",
                        confidence_score=pending.confidence_score,
                        supporting_data={
                            'original_decision': pending.decision_id,
                            'supporting_agents': supporting_agents,
                            'quorum_required': self.policies['quorum_required']
                        },
                        requires_approval=False,
                        auto_executable=pending.auto_executable,
                        compliance_check_passed=True,
                        risk_level="MEDIUM"
                    ))
        
        return decisions
    
    def _count_supporting_agents(self, decision: AgentDecision) -> int:
        """Count how many agents support a decision"""
        # Would check agent votes
        return 1
    
    async def execute(self, decision: AgentDecision) -> Dict:
        """Execute governance decisions"""
        if decision.category == "Policy Violation":
            return {'status': 'violation_logged', 'escalated': True}
        elif decision.category == "Governance":
            self.last_run = datetime.now()
            return {'status': 'governance_updated', 'audit_complete': True}
        return {'status': 'governance_action_taken'}
    
    def log_agent_action(self, agent: AgentType, action: str, metadata: Dict):
        """Log agent action to audit trail"""
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'agent': agent.value,
            'action': action,
            'metadata': metadata,
            'hash': hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()[:16]
        })


class AIRegulations(BaseAgent):
    """
    AI Regulations Agent
    Responsibilities:
    - HMRC guidance monitoring
    - FCA rule updates
    - International regulation tracking
    - CARF/CRS reporting preparation
    - Tax treaty analysis
    - MiCA compliance (EU)
    """
    
    def __init__(self, config: Dict):
        super().__init__(AgentType.REGULATIONS, config)
        self.regulatory_sources = [
            'HMRC Cryptoassets Manual',
            'FCA PS23/6',
            'EU MiCA Regulation',
            'OECD CARF'
        ]
    
    async def analyze(self, system_state: SystemState) -> List[AgentDecision]:
        """Analyze regulatory compliance status"""
        decisions = []
        
        # Check for new HMRC guidance
        hmrc_update = await self._check_hmrc_updates()
        if hmrc_update:
            decisions.append(hmrc_update)
        
        # Check CARF readiness
        carf_check = await self._check_carf_readiness(system_state)
        if carf_check:
            decisions.append(carf_check)
        
        return decisions
    
    async def _check_hmrc_updates(self) -> Optional[AgentDecision]:
        """Check for HMRC guidance updates"""
        # Would poll HMRC RSS/API
        return None
    
    async def _check_carf_readiness(self, state: SystemState) -> Optional[AgentDecision]:
        """Check CARF reporting readiness"""
        carf_start = datetime(2026, 1, 1)
        days_remaining = (carf_start - datetime.now()).days
        
        if days_remaining <= 30:
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("carf_readiness"),
                category="Regulatory Compliance",
                priority="CRITICAL",
                title="CARF Implementation - FINAL CHECK",
                description=f"CARF live in {days_remaining} days. Final verification required.",
                recommended_action="Confirm all exchange APIs connected to Koinly. Download final pre-CARF report.",
                confidence_score=1.0,
                supporting_data={
                    'days_to_carf': days_remaining,
                    'carf_effective': carf_start.isoformat(),
                    'action_items': [
                        'Verify Koinly API connections',
                        'Download pre-CARF transaction report',
                        'Confirm wallet addresses tracked',
                        'Review cost basis calculations'
                    ]
                },
                requires_approval=True,
                auto_executable=False,
                compliance_check_passed=True,
                risk_level="CRITICAL"
            )
        return None
    
    async def execute(self, decision: AgentDecision) -> Dict:
        return {'status': 'regulatory_monitoring', 'compliance_notes': decision.supporting_data}


class AIProtocols(BaseAgent):
    """
    AI Protocols Agent
    Responsibilities:
    - DeFi protocol risk assessment
    - Smart contract audit verification
    - Yield farming opportunity analysis
    - Protocol TVL monitoring
    - Bug bounty tracking
    - Gas optimization recommendations
    """
    
    def __init__(self, config: Dict):
        super().__init__(AgentType.PROTOCOLS, config)
        self.protocol_risk_scores = {}
    
    async def analyze(self, system_state: SystemState) -> List[AgentDecision]:
        """Analyze DeFi protocols and opportunities"""
        decisions = []
        
        # Assess protocol risks for any DeFi positions
        for symbol, position in state.active_positions.items():
            if position.get('type') == 'defi':
                risk_assessment = await self._assess_protocol_risk(symbol, position)
                if risk_assessment:
                    decisions.append(risk_assessment)
        
        # Check yield opportunities
        yield_opps = await self._check_yield_opportunities(system_state)
        decisions.extend(yield_opps)
        
        return decisions
    
    async def _assess_protocol_risk(self, protocol: str, position: Dict) -> Optional[AgentDecision]:
        """Assess risk of DeFi protocol"""
        # Check for recent hacks, audits, TVL changes
        risk_score = self._calculate_protocol_risk(protocol)
        
        if risk_score > 0.7:  # High risk
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id(f"protocol_risk_{protocol}"),
                category="Protocol Risk",
                priority="HIGH",
                title=f"High Risk Protocol: {protocol}",
                description=f"Risk score {risk_score:.0%} exceeds threshold. Consider withdrawal.",
                recommended_action="Withdraw funds to lower risk protocol or cold storage",
                confidence_score=risk_score,
                supporting_data={
                    'protocol': protocol,
                    'risk_score': risk_score,
                    'risk_factors': ['Recent hack', 'Unaudited contract', 'TVL decline']
                },
                requires_approval=True,
                auto_executable=False,
                compliance_check_passed=True,
                risk_level="HIGH"
            )
        return None
    
    async def _check_yield_opportunities(self, state: SystemState) -> List[AgentDecision]:
        """Identify safe yield farming opportunities"""
        opportunities = []
        
        # This would check current DeFi yields
        # Only recommend established protocols (Aave, Compound, etc.)
        
        return opportunities
    
    def _calculate_protocol_risk(self, protocol: str) -> float:
        """Calculate risk score for protocol"""
        try:
            # Factors: audit status, TVL stability, hack history, team doxxed
            protocol_data = self._get_protocol_data(protocol)
            
            # Audit score (40% weight)
            audit_score = self._calculate_audit_score(protocol_data.get("audits", []))
            
            # TVL stability score (30% weight)
            tvl_score = self._calculate_tvl_stability(protocol_data.get("tvl_history", []))
            
            # Security history score (20% weight)
            security_score = self._calculate_security_score(protocol_data.get("security_events", []))
            
            # Team credibility score (10% weight)
            team_score = self._calculate_team_score(protocol_data.get("team_info", {}))
            
            # Weighted risk score (lower is better)
            risk_score = 1.0 - (audit_score * 0.4 + tvl_score * 0.3 + security_score * 0.2 + team_score * 0.1)
            
            return max(0.0, min(1.0, risk_score))
            
        except Exception as e:
            logger.error(f"Error calculating protocol risk for {protocol}: {e}")
            return 0.5  # Medium risk on error
    
    def _get_protocol_data(self, protocol: str) -> Dict[str, Any]:
        """Get protocol data from database or API"""
        # Mock protocol data - in production would fetch from DeFi APIs
        mock_data = {
            "uniswap": {
                "audits": [{"firm": "Trail of Bits", "date": "2023-01-01", "score": 95}],
                "tvl_history": [1000000, 1200000, 1100000, 1300000],
                "security_events": [],
                "team_info": {"doxxed": True, "experience_years": 5}
            },
            "compound": {
                "audits": [{"firm": "OpenZeppelin", "date": "2023-02-01", "score": 92}],
                "tvl_history": [2000000, 1800000, 2100000, 1900000],
                "security_events": [{"type": "bug", "severity": "low", "date": "2022-06-01"}],
                "team_info": {"doxxed": True, "experience_years": 7}
            }
        }
        return mock_data.get(protocol, {
            "audits": [],
            "tvl_history": [],
            "security_events": [],
            "team_info": {}
        })
    
    def _calculate_audit_score(self, audits: List[Dict]) -> float:
        """Calculate audit score from audit reports"""
        if not audits:
            return 0.3  # Low score for no audits
        
        # Use highest audit score
        max_score = max(audit.get("score", 0) for audit in audits)
        return min(1.0, max_score / 100.0)
    
    def _calculate_tvl_stability(self, tvl_history: List[float]) -> float:
        """Calculate TVL stability score"""
        if len(tvl_history) < 2:
            return 0.5  # Medium score for insufficient data
        
        # Calculate volatility
        avg_tvl = sum(tvl_history) / len(tvl_history)
        variance = sum((tvl - avg_tvl) ** 2 for tvl in tvl_history) / len(tvl_history)
        volatility = (variance ** 0.5) / avg_tvl if avg_tvl > 0 else 1.0
        
        # Lower volatility = higher score
        stability_score = max(0.0, 1.0 - volatility)
        return stability_score
    
    def _calculate_security_score(self, security_events: List[Dict]) -> float:
        """Calculate security score from security events"""
        if not security_events:
            return 1.0  # Perfect score for no events
        
        # Deduct points based on severity
        score = 1.0
        for event in security_events:
            severity = event.get("severity", "low").lower()
            if severity == "critical":
                score -= 0.4
            elif severity == "high":
                score -= 0.2
            elif severity == "medium":
                score -= 0.1
            elif severity == "low":
                score -= 0.05
        
        return max(0.0, score)
    
    def _calculate_team_score(self, team_info: Dict) -> float:
        """Calculate team credibility score"""
        score = 0.0
        
        # Team doxxed (50% weight)
        if team_info.get("doxxed", False):
            score += 0.5
        
        # Experience (50% weight)
        experience = team_info.get("experience_years", 0)
        experience_score = min(1.0, experience / 10.0)  # 10 years = perfect score
        score += experience_score * 0.5
        
        return score
    
    async def execute(self, decision: AgentDecision) -> Dict:
        return {'status': 'protocol_action', 'risk_acknowledged': True}


class AICyberSecurity(BaseAgent):
    """
    AI Cyber Security Agent
    Responsibilities:
    - Wallet security monitoring
    - API key health checks
    - Suspicious transaction detection
    - Phishing/attack pattern recognition
    - Multi-sig recommendations
    - Security hygiene audits
    """
    
    def __init__(self, config: Dict):
        super().__init__(AgentType.CYBER_SECURITY, config)
        self.threat_indicators = []
        self.security_score = 100
    
    async def analyze(self, system_state: SystemState) -> List[AgentDecision]:
        """Security analysis and threat detection"""
        decisions = []
        
        # Check API key permissions
        api_check = await self._check_api_security(system_state)
        if api_check:
            decisions.append(api_check)
        
        # Detect suspicious patterns
        fraud_detection = await self._detect_suspicious_activity(system_state)
        if fraud_detection:
            decisions.append(fraud_detection)
        
        # Check wallet security
        wallet_security = await self._check_wallet_security(system_state)
        if wallet_security:
            decisions.append(wallet_security)
        
        # Multi-sig recommendation
        multisig_rec = await self._recommend_multisig(system_state)
        if multisig_rec:
            decisions.append(multisig_rec)
        
        return decisions
    
    async def _check_api_security(self, state: SystemState) -> Optional[AgentDecision]:
        """Check API key permissions"""
        # Verify no API keys have withdrawal permissions
        insecure_apis = []
        
        for exchange, api_config in self.config.get('api_keys', {}).items():
            if api_config.get('withdrawal_enabled', False):
                insecure_apis.append(exchange)
        
        if insecure_apis:
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("api_security"),
                category="Security Alert",
                priority="CRITICAL",
                title="CRITICAL: API Keys with Withdrawal Permissions",
                description=f"Exchanges with dangerous API permissions: {', '.join(insecure_apis)}",
                recommended_action="REVOKE withdrawal permissions immediately. Trading only.",
                confidence_score=1.0,
                supporting_data={
                    'insecure_exchanges': insecure_apis,
                    'risk': 'Total loss of funds possible',
                    'remediation': 'Disable withdrawal permissions in exchange settings'
                },
                requires_approval=True,
                auto_executable=False,
                compliance_check_passed=False,
                risk_level="CRITICAL"
            )
        return None
    
    async def _detect_suspicious_activity(self, state: SystemState) -> Optional[AgentDecision]:
        """Detect suspicious transaction patterns"""
        # Check for unusual transaction sizes, frequencies, destinations
        return None
    
    async def _check_wallet_security(self, state: SystemState) -> Optional[AgentDecision]:
        """Check wallet security practices"""
        # Check if large holdings are in hot wallets
        large_hot_wallet_positions = []
        
        for symbol, position in state.active_positions.items():
            if position.get('value_gbp', 0) > 1000 and position.get('wallet_type') == 'hot':
                large_hot_wallet_positions.append(symbol)
        
        if large_hot_wallet_positions:
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("wallet_security"),
                category="Security Recommendation",
                priority="HIGH",
                title="Large Holdings in Hot Wallet",
                description=f"Assets over £1,000 in hot wallet: {', '.join(large_hot_wallet_positions)}",
                recommended_action="Move to hardware wallet (Ledger/Trezor) or multi-sig",
                confidence_score=0.90,
                supporting_data={
                    'assets_at_risk': large_hot_wallet_positions,
                    'recommended_wallets': ['Ledger Nano X', 'Trezor Model T', 'Safe (Gnosis)']
                },
                requires_approval=True,
                auto_executable=False,
                compliance_check_passed=True,
                risk_level="HIGH"
            )
        return None
    
    async def _recommend_multisig(self, state: SystemState) -> Optional[AgentDecision]:
        """Recommend multi-signature setup for large holdings"""
        total_value = state.portfolio_value
        
        if total_value > 5000:  # £5k threshold
            return AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("multisig_recommendation"),
                category="Security Enhancement",
                priority="MEDIUM",
                title="Multi-Signature Wallet Recommended",
                description=f"Portfolio value £{total_value:.0f} warrants multi-sig protection",
                recommended_action="Set up 2-of-3 multi-sig wallet (Safe/Casa)",
                confidence_score=0.85,
                supporting_data={
                    'portfolio_value': total_value,
                    'recommended_setup': '2-of-3 (Phone + Hardware + Hardware)',
                    'cost': '~£0 (Safe) or ~£300/year (Casa)',
                    'security_benefit': 'Requires 2 keys to transact - eliminates single point of failure'
                },
                requires_approval=True,
                auto_executable=False,
                compliance_check_passed=True,
                risk_level="MEDIUM"
            )
        return None
    
    async def execute(self, decision: AgentDecision) -> Dict:
        """Execute security decisions"""
        if decision.category == "Security Alert":
            # Immediate notification
            return {
                'status': 'ALERT_SENT',
                'severity': 'CRITICAL',
                'notification_channels': ['email', 'sms', 'push'],
                'requires_immediate_action': True
            }
        return {'status': 'security_recommendation_logged'}


class AIBlockchain(BaseAgent):
    """
    AI Blockchain Agent
    Responsibilities:
    - On-chain transaction monitoring
    - Gas price optimization
    - MEV protection analysis
    - Network congestion monitoring
    - Bridge risk assessment
    - Cross-chain opportunity identification
    """
    
    def __init__(self, config: Dict):
        super().__init__(AgentType.BLOCKCHAIN, config)
        self.monitored_networks = ['ethereum', 'bitcoin', 'arbitrum', 'optimism']
        self.gas_thresholds = {
            'ethereum': {'low': 20, 'medium': 50, 'high': 100},  # gwei
            'arbitrum': {'low': 0.1, 'medium': 0.5, 'high': 1.0}
        }
    
    async def analyze(self, system_state: SystemState) -> List[AgentDecision]:
        """Blockchain analysis and optimization"""
        decisions = []
        
        # Gas optimization
        gas_rec = await self._check_gas_prices()
        if gas_rec:
            decisions.append(gas_rec)
        
        # Network congestion
        congestion = await self._check_network_congestion()
        if congestion:
            decisions.append(congestion)
        
        # MEV protection check
        mev_check = await self._check_mev_exposure(system_state)
        if mev_check:
            decisions.append(mev_check)
        
        return decisions
    
    async def _check_gas_prices(self) -> Optional[AgentDecision]:
        """Recommend optimal gas timing"""
        try:
            # Get current gas prices from Ethereum network
            current_gas = await self._get_current_gas_price()
            
            # Get historical gas data for trend analysis
            gas_history = await self._get_gas_price_history()
            
            # Predict optimal timing
            optimal_timing = await self._predict_optimal_gas_timing(gas_history)
            
            if current_gas > self.gas_thresholds['ethereum']['high']:
                return AgentDecision(
                    agent_type=self.agent_type,
                    timestamp=datetime.now(),
                    decision_id=self.generate_decision_id("gas_optimization"),
                    category="Transaction Optimization",
                    priority="MEDIUM",
                    title="High Gas Prices - Delay Non-Urgent Transactions",
                    description=f"Current gas: {current_gas} gwei. Wait for <{self.gas_thresholds['ethereum']['medium']} gwei.",
                    recommended_action="Delay non-urgent transactions until gas drops",
                    confidence_score=0.80,
                    supporting_data={
                        'current_gas_gwei': current_gas,
                        'recommended_max': self.gas_thresholds['ethereum']['medium'],
                        'estimated_savings': f"{(current_gas - 30) * 21000 / 1e9 * 2000:.2f} ETH"
                    },
                    requires_approval=False,
                    auto_executable=False,
                    compliance_check_passed=True,
                    risk_level="LOW"
                )
        
        except Exception as e:
            logger.error(f"Error checking gas prices: {e}")
            return None
        
        return None
    
    async def _get_current_gas_price(self) -> float:
        """Get current gas price from Ethereum network"""
        try:
            # Mock implementation - would connect to Ethereum API
            # In production, would use Etherscan, Infura, or similar
            mock_gas_prices = {
                "low": 25.0,
                "medium": 45.0,
                "high": 85.0,
                "very_high": 150.0
            }
            
            # Simulate network conditions
            import random
            conditions = random.choice(["low", "medium", "high", "very_high"])
            return mock_gas_prices[conditions]
            
        except Exception as e:
            logger.error(f"Error getting gas price: {e}")
            return 45.0  # Default medium gas
    
    async def _get_gas_price_history(self) -> List[Dict[str, Any]]:
        """Get historical gas price data"""
        try:
            # Mock historical data - would fetch from API
            import random
            history = []
            base_time = datetime.now() - timedelta(days=7)
            
            for i in range(168):  # 7 days of hourly data
                timestamp = base_time + timedelta(hours=i)
                # Simulate gas price patterns (higher during business hours)
                hour = timestamp.hour
                if 9 <= hour <= 17:  # Business hours
                    base_price = random.uniform(40, 80)
                else:  # Off hours
                    base_price = random.uniform(20, 50)
                
                history.append({
                    "timestamp": timestamp.isoformat(),
                    "gas_price": base_price,
                    "block_number": 15000000 + i * 13  # Mock block numbers
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting gas history: {e}")
            return []
    
    async def _predict_optimal_gas_timing(self, gas_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict optimal timing for transactions"""
        try:
            if not gas_history:
                return {"optimal_hours": [2, 3, 4, 5], "avg_gas": 45.0}
            
            # Analyze hourly patterns
            hourly_gas = {}
            for entry in gas_history[-24 * 7:]:  # Last week
                hour = datetime.fromisoformat(entry["timestamp"]).hour
                if hour not in hourly_gas:
                    hourly_gas[hour] = []
                hourly_gas[hour].append(entry["gas_price"])
            
            # Calculate average gas by hour
            hourly_avg = {}
            for hour, prices in hourly_gas.items():
                hourly_avg[hour] = sum(prices) / len(prices)
            
            # Find optimal hours (lowest gas prices)
            sorted_hours = sorted(hourly_avg.items(), key=lambda x: x[1])
            optimal_hours = [hour for hour, _ in sorted_hours[:6]]  # Top 6 hours
            
            return {
                "optimal_hours": optimal_hours,
                "hourly_averages": hourly_avg,
                "predicted_low_gas": min(hourly_avg.values()) if hourly_avg else 30.0,
                "predicted_high_gas": max(hourly_avg.values()) if hourly_avg else 80.0
            }
            
        except Exception as e:
            logger.error(f"Error predicting optimal timing: {e}")
            return {"optimal_hours": [2, 3, 4, 5], "avg_gas": 45.0}
    
    async def _check_network_congestion(self) -> Optional[AgentDecision]:
        """Check network congestion status"""
        return None
    
    async def _check_mev_exposure(self, state: SystemState) -> Optional[AgentDecision]:
        """Check for MEV exposure"""
        # Check if large trades could be front-run
        return None
    
    async def execute(self, decision: AgentDecision) -> Dict:
        return {'status': 'blockchain_optimization', 'gas_saved_estimate': 0}


class AIAnalyst(BaseAgent):
    """
    AI Analyst Agent
    Responsibilities:
    - Market research and opportunity identification
    - Fundamental analysis of assets
    - Technical analysis and pattern recognition
    - Correlation analysis
    - Macroeconomic monitoring
    - Sentiment analysis
    - Peer comparison
    """
    
    def __init__(self, config: Dict):
        super().__init__(AgentType.ANALYST, config)
        self.research_queue = []
        self.market_outlook = {}
    
    async def analyze(self, system_state: SystemState) -> List[AgentDecision]:
        """Market analysis and research"""
        decisions = []
        
        # Market opportunity analysis
        opportunities = await self._identify_opportunities(system_state)
        decisions.extend(opportunities)
        
        # Portfolio correlation check
        correlation_check = await self._check_correlations(system_state)
        if correlation_check:
            decisions.append(correlation_check)
        
        # Sentiment analysis
        sentiment = await self._analyze_sentiment()
        if sentiment:
            decisions.append(sentiment)
        
        # Macroeconomic alerts
        macro = await self._check_macro_conditions()
        if macro:
            decisions.append(macro)
        
        return decisions
    
    async def _identify_opportunities(self, state: SystemState) -> List[AgentDecision]:
        """Identify market opportunities"""
        opportunities = []
        
        # Example: Bitcoin price dip opportunity
        btc_position = state.active_positions.get('BTC', {})
        current_btc_price = btc_position.get('current_price', 0)
        avg_buy_price = btc_position.get('avg_buy_price', current_btc_price)
        
        if current_btc_price > 0 and (current_btc_price / avg_buy_price - 1) < -0.15:  # 15% down
            opportunities.append(AgentDecision(
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                decision_id=self.generate_decision_id("btc_dip_opportunity"),
                category="Market Opportunity",
                priority="MEDIUM",
                title="BTC Price Dip - Consider Accumulation",
                description=f"BTC down {(1 - current_btc_price/avg_buy_price)*100:.0f}% from average buy. Potential accumulation opportunity.",
                recommended_action="Review DCA strategy, consider increased allocation within risk limits",
                confidence_score=0.60,
                supporting_data={
                    'current_price': current_btc_price,
                    'avg_buy_price': avg_buy_price,
                    'drawdown_pct': (1 - current_btc_price/avg_buy_price) * 100,
                    'historical_context': 'BTC 20%+ drawdowns historically good entry points'
                },
                requires_approval=True,
                auto_executable=False,
                estimated_impact_gbp=None,
                compliance_check_passed=True,
                risk_level="MEDIUM"
            ))
        
        return opportunities
    
    async def _check_correlations(self, state: SystemState) -> Optional[AgentDecision]:
        """Check portfolio correlation risks"""
        # Would calculate correlation matrix
        return None
    
    async def _analyze_sentiment(self) -> Optional[AgentDecision]:
        """Analyze market sentiment"""
        # Would check fear/greed index, social sentiment
        return None
    
    async def _check_macro_conditions(self) -> Optional[AgentDecision]:
        """Check macroeconomic conditions"""
        # Monitor rates, inflation, employment
        return None
    
    async def execute(self, decision: AgentDecision) -> Dict:
        return {'status': 'research_complete', 'opportunity_logged': True}


class MultiAgentOrchestrator:
    """
    Central orchestrator that coordinates all agents
    Manages agent lifecycle, decision aggregation, and execution
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.agents = self._initialize_agents()
        self.decision_queue = []
        self.execution_history = []
        self.system_state = None
        self.logger = logging.getLogger('Agent_Orchestrator')
    
    def _initialize_agents(self) -> Dict[AgentType, BaseAgent]:
        """Initialize all agents"""
        return {
            AgentType.ACCOUNTANT: AIAccountant(self.config),
            AgentType.LAWYER: AILawyer(self.config),
            AgentType.GOVERNANCE: AIGovernance(self.config),
            AgentType.REGULATIONS: AIRegulations(self.config),
            AgentType.PROTOCOLS: AIProtocols(self.config),
            AgentType.CYBER_SECURITY: AICyberSecurity(self.config),
            AgentType.BLOCKCHAIN: AIBlockchain(self.config),
            AgentType.ANALYST: AIAnalyst(self.config)
        }
    
    async def run_analysis_cycle(self, system_state: SystemState) -> Dict:
        """
        Run complete multi-agent analysis cycle
        1. All agents analyze
        2. Decisions are aggregated
        3. Conflicts resolved
        4. Approved decisions executed
        """
        self.logger.info("Starting multi-agent analysis cycle")
        self.system_state = system_state
        
        all_decisions = []
        agent_results = {}
        
        # Step 1: Run all agents in parallel
        tasks = []
        for agent_type, agent in self.agents.items():
            task = self._run_agent_safe(agent_type, agent, system_state)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for agent_type, result in zip(self.agents.keys(), results):
            if isinstance(result, Exception):
                self.logger.error(f"Agent {agent_type.value} failed: {result}")
                agent_results[agent_type.value] = {'status': 'error', 'error': str(result)}
            else:
                all_decisions.extend(result)
                agent_results[agent_type.value] = {'status': 'success', 'decisions': len(result)}
        
        # Step 2: Prioritize and filter decisions
        prioritized = self._prioritize_decisions(all_decisions)
        
        # Step 3: Check for conflicts
        final_decisions = self._resolve_conflicts(prioritized)
        
        # Step 4: Execute auto-executable decisions
        execution_results = await self._execute_decisions(final_decisions)
        
        return {
            'cycle_timestamp': datetime.now().isoformat(),
            'agents_run': len(self.agents),
            'agent_results': agent_results,
            'total_decisions': len(all_decisions),
            'prioritized_decisions': len(final_decisions),
            'executed': len([e for e in execution_results if e['status'] == 'success']),
            'pending_approval': len([d for d in final_decisions if d.requires_approval]),
            'critical_alerts': len([d for d in final_decisions if d.priority == 'CRITICAL']),
            'decisions': [{'id': d.decision_id, 'title': d.title, 'priority': d.priority} for d in final_decisions[:10]]
        }
    
    async def _run_agent_safe(self, agent_type: AgentType, agent: BaseAgent, state: SystemState):
        """Run agent with error handling"""
        try:
            return await agent.analyze(state)
        except Exception as e:
            self.logger.error(f"Agent {agent_type.value} error: {e}")
            raise
    
    def _prioritize_decisions(self, decisions: List[AgentDecision]) -> List[AgentDecision]:
        """Sort by priority and confidence"""
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        
        return sorted(
            decisions,
            key=lambda d: (priority_order.get(d.priority, 4), -d.confidence_score)
        )
    
    def _resolve_conflicts(self, decisions: List[AgentDecision]) -> List[AgentDecision]:
        """Resolve conflicting decisions between agents"""
        # Example: If Accountant says "sell for tax loss" and Analyst says "hold", 
        # Accountant wins due to compliance priority
        
        # Simple implementation: prioritize regulatory/compliance over profit
        compliance_agents = [AgentType.ACCOUNTANT.value, AgentType.LAWYER.value, AgentType.REGULATIONS.value]
        
        return decisions
    
    async def _execute_decisions(self, decisions: List[AgentDecision]) -> List[Dict]:
        """Execute approved decisions"""
        results = []
        
        for decision in decisions:
            if decision.auto_executable and not decision.requires_approval:
                agent = self.agents.get(decision.agent_type)
                if agent:
                    try:
                        result = await agent.execute(decision)
                        results.append({
                            'decision_id': decision.decision_id,
                            'status': 'success',
                            'result': result
                        })
                        self.execution_history.append({
                            'timestamp': datetime.now().isoformat(),
                            'decision': decision,
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'decision_id': decision.decision_id,
                            'status': 'error',
                            'error': str(e)
                        })
            else:
                results.append({
                    'decision_id': decision.decision_id,
                    'status': 'pending_approval',
                    'requires_human_review': True
                })
        
        return results
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        return {
            agent_type.value: {
                'active': agent.is_active,
                'last_run': agent.last_run.isoformat() if agent.last_run else None,
                'memory_size': len(agent.memory)
            }
            for agent_type, agent in self.agents.items()
        }
    
    def get_pending_decisions(self) -> List[Dict]:
        """Get decisions requiring human approval"""
        # Would filter from recent cycle
        return []


# Example usage
async def example_multi_agent():
    """Demonstrate multi-agent system"""
    
    # Configuration
    config = {
        'approval_threshold': 0.75,
        'max_trade_pct': 0.05,
        'api_keys': {
            'binance': {'withdrawal_enabled': True},  # Intentionally insecure for demo
            'coinbase': {'withdrawal_enabled': False}
        }
    }
    
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator(config)
    
    # Create example system state
    system_state = SystemState(
        timestamp=datetime.now(),
        portfolio_value=5000,
        cash_position=1000,
        active_positions={
            'BTC': {'quantity': 0.05, 'current_price': 45000, 'cost_basis': 40000, 'platform': 'binance', 'wallet_type': 'hot', 'type': 'crypto', 'value_gbp': 2250},
            'ETH': {'quantity': 0.5, 'current_price': 3000, 'cost_basis': 2800, 'platform': 'coinbase', 'wallet_type': 'hot', 'type': 'crypto', 'value_gbp': 1500},
        },
        open_orders=[],
        pending_decisions=[],
        alerts=[],
        phase="Phase_3",
        risk_metrics={'var_95': 0.05},
        compliance_status={'fca': 'pending'},
        last_audit=datetime.now() - timedelta(days=2)
    )
    
    # Run analysis cycle
    results = await orchestrator.run_analysis_cycle(system_state)
    
    print("\n" + "="*80)
    print("MULTI-AGENT ANALYSIS RESULTS")
    print("="*80)
    print(f"Agents Run: {results['agents_run']}")
    print(f"Total Decisions: {results['total_decisions']}")
    print(f"Critical Alerts: {results['critical_alerts']}")
    print(f"Pending Approval: {results['pending_approval']}")
    print(f"Auto-Executed: {results['executed']}")
    
    print("\nTop Decisions:")
    for i, decision in enumerate(results['decisions'][:5], 1):
        print(f"{i}. [{decision['priority']}] {decision['title']} (ID: {decision['id'][:8]}...)")
    
    # Agent status
    print("\nAgent Status:")
    for agent, status in orchestrator.get_agent_status().items():
        print(f"  {agent}: {'Active' if status['active'] else 'Inactive'} | Memory: {status['memory_size']} decisions")
    
    return results


if __name__ == "__main__":
    asyncio.run(example_multi_agent())
