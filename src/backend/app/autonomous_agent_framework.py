"""
Financial Master - Autonomous Agent Execution Framework
========================================================
Multi-agent system with guardrails, human approval gates, and kill switches.

Architecture: 8 specialized AI agents with clear responsibilities
Safety: Multi-layer approval system for financial actions
Cost: £0 (uses local Ollama) with optional paid fallback

Agents:
1. Market Data Collector    - Real-time price feeds
2. Retirement/FIRE Planner  - Long-term projections  
3. Tax Optimizer            - CGT, ISA, tax-loss harvesting
4. Risk Manager             - Portfolio risk monitoring
5. Portfolio Rebalancer     - Asset allocation
6. Withdrawal Strategist    - Retirement income
7. Sentiment Analyzer       - Market mood
8. Compliance Auditor       - Regulatory checks
"""

import os
import json
import asyncio
import sqlite3
from typing import Optional, Dict, List, Any, Callable, Literal
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import threading
import logging
from functools import wraps

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AgentFramework')


# ============================================================================
# SAFETY & GUARDRAILS
# ============================================================================

class RiskLevel(Enum):
    LOW = "low"           # Informational only, auto-approve
    MEDIUM = "medium"     # Needs human notification
    HIGH = "high"         # Needs human approval
    CRITICAL = "critical"   # Emergency stop, multiple approvals


class ActionType(Enum):
    READ = "read"               # Data reading
    ANALYZE = "analyze"         # Analysis/recommendations
    RECOMMEND = "recommend"     # Suggestions (no execution)
    EXECUTE = "execute"         # Actual trades/transfers
    KILL = "kill"               # Emergency stop


@dataclass
class GuardrailConfig:
    """Safety configuration for agent actions"""
    # Auto-approval limits
    max_daily_trades: int = 5
    max_daily_value: float = 100000  # £100k
    max_single_trade: float = 25000  # £25k
    max_cgt_exposure: float = 3000  # £3k CGT allowance buffer
    
    # Approval requirements
    require_approval_above: float = 10000  # £10k+ needs approval
    require_approval_cgt_impact: bool = True
    require_approval_tax_year_end: bool = True
    
    # Circuit breakers
    daily_loss_limit: float = 5000  # £5k max daily loss
    volatility_threshold: float = 0.05  # 5% market move
    correlation_breakdown: float = 0.8  # 80% correlation spike
    
    # Emergency controls
    global_kill_switch: bool = False
    pause_all_agents: bool = False
    allowed_hours: tuple = (8, 18)  # 8am-6pm only
    
    # Notifications
    notify_methods: List[str] = field(default_factory=lambda: ["log", "telegram"])
    notification_cooldown: int = 300  # 5 min between alerts


@dataclass
class AgentDecision:
    """A decision record from an agent"""
    decision_id: str
    agent_name: str
    timestamp: datetime
    action_type: ActionType
    risk_level: RiskLevel
    description: str
    details: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    status: Literal["pending", "approved", "rejected", "executed", "failed"] = "pending"
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    execution_result: Optional[Dict] = None


class ApprovalGate:
    """
    Human approval system for agent decisions.
    Routes decisions based on risk level and config.
    """
    
    def __init__(self, config: GuardrailConfig, db_path: str = "./data/approvals.db"):
        self.config = config
        self.db_path = db_path
        self._pending: Dict[str, AgentDecision] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize approvals database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                agent_name TEXT,
                timestamp TEXT,
                action_type TEXT,
                risk_level TEXT,
                description TEXT,
                details TEXT,
                confidence REAL,
                status TEXT,
                approved_by TEXT,
                approval_timestamp TEXT,
                execution_result TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def submit(self, decision: AgentDecision) -> Dict[str, Any]:
        """
        Submit a decision for routing/approval.
        Returns routing result with action required.
        """
        # Save to DB
        self._save_decision(decision)
        
        # Auto-approve low risk read-only actions
        if decision.risk_level == RiskLevel.LOW and decision.action_type in [ActionType.READ, ActionType.ANALYZE]:
            decision.status = "approved"
            decision.approved_by = "SYSTEM_AUTO"
            decision.approval_timestamp = datetime.now()
            self._update_decision(decision)
            return {
                "decision_id": decision.decision_id,
                "status": "auto_approved",
                "action": "proceed",
                "message": "Low risk action auto-approved"
            }
        
        # Check kill switch
        if self.config.global_kill_switch:
            decision.status = "rejected"
            self._update_decision(decision)
            return {
                "decision_id": decision.decision_id,
                "status": "rejected",
                "action": "stop",
                "message": "Global kill switch is active"
            }
        
        # Check value limits for trades
        if decision.action_type == ActionType.EXECUTE:
            value = decision.details.get("value_gbp", 0)
            if value > self.config.require_approval_above:
                decision.risk_level = RiskLevel.HIGH
        
        # Route based on risk
        with self._lock:
            self._pending[decision.decision_id] = decision
        
        if decision.risk_level == RiskLevel.MEDIUM:
            # Notify but auto-approve after delay
            self._notify(decision)
            return {
                "decision_id": decision.decision_id,
                "status": "pending_notification",
                "action": "wait_for_objection",
                "timeout_seconds": 300,  # 5 min objection window
                "message": f"Medium risk action: {decision.description}"
            }
        
        elif decision.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            # Require explicit approval
            self._notify(decision)
            return {
                "decision_id": decision.decision_id,
                "status": "pending_approval",
                "action": "require_human_approval",
                "approval_url": f"/api/approvals/{decision.decision_id}",
                "message": f"APPROVAL REQUIRED: {decision.description}"
            }
        
        return {
            "decision_id": decision.decision_id,
            "status": "submitted",
            "action": "review"
        }
    
    def approve(self, decision_id: str, approved_by: str, notes: Optional[str] = None) -> bool:
        """Human approves a pending decision"""
        with self._lock:
            if decision_id not in self._pending:
                return False
            decision = self._pending[decision_id]
        
        decision.status = "approved"
        decision.approved_by = approved_by
        decision.approval_timestamp = datetime.now()
        self._update_decision(decision)
        
        # Trigger callbacks
        self._trigger_callbacks(decision_id, "approved")
        
        logger.info(f"Decision {decision_id} approved by {approved_by}")
        return True
    
    def reject(self, decision_id: str, rejected_by: str, reason: str) -> bool:
        """Human rejects a pending decision"""
        with self._lock:
            if decision_id not in self._pending:
                return False
            decision = self._pending[decision_id]
        
        decision.status = "rejected"
        decision.approved_by = rejected_by
        decision.approval_timestamp = datetime.now()
        decision.execution_result = {"rejection_reason": reason}
        self._update_decision(decision)
        
        self._trigger_callbacks(decision_id, "rejected")
        
        logger.warning(f"Decision {decision_id} rejected by {rejected_by}: {reason}")
        return True
    
    def _save_decision(self, decision: AgentDecision):
        """Save decision to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision.decision_id,
            decision.agent_name,
            decision.timestamp.isoformat(),
            decision.action_type.value,
            decision.risk_level.value,
            decision.description,
            json.dumps(decision.details),
            decision.confidence,
            decision.status,
            decision.approved_by,
            decision.approval_timestamp.isoformat() if decision.approval_timestamp else None,
            json.dumps(decision.execution_result) if decision.execution_result else None
        ))
        conn.commit()
        conn.close()
    
    def _update_decision(self, decision: AgentDecision):
        """Update decision status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE decisions SET status = ?, approved_by = ?, approval_timestamp = ?, execution_result = ?
            WHERE decision_id = ?
        """, (
            decision.status,
            decision.approved_by,
            decision.approval_timestamp.isoformat() if decision.approval_timestamp else None,
            json.dumps(decision.execution_result) if decision.execution_result else None,
            decision.decision_id
        ))
        conn.commit()
        conn.close()
    
    def _notify(self, decision: AgentDecision):
        """Send notifications"""
        for method in self.config.notify_methods:
            if method == "log":
                logger.warning(f"AGENT ACTION PENDING: {decision.agent_name} - {decision.description} [{decision.risk_level.value}]")
            elif method == "telegram":
                # TODO: Integrate with 12_Telegram_Bot.py
                pass
            elif method == "email":
                # TODO: Send email notification
                pass
    
    def _trigger_callbacks(self, decision_id: str, event: str):
        """Trigger registered callbacks"""
        if decision_id in self._callbacks:
            for callback in self._callbacks[decision_id]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
    
    def on_decision(self, decision_id: str, callback: Callable):
        """Register callback for decision events"""
        if decision_id not in self._callbacks:
            self._callbacks[decision_id] = []
        self._callbacks[decision_id].append(callback)
    
    def get_pending(self) -> List[AgentDecision]:
        """Get all pending decisions"""
        with self._lock:
            return [d for d in self._pending.values() if d.status == "pending"]


# ============================================================================
# BASE AGENT CLASS
# ============================================================================

class BaseAgent:
    """
    Base class for all Financial Master agents.
    Provides common functionality: guardrails, approval gates, logging.
    """
    
    def __init__(
        self,
        name: str,
        approval_gate: ApprovalGate,
        llm_manager: Any = None  # From 13_LLM_Integration_Free_Tier.py
    ):
        self.name = name
        self.approval_gate = approval_gate
        self.llm = llm_manager
        self.running = False
        self.last_run: Optional[datetime] = None
        self.run_count = 0
        self.decision_history: List[AgentDecision] = []
    
    def decide(
        self,
        action_type: ActionType,
        risk_level: RiskLevel,
        description: str,
        details: Dict[str, Any],
        confidence: float = 0.8
    ) -> Dict[str, Any]:
        """
        Submit a decision to the approval gate.
        All agents must use this for any action.
        """
        decision = AgentDecision(
            decision_id=f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.run_count}",
            agent_name=self.name,
            timestamp=datetime.now(),
            action_type=action_type,
            risk_level=risk_level,
            description=description,
            details=details,
            confidence=confidence
        )
        
        result = self.approval_gate.submit(decision)
        self.decision_history.append(decision)
        
        logger.info(f"Agent {self.name} decision: {description} -> {result['status']}")
        return result
    
    async def run(self):
        """Main agent loop - override in subclasses"""
        self.running = True
        while self.running:
            try:
                await self.execute_cycle()
                self.last_run = datetime.now()
                self.run_count += 1
                await asyncio.sleep(self.get_interval_seconds())
            except Exception as e:
                logger.error(f"Agent {self.name} error: {e}")
                await asyncio.sleep(60)  # Wait 1 min on error
    
    async def execute_cycle(self):
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement execute_cycle")
    
    def get_interval_seconds(self) -> int:
        """Override to set agent run interval"""
        return 300  # 5 minutes default
    
    def stop(self):
        """Stop the agent"""
        self.running = False
        logger.info(f"Agent {self.name} stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "running": self.running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "run_count": self.run_count,
            "decisions_24h": len([d for d in self.decision_history 
                                  if d.timestamp > datetime.now() - timedelta(hours=24)]),
            "pending_decisions": len([d for d in self.decision_history 
                                      if d.status == "pending"])
        }


# ============================================================================
# SPECIALIZED AGENTS
# ============================================================================

class MarketDataCollectorAgent(BaseAgent):
    """
    Agent 1: Real-time market data collection
    Risk: LOW (read-only)
    """
    
    def __init__(self, approval_gate: ApprovalGate, llm_manager=None):
        super().__init__("MarketDataCollector", approval_gate, llm_manager)
        self.price_cache: Dict[str, Dict] = {}
    
    async def execute_cycle(self):
        """Collect latest prices"""
        # This would integrate with price feeds
        # For now, simulate data collection
        
        decision = self.decide(
            action_type=ActionType.READ,
            risk_level=RiskLevel.LOW,
            description="Collect market price data",
            details={"tickers": ["VUAG", "AGGH", "AYEM", "HMWO"]},
            confidence=1.0
        )
        
        if decision["status"] in ["auto_approved", "approved"]:
            # Execute data collection
            logger.info("Collecting market data...")
            # TODO: Integrate with price feed APIs
    
    def get_interval_seconds(self) -> int:
        return 60  # Every minute


class TaxOptimizerAgent(BaseAgent):
    """
    Agent 3: CGT and ISA optimization
    Risk: HIGH (tax decisions)
    """
    
    def __init__(self, approval_gate: ApprovalGate, llm_manager=None):
        super().__init__("TaxOptimizer", approval_gate, llm_manager)
        self.cgt_used = 0.0
        self.isa_allowance_used = 0.0
    
    async def execute_cycle(self):
        """Analyze tax optimization opportunities"""
        # Check for tax-loss harvesting opportunities
        opportunities = self._find_tax_loss_opportunities()
        
        if opportunities:
            for opp in opportunities:
                decision = self.decide(
                    action_type=ActionType.RECOMMEND,
                    risk_level=RiskLevel.HIGH,
                    description=f"Tax-loss harvest: Sell {opp['ticker']} for £{opp['loss']:,.2f} loss",
                    details=opp,
                    confidence=0.85
                )
                
                if decision["status"] == "approved":
                    # Execute the trade
                    self._execute_tax_loss_harvest(opp)
        
        # Check ISA optimization
        isa_action = self._check_isa_optimization()
        if isa_action:
            decision = self.decide(
                action_type=ActionType.RECOMMEND,
                risk_level=RiskLevel.MEDIUM,
                description=f"Bed & ISA: Move £{isa_action['amount']:,.2f} to ISA",
                details=isa_action,
                confidence=0.9
            )
    
    def _find_tax_loss_opportunities(self) -> List[Dict]:
        """Find unrealized losses for harvesting"""
        # TODO: Integrate with portfolio data
        return []
    
    def _check_isa_optimization(self) -> Optional[Dict]:
        """Check for Bed & ISA opportunities"""
        # TODO: Check current ISA allowance
        return None
    
    def _execute_tax_loss_harvest(self, opportunity: Dict):
        """Execute tax loss harvest trade"""
        logger.info(f"Executing tax loss harvest: {opportunity}")
        # TODO: Integrate with broker API
    
    def get_interval_seconds(self) -> int:
        return 3600  # Hourly


class RiskManagerAgent(BaseAgent):
    """
    Agent 4: Portfolio risk monitoring
    Risk: MEDIUM (alerts and recommendations)
    """
    
    def __init__(self, approval_gate: ApprovalGate, llm_manager=None):
        super().__init__("RiskManager", approval_gate, llm_manager)
        self.risk_metrics: Dict[str, float] = {}
    
    async def execute_cycle(self):
        """Calculate and monitor risk metrics"""
        # Calculate portfolio risk
        var_95 = self._calculate_var()
        correlation = self._check_correlations()
        concentration = self._check_concentration()
        
        # Alert on risk thresholds
        if var_95 > 0.05:  # 5% daily VaR
            self.decide(
                action_type=ActionType.ANALYZE,
                risk_level=RiskLevel.MEDIUM,
                description=f"Risk Alert: VaR(95%) = {var_95:.2%}",
                details={"var_95": var_95, "correlation": correlation},
                confidence=0.8
            )
        
        # Check for correlation breakdown
        if correlation > 0.8:
            self.decide(
                action_type=ActionType.RECOMMEND,
                risk_level=RiskLevel.HIGH,
                description="Correlation breakdown detected - diversification needed",
                details={"correlation": correlation},
                confidence=0.9
            )
    
    def _calculate_var(self) -> float:
        """Calculate Value at Risk"""
        # TODO: Implement VaR calculation
        return 0.03
    
    def _check_correlations(self) -> float:
        """Check asset correlations"""
        # TODO: Calculate correlation matrix
        return 0.5
    
    def _check_concentration(self) -> Dict[str, float]:
        """Check for concentration risk"""
        return {}
    
    def get_interval_seconds(self) -> int:
        return 300  # Every 5 minutes during market hours


class PortfolioRebalancerAgent(BaseAgent):
    """
    Agent 5: Portfolio rebalancing
    Risk: HIGH (executes trades)
    """
    
    def __init__(self, approval_gate: ApprovalGate, llm_manager=None):
        super().__init__("PortfolioRebalancer", approval_gate, llm_manager)
        self.target_allocation: Dict[str, float] = {}
        self.rebalance_threshold = 0.05  # 5% drift triggers rebalance
    
    async def execute_cycle(self):
        """Check and execute rebalancing"""
        drift = self._calculate_allocation_drift()
        
        significant_drift = {k: v for k, v in drift.items() if abs(v) > self.rebalance_threshold}
        
        if significant_drift:
            trades = self._calculate_rebalance_trades(drift)
            total_value = sum(abs(t['amount']) for t in trades)
            
            decision = self.decide(
                action_type=ActionType.EXECUTE,
                risk_level=RiskLevel.HIGH,
                description=f"Rebalance portfolio: {len(trades)} trades, £{total_value:,.2f}",
                details={
                    "drift": drift,
                    "trades": trades,
                    "total_value": total_value
                },
                confidence=0.9
            )
            
            if decision["status"] == "approved":
                self._execute_trades(trades)
    
    def _calculate_allocation_drift(self) -> Dict[str, float]:
        """Calculate current vs target allocation drift"""
        # TODO: Calculate from portfolio
        return {}
    
    def _calculate_rebalance_trades(self, drift: Dict[str, float]) -> List[Dict]:
        """Calculate trades needed for rebalancing"""
        return []
    
    def _execute_trades(self, trades: List[Dict]):
        """Execute rebalance trades"""
        logger.info(f"Executing rebalance trades: {trades}")
        # TODO: Integrate with broker API
    
    def get_interval_seconds(self) -> int:
        return 86400  # Daily


# ============================================================================
# AGENT ORCHESTRATOR
# ============================================================================

class AgentOrchestrator:
    """
    Central manager for all agents.
    Handles agent lifecycle, coordination, and emergency controls.
    """
    
    def __init__(self, guardrail_config: Optional[GuardrailConfig] = None):
        self.config = guardrail_config or GuardrailConfig()
        self.approval_gate = ApprovalGate(self.config)
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.running = False
        self.emergency_stop = False
        self._lock = asyncio.Lock()
    
    def register_agent(self, agent: BaseAgent) -> str:
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
        return agent.name
    
    async def start_all(self):
        """Start all registered agents"""
        self.running = True
        logger.info("Starting all agents...")
        
        for name, agent in self.agents.items():
            if not self.config.pause_all_agents and not self.emergency_stop:
                task = asyncio.create_task(agent.run())
                self.tasks[name] = task
                logger.info(f"Started agent: {name}")
    
    async def stop_all(self):
        """Stop all agents gracefully"""
        self.running = False
        logger.info("Stopping all agents...")
        
        for name, agent in self.agents.items():
            agent.stop()
        
        # Wait for tasks to complete
        for name, task in self.tasks.items():
            try:
                await asyncio.wait_for(task, timeout=10.0)
                logger.info(f"Agent {name} stopped gracefully")
            except asyncio.TimeoutError:
                logger.warning(f"Agent {name} did not stop in time")
                task.cancel()
    
    def kill_switch(self, triggered_by: str, reason: str):
        """Emergency stop all agents"""
        self.emergency_stop = True
        self.config.global_kill_switch = True
        
        logger.critical(f"🚨 KILL SWITCH ACTIVATED by {triggered_by}: {reason}")
        
        # Immediately stop all agents
        for name, agent in self.agents.items():
            agent.stop()
            logger.critical(f"Agent {name} emergency stopped")
        
        # Cancel all tasks
        for task in self.tasks.values():
            task.cancel()
        
        # Notify through all channels
        self._emergency_notification(triggered_by, reason)
    
    def _emergency_notification(self, triggered_by: str, reason: str):
        """Send emergency notifications"""
        message = f"🚨 FINANCIAL MASTER EMERGENCY STOP\nTriggered by: {triggered_by}\nReason: {reason}\nTime: {datetime.now().isoformat()}"
        
        # Log
        logger.critical(message)
        
        # Telegram
        # TODO: Send via 12_Telegram_Bot.py
        
        # Dashboard
        # TODO: Send WebSocket alert
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "running": self.running,
            "emergency_stop": self.emergency_stop,
            "global_kill_switch": self.config.global_kill_switch,
            "agents": {
                name: agent.get_status()
                for name, agent in self.agents.items()
            },
            "pending_approvals": len(self.approval_gate.get_pending()),
            "config": asdict(self.config)
        }
    
    def get_pending_decisions(self) -> List[AgentDecision]:
        """Get all pending decisions across all agents"""
        return self.approval_gate.get_pending()
    
    def approve_decision(self, decision_id: str, approved_by: str) -> bool:
        """Approve a pending decision"""
        return self.approval_gate.approve(decision_id, approved_by)
    
    def reject_decision(self, decision_id: str, rejected_by: str, reason: str) -> bool:
        """Reject a pending decision"""
        return self.approval_gate.reject(decision_id, rejected_by, reason)


# ============================================================================
# INITIALIZATION HELPERS
# ============================================================================

def create_default_agents(orchestrator: AgentOrchestrator, llm_manager=None) -> List[str]:
    """Create and register all 8 default agents"""
    agents = [
        MarketDataCollectorAgent(orchestrator.approval_gate, llm_manager),
        TaxOptimizerAgent(orchestrator.approval_gate, llm_manager),
        RiskManagerAgent(orchestrator.approval_gate, llm_manager),
        PortfolioRebalancerAgent(orchestrator.approval_gate, llm_manager),
        # TODO: Add remaining agents
        # RetirementPlannerAgent,
        # WithdrawalStrategistAgent,
        # SentimentAnalyzerAgent,
        # ComplianceAuditorAgent
    ]
    
    agent_ids = []
    for agent in agents:
        agent_id = orchestrator.register_agent(agent)
        agent_ids.append(agent_id)
    
    return agent_ids


# ============================================================================
# MAIN / TEST
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          FINANCIAL MASTER - AUTONOMOUS AGENT FRAMEWORK            ║
╠══════════════════════════════════════════════════════════════════╣
║  8 AI Agents with Guardrails and Human Approval Gates             ║
║  Cost: £0 (uses local Ollama models)                              ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Create configuration
    config = GuardrailConfig(
        max_daily_trades=5,
        require_approval_above=10000,
        notify_methods=["log"]
    )
    
    # Create orchestrator
    orchestrator = AgentOrchestrator(config)
    
    # Register agents
    agent_ids = create_default_agents(orchestrator)
    
    print(f"\n✓ Registered {len(agent_ids)} agents:")
    for aid in agent_ids:
        print(f"  - {aid}")
    
    # Print status
    print("\n📊 System Status:")
    print(json.dumps(orchestrator.get_status(), indent=2, default=str))
    
    print("\n" + "="*60)
    print("To start agents:")
    print("  asyncio.run(orchestrator.start_all())")
    print("\nTo emergency stop:")
    print("  orchestrator.kill_switch('user', 'manual stop')")
    print("="*60)
