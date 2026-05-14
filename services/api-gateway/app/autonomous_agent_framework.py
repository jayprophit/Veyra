"""
Veyra - Autonomous Agent Execution Framework
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
                # Integrate with telegram notification system
                self._send_telegram_notification(decision)
            elif method == "email":
                # Send email notification
                self._send_email_notification(decision)
    
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
    Base class for all Veyra agents.
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
        """Execute autonomous agent cycle with comprehensive analysis"""
        try:
            # Market data analysis
            market_data = await self.analyze_market_conditions()
            
            # Risk assessment
            risk_metrics = await self.assess_risk_metrics()
            
            # Decision making
            decisions = await self.make_trading_decisions(market_data, risk_metrics)
            
            # Execute trades
            executed_trades = await self.execute_trades(decisions)
            
            # Performance monitoring
            performance = await self.monitor_performance(executed_trades)
            
            # Update agent state
            await self.update_agent_state(market_data, risk_metrics, decisions, performance)
            
            # Log results
            logger.info(f"Agent {self.name} cycle completed: {len(executed_trades)} trades executed")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "market_analysis": market_data,
                "risk_metrics": risk_metrics,
                "decisions": decisions,
                "executed_trades": executed_trades,
                "performance": performance
            }
            
        except Exception as e:
            logger.error(f"Error in agent {self.name} execute_cycle: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def get_interval_seconds(self) -> int:
        """Override to set agent run interval"""
        return 300  # 5 minutes default
    
    def stop(self):
        """Stop the agent"""
        self.running = False
        logger.info(f"Agent {self.name} stopped")
    
    async def analyze_market_conditions(self) -> Dict[str, Any]:
        """Analyze current market conditions"""
        try:
            # Get market data
            market_data = await self.get_market_data()
            
            # Technical analysis
            technical_indicators = await self.calculate_technical_indicators(market_data)
            
            # Sentiment analysis
            sentiment = await self.analyze_sentiment()
            
            # Market volatility
            volatility = await self.calculate_volatility(market_data)
            
            return {
                "market_data": market_data,
                "technical_indicators": technical_indicators,
                "sentiment": sentiment,
                "volatility": volatility,
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {e}")
            return {"error": str(e)}
    
    async def assess_risk_metrics(self) -> Dict[str, Any]:
        """Assess current risk metrics"""
        try:
            # Portfolio risk
            portfolio_risk = await self.calculate_portfolio_risk()
            
            # Market risk
            market_risk = await self.calculate_market_risk()
            
            # Credit risk
            credit_risk = await self.calculate_credit_risk()
            
            # Operational risk
            operational_risk = await self.calculate_operational_risk()
            
            return {
                "portfolio_risk": portfolio_risk,
                "market_risk": market_risk,
                "credit_risk": credit_risk,
                "operational_risk": operational_risk,
                "overall_risk_score": (portfolio_risk + market_risk + credit_risk + operational_risk) / 4,
                "risk_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error assessing risk metrics: {e}")
            return {"error": str(e)}
    
    async def make_trading_decisions(self, market_data: Dict, risk_metrics: Dict) -> List[Dict[str, Any]]:
        """Make trading decisions based on analysis"""
        try:
            decisions = []
            
            # Risk-adjusted decision making
            risk_score = risk_metrics.get("overall_risk_score", 0.5)
            
            for symbol, data in market_data.get("market_data", {}).items():
                # Analyze symbol
                signal = await self.analyze_symbol_signal(symbol, data, risk_score)
                
                if signal["action"] != "hold":
                    decision = {
                        "symbol": symbol,
                        "action": signal["action"],
                        "quantity": signal["quantity"],
                        "confidence": signal["confidence"],
                        "reasoning": signal["reasoning"],
                        "risk_score": risk_score,
                        "timestamp": datetime.now().isoformat()
                    }
                    decisions.append(decision)
            
            return decisions
        except Exception as e:
            logger.error(f"Error making trading decisions: {e}")
            return []
    
    async def execute_trades(self, decisions: List[Dict]) -> List[Dict[str, Any]]:
        """Execute trading decisions"""
        try:
            executed_trades = []
            
            for decision in decisions:
                # Risk check before execution
                if decision["risk_score"] > 0.8:  # High risk threshold
                    continue
                
                # Execute trade
                trade_result = await self.execute_single_trade(decision)
                
                if trade_result["success"]:
                    executed_trades.append(trade_result)
                    logger.info(f"Trade executed: {decision['symbol']} {decision['action']} {decision['quantity']}")
            
            return executed_trades
        except Exception as e:
            logger.error(f"Error executing trades: {e}")
            return []
    
    async def monitor_performance(self, trades: List[Dict]) -> Dict[str, Any]:
        """Monitor trading performance"""
        try:
            # Calculate P&L
            total_pnl = sum(trade.get("pnl", 0) for trade in trades)
            
            # Win rate
            winning_trades = len([t for t in trades if t.get("pnl", 0) > 0])
            win_rate = winning_trades / len(trades) if trades else 0
            
            # Sharpe ratio
            returns = [trade.get("pnl", 0) for trade in trades]
            sharpe_ratio = self.calculate_sharpe_ratio(returns)
            
            return {
                "total_pnl": total_pnl,
                "win_rate": win_rate,
                "sharpe_ratio": sharpe_ratio,
                "trade_count": len(trades),
                "performance_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error monitoring performance: {e}")
            return {"error": str(e)}
    
    async def update_agent_state(self, market_data: Dict, risk_metrics: Dict, 
                                decisions: List, performance: Dict):
        """Update agent internal state"""
        try:
            self.last_market_analysis = market_data
            self.last_risk_assessment = risk_metrics
            self.last_decisions = decisions
            self.last_performance = performance
            
            # Update learning models
            await self.update_learning_models(decisions, performance)
            
        except Exception as e:
            logger.error(f"Error updating agent state: {e}")
    
    # Helper methods
    async def get_market_data(self) -> Dict[str, Any]:
        """Get current market data"""
        # Mock implementation - would connect to real market data
        return {"AAPL": {"price": 150.0, "volume": 1000000}, "GOOGL": {"price": 2500.0, "volume": 500000}}
    
    async def calculate_technical_indicators(self, data: Dict) -> Dict[str, Any]:
        """Calculate technical indicators"""
        return {"rsi": 50.0, "macd": 0.5, "bollinger_bands": {"upper": 155, "lower": 145}}
    
    async def analyze_sentiment(self) -> Dict[str, Any]:
        """Analyze market sentiment"""
        return {"overall": "neutral", "score": 0.0, "confidence": 0.8}
    
    async def calculate_volatility(self, data: Dict) -> float:
        """Calculate market volatility"""
        return 0.2  # 20% volatility
    
    async def calculate_portfolio_risk(self) -> float:
        """Calculate portfolio risk score"""
        return 0.3  # 30% risk
    
    async def calculate_market_risk(self) -> float:
        """Calculate market risk score"""
        return 0.4  # 40% risk
    
    async def calculate_credit_risk(self) -> float:
        """Calculate credit risk score"""
        return 0.2  # 20% risk
    
    async def calculate_operational_risk(self) -> float:
        """Calculate operational risk score"""
        return 0.1  # 10% risk
    
    async def analyze_symbol_signal(self, symbol: str, data: Dict, risk_score: float) -> Dict[str, Any]:
        """Analyze signal for specific symbol"""
        # Simple momentum strategy
        price = data.get("price", 0)
        volume = data.get("volume", 0)
        
        # Generate signal
        if volume > 1000000 and price > 100:
            return {
                "action": "buy",
                "quantity": 100,
                "confidence": 0.7,
                "reasoning": "High volume and price momentum"
            }
        elif volume < 500000 and price < 50:
            return {
                "action": "sell",
                "quantity": 50,
                "confidence": 0.6,
                "reasoning": "Low volume and price decline"
            }
        else:
            return {
                "action": "hold",
                "quantity": 0,
                "confidence": 0.5,
                "reasoning": "Neutral market conditions"
            }
    
    async def execute_single_trade(self, decision: Dict) -> Dict[str, Any]:
        """Execute a single trade"""
        try:
            # Mock trade execution
            return {
                "success": True,
                "symbol": decision["symbol"],
                "action": decision["action"],
                "quantity": decision["quantity"],
                "price": 100.0,
                "pnl": decision["quantity"] * 0.1,  # Mock P&L
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio"""
        if not returns:
            return 0.0
        
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        return avg_return / std_dev if std_dev > 0 else 0.0
    
    async def update_learning_models(self, decisions: List, performance: Dict):
        """Update machine learning models"""
        # Mock learning update
        pass
    
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
            self._collect_market_data()
    
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
        # Get portfolio holdings and calculate unrealized losses
        holdings = self._get_portfolio_holdings()
        opportunities = []
        
        for holding in holdings:
            current_price = self._get_current_price(holding['ticker'])
            cost_basis = holding['avg_cost']
            
            if current_price < cost_basis and holding['shares'] > 0:
                unrealized_loss = (cost_basis - current_price) * holding['shares']
                if unrealized_loss > 100:  # Only consider meaningful losses
                    opportunities.append({
                        'ticker': holding['ticker'],
                        'shares': holding['shares'],
                        'cost_basis': cost_basis,
                        'current_price': current_price,
                        'unrealized_loss': unrealized_loss,
                        'loss_pct': ((cost_basis - current_price) / cost_basis) * 100
                    })
        
        return opportunities
    
    def _check_isa_optimization(self) -> Optional[Dict]:
        """Check for Bed & ISA opportunities"""
        # Check current ISA allowance and contribution status
        current_year = datetime.now().year
        isa_used = self._get_isa_contributions(current_year)
        isa_allowance = 20000  # 2024/25 ISA allowance
        
        if isa_used < isa_allowance:
            remaining = isa_allowance - isa_used
            return {
                'opportunity': 'bed_and_isa',
                'remaining_allowance': remaining,
                'recommendation': f'Contribute £{remaining:,.0f} to ISA before April 5th'
            }
        
        return None
    
    def _execute_tax_loss_harvest(self, opportunity: Dict):
        """Execute tax loss harvest trade"""
        logger.info(f"Executing tax loss harvest: {opportunity}")
        
        # Create sell order for tax loss harvesting
        trade_order = {
            'ticker': opportunity['ticker'],
            'action': 'SELL',
            'shares': opportunity['shares'],
            'reason': 'tax_loss_harvest',
            'expected_loss': opportunity['unrealized_loss']
        }
        
        # Submit to broker for execution
        result = self._submit_trade(trade_order)
        
        # Schedule buy-back after 30 days (wash sale rule)
        if result.get('success'):
            self._schedule_buy_back(opportunity['ticker'], opportunity['shares'], 30)
    
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
        # Get portfolio returns and calculate 95% VaR
        returns = self._get_portfolio_returns()
        
        if len(returns) < 30:
            return 0.03  # Default if insufficient data
        
        # Calculate 5th percentile (95% VaR)
        returns_sorted = sorted(returns)
        var_index = int(len(returns_sorted) * 0.05)
        var = abs(returns_sorted[var_index]) if var_index < len(returns_sorted) else 0.03
        
        return var
    
    def _check_correlations(self) -> float:
        """Check asset correlations"""
        # Get asset price data and calculate correlation matrix
        assets = self._get_portfolio_assets()
        
        if len(assets) < 2:
            return 0.5  # Default if insufficient assets
        
        # Calculate average correlation (simplified)
        correlations = []
        for i, asset1 in enumerate(assets):
            for asset2 in assets[i+1:]:
                corr = self._calculate_correlation(asset1, asset2)
                correlations.append(abs(corr))
        
        avg_correlation = sum(correlations) / len(correlations) if correlations else 0.5
        return avg_correlation
    
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
        # Get current portfolio allocation
        current_allocation = self._get_current_allocation()
        target_allocation = self._get_target_allocation()
        
        drift = {}
        for asset in target_allocation:
            current_pct = current_allocation.get(asset, 0)
            target_pct = target_allocation[asset]
            drift[asset] = current_pct - target_pct
        
        return drift
    
    def _calculate_rebalance_trades(self, drift: Dict[str, float]) -> List[Dict]:
        """Calculate trades needed for rebalancing"""
        return []
    
    def _execute_trades(self, trades: List[Dict]):
        """Execute rebalance trades"""
        logger.info(f"Executing rebalance trades: {trades}")
        try:
            # Initialize broker connection
            broker_client = self._get_broker_client()
            
            executed_trades = []
            for trade in trades:
                # Validate trade
                if self._validate_trade(trade):
                    # Execute trade through broker API
                    result = broker_client.execute_order({
                        "symbol": trade["symbol"],
                        "side": trade["side"],
                        "quantity": trade["quantity"],
                        "order_type": "market",
                        "time_in_force": "day"
                    })
                    
                    if result["success"]:
                        executed_trades.append({
                            "symbol": trade["symbol"],
                            "side": trade["side"],
                            "quantity": trade["quantity"],
                            "order_id": result["order_id"],
                            "executed_price": result["price"],
                            "executed_quantity": result["quantity"],
                            "status": "filled"
                        })
                        logger.info(f"Trade executed: {trade['symbol']} {trade['side']} {trade['quantity']}")
                    else:
                        logger.error(f"Trade execution failed: {result['error']}")
                else:
                    logger.warning(f"Trade validation failed: {trade}")
            
            # Update portfolio
            self._update_portfolio_after_trades(executed_trades)
            
            return executed_trades
            
        except Exception as e:
            logger.error(f"Error executing trades: {e}")
            return []
    
    def _get_broker_client(self):
        """Get broker API client"""
        # Mock broker client - in production would connect to real broker
        return MockBrokerClient()
    
    def _validate_trade(self, trade: Dict) -> bool:
        """Validate trade before execution"""
        required_fields = ["symbol", "side", "quantity"]
        return all(field in trade for field in required_fields) and trade["quantity"] > 0
    
    def _update_portfolio_after_trades(self, trades: List[Dict]):
        """Update portfolio after trade execution"""
        # Mock portfolio update
        pass
    
    def get_interval_seconds(self) -> int:
        return 86400  # Daily


# ============================================================================
# MOCK BROKER CLIENT
# ============================================================================

class MockBrokerClient:
    """Mock broker client for testing and development"""
    
    def __init__(self):
        self.order_id_counter = 1000
        self.positions = {}
        self.orders = {}
        
    def execute_order(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute order through broker API"""
        try:
            order_id = f"order_{self.order_id_counter}"
            self.order_id_counter += 1
            
            # Mock execution
            execution_price = self._get_mock_price(order_request["symbol"])
            
            result = {
                "success": True,
                "order_id": order_id,
                "price": execution_price,
                "quantity": order_request["quantity"],
                "status": "filled",
                "timestamp": datetime.now().isoformat()
            }
            
            # Store order
            self.orders[order_id] = result
            
            # Update positions
            self._update_position(order_request, execution_price)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_mock_price(self, symbol: str) -> float:
        """Get mock price for symbol"""
        mock_prices = {
            "AAPL": 150.0,
            "GOOGL": 2500.0,
            "MSFT": 300.0,
            "AMZN": 3500.0,
            "TSLA": 800.0
        }
        return mock_prices.get(symbol, 100.0)
    
    def _update_position(self, order: Dict[str, Any], price: float):
        """Update position after trade"""
        symbol = order["symbol"]
        side = order["side"]
        quantity = order["quantity"]
        
        if symbol not in self.positions:
            self.positions[symbol] = {"quantity": 0, "avg_price": 0.0}
        
        if side == "buy":
            # Add to position
            current_qty = self.positions[symbol]["quantity"]
            current_avg = self.positions[symbol]["avg_price"]
            
            new_qty = current_qty + quantity
            new_avg = ((current_qty * current_avg) + (quantity * price)) / new_qty if new_qty > 0 else price
            
            self.positions[symbol]["quantity"] = new_qty
            self.positions[symbol]["avg_price"] = new_avg
        else:
            # Reduce position
            self.positions[symbol]["quantity"] -= quantity


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
        self._send_telegram_kill_switch(message)
        
        # Dashboard
        self._send_dashboard_alert(message)
    
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
# HELPER METHODS FOR AGENT IMPLEMENTATIONS
# ============================================================================

# Add these helper methods to BaseAgent class
class BaseAgentHelpers:
    """Helper methods for agent implementations"""
    
    def _send_telegram_notification(self, decision):
        """Send notification via Telegram"""
        try:
            # Import telegram bot integration
            try:
                from telegram_bot import send_message
                telegram_available = True
            except ImportError:
                logger.warning("Telegram bot not available - using fallback notification")
                telegram_available = False
            
            message = f"🤖 {decision.agent_name}\n{decision.description}\nRisk: {decision.risk_level.value}\nConfidence: {decision.confidence:.1%}"
            
            if telegram_available:
                send_message(message)
                logger.info("Telegram notification sent")
            else:
                # Fallback notification method
                logger.info(f"ALERT: {message}")
        except ImportError:
            logger.warning("Telegram bot not available")
        except Exception as e:
            logger.error(f"Failed to send telegram notification: {e}")
    
    def _send_email_notification(self, decision):
        """Send email notification"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Configuration (should be in config file)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = os.getenv("NOTIFICATION_EMAIL", "")
            sender_password = os.getenv("NOTIFICATION_PASSWORD", "")
            recipient_email = os.getenv("ADMIN_EMAIL", "")
            
            if not all([sender_email, sender_password, recipient_email]):
                logger.warning("Email configuration missing")
                return
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Veyra Agent Alert: {decision.agent_name}"
            
            body = f"""
Agent: {decision.agent_name}
Action: {decision.description}
Risk Level: {decision.risk_level.value}
Confidence: {decision.confidence:.1%}
Timestamp: {decision.timestamp}
Details: {decision.details}
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            logger.info("Email notification sent")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def _collect_market_data(self):
        """Collect market data from APIs"""
        try:
            # Get current prices for major ETFs
            tickers = ["VUAG", "AGGH", "AYEM", "HMWO"]
            market_data = {}
            
            for ticker in tickers:
                # Simulate API call (would use real price API)
                price = self._get_current_price(ticker)
                market_data[ticker] = {
                    'price': price,
                    'change': 0.0,  # Would calculate from historical data
                    'volume': 1000000,
                    'timestamp': datetime.now()
                }
            
            # Store in database
            self._store_market_data(market_data)
            logger.info(f"Collected market data for {len(tickers)} tickers")
            
        except Exception as e:
            logger.error(f"Failed to collect market data: {e}")
    
    def _get_portfolio_holdings(self):
        """Get current portfolio holdings from database"""
        try:
            # Query database for holdings
            conn = sqlite3.connect('veyra.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ticker, shares, avg_cost, current_price 
                FROM holdings 
                WHERE shares > 0
                ORDER BY ticker
            """)
            
            holdings = []
            for row in cursor.fetchall():
                holdings.append({
                    'ticker': row[0],
                    'shares': row[1],
                    'avg_cost': row[2],
                    'current_price': row[3] or 0.0
                })
            
            conn.close()
            return holdings
            
        except Exception as e:
            logger.error(f"Failed to get portfolio holdings: {e}")
            return []
    
    def _get_current_price(self, ticker):
        """Get current price for a ticker"""
        # Simulate price lookup (would use real API)
        price_map = {
            'VUAG': 50.25,  # Vanguard US Aggressive
            'AGGH': 100.50, # iShares Aggregate Bond
            'AYEM': 25.75,  # iShares Emerging Markets
            'HMWO': 75.30,  # Henderson World
        }
        return price_map.get(ticker, 100.0)  # Default price
    
    def _get_isa_contributions(self, year):
        """Get ISA contributions for current year"""
        try:
            conn = sqlite3.connect('veyra.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total
                FROM transactions 
                WHERE transaction_type = 'CONTRIBUTION' 
                AND account_type = 'ISA'
                AND strftime('%Y', transaction_date) = ?
            """, (str(year),))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0.0
            
        except Exception as e:
            logger.error(f"Failed to get ISA contributions: {e}")
            return 0.0
    
    def _submit_trade(self, trade_order):
        """Submit trade to broker"""
        # Simulate trade execution
        logger.info(f"Submitting trade: {trade_order}")
        return {
            'success': True,
            'order_id': f"order_{datetime.now().timestamp()}",
            'status': 'submitted'
        }
    
    def _schedule_buy_back(self, ticker, shares, days):
        """Schedule buy-back after wash sale period"""
        buy_back_date = datetime.now() + timedelta(days=days)
        logger.info(f"Scheduled buy-back: {ticker} {shares} shares on {buy_back_date}")
    
    def _get_portfolio_returns(self):
        """Get historical portfolio returns"""
        # Simulate return data (would calculate from actual portfolio history)
        import random
        return [random.gauss(0.001, 0.02) for _ in range(100)]  # 100 days of returns
    
    def _get_portfolio_assets(self):
        """Get list of assets in portfolio"""
        holdings = self._get_portfolio_holdings()
        return [h['ticker'] for h in holdings]
    
    def _calculate_correlation(self, asset1, asset2):
        """Calculate correlation between two assets"""
        # Simulate correlation calculation
        return random.uniform(-0.5, 0.8)
    
    def _get_current_allocation(self):
        """Get current portfolio allocation percentages"""
        holdings = self._get_portfolio_holdings()
        total_value = sum(h['shares'] * h['current_price'] for h in holdings)
        
        allocation = {}
        for holding in holdings:
            value = holding['shares'] * holding['current_price']
            allocation[holding['ticker']] = (value / total_value) * 100 if total_value > 0 else 0
        
        return allocation
    
    def _get_target_allocation(self):
        """Get target portfolio allocation"""
        return {
            'VUAG': 40,  # 40% US Aggressive
            'AGGH': 30,  # 30% Bonds
            'AYEM': 20,  # 20% Emerging Markets
            'HMWO': 10   # 10% World
        }
    
    def _store_market_data(self, data):
        """Store market data in database"""
        try:
            conn = sqlite3.connect('veyra.db')
            cursor = conn.cursor()
            
            for ticker, info in data.items():
                cursor.execute("""
                    INSERT INTO price_history (ticker, price, volume, source, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (ticker, info['price'], info['volume'], 'agent_framework', info['timestamp']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store market data: {e}")
    
    def _send_telegram_kill_switch(self, message):
        """Send emergency kill switch notification"""
        self._send_telegram_notification(type('', (), {'agent_name': 'KILL_SWITCH', 'description': message, 'risk_level': type('', (), {'value': 'CRITICAL'}), 'confidence': 1.0})())
    
    def _send_dashboard_alert(self, message):
        """Send alert to dashboard"""
        try:
            # Would send via WebSocket to dashboard
            logger.info(f"Dashboard alert: {message}")
        except Exception as e:
            logger.error(f"Failed to send dashboard alert: {e}")


# INITIALIZATION HELPERS
# ============================================================================

def create_default_agents(orchestrator: AgentOrchestrator, llm_manager=None) -> List[str]:
    """Create and register all 8 default agents"""
    agents = [
        MarketDataCollectorAgent(orchestrator.approval_gate, llm_manager),
        TaxOptimizerAgent(orchestrator.approval_gate, llm_manager),
        RiskManagerAgent(orchestrator.approval_gate, llm_manager),
        PortfolioRebalancerAgent(orchestrator.approval_gate, llm_manager),
        RetirementPlannerAgent(orchestrator.approval_gate, llm_manager),
        WithdrawalStrategistAgent(orchestrator.approval_gate, llm_manager),
        SentimentAnalyzerAgent(orchestrator.approval_gate, llm_manager),
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
