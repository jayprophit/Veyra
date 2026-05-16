"""
Veyra API Server - FastAPI Backend with Authentication
==========================================
REST API to serve the React Dashboard.

Endpoints:
- GET /api/portfolio          - Portfolio summary
- GET /api/holdings           - All holdings
- GET /api/transactions       - Transaction history
- GET /api/tax/summary        - Tax year summary
- GET /api/agents/status      - Agent status
- GET /api/agents/decisions   - Pending decisions
- POST /api/agents/approve     - Approve decision
- GET /api/retirement/mc      - Monte Carlo results
- GET /api/tax/harvest        - Tax-loss opportunities
- GET /api/websocket/status   - WebSocket feed status

Run: uvicorn 19_API_Server:app --reload --port 8000
"""

import os
import json
import asyncio
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import system components
from database_layer import DatabaseManager, DatabaseConfig
from autonomous_agent_framework import AgentOrchestrator, GuardrailConfig
from websocket_real_time_feeds import DataFeedManager, WebSocketConfig, DataProvider
from retirement_monte_carlo import RetirementPlanner, RetirementScenario, WithdrawalStrategy
from tax_loss_harvesting import TaxLossHarvester
from auth_security_system import SSSSecurityManager, UserRole, Permission
from api_middleware import AuthMiddleware, require_auth, can_read_portfolio, can_trade

# Import API routes (including FinOS integrations)
from api.fuel_tracker import router as fuel_router

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PortfolioSummary(BaseModel):
    total_value: float
    cost_basis: float
    unrealized_pnl: float
    by_account: Dict[str, Dict[str, float]]

class Holding(BaseModel):
    ticker: str
    name: Optional[str]
    shares: float
    avg_cost: float
    current_price: Optional[float]
    account_type: str
    value: Optional[float]

class Transaction(BaseModel):
    id: int
    ticker: str
    type: str
    shares: Optional[float]
    price: Optional[float]
    amount: float
    date: str
    account_type: str

class Decision(BaseModel):
    decision_id: str
    agent_name: str
    action_type: str
    risk_level: str
    description: str
    status: str
    created_at: str

class MonteCarloRequest(BaseModel):
    current_age: int
    retirement_age: int
    current_savings: float
    monthly_contribution: float
    annual_withdrawal: float
    expected_return: float = 0.07
    volatility: float = 0.15

class SystemStatus(BaseModel):
    api_running: bool
    database_connected: bool
    websocket_status: str
    agents_running: int
    pending_decisions: int
    timestamp: str

# ============================================================================
# GLOBAL STATE
# ============================================================================

db: Optional[DatabaseManager] = None
orchestrator: Optional[AgentOrchestrator] = None
feed_manager: Optional[DataFeedManager] = None

# ============================================================================
# LIFESPAN MANAGER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global db, orchestrator, feed_manager
    
    # Startup
    print("🚀 Starting Veyra API Server...")
    
    # Initialize database
    db_config = DatabaseConfig(
        db_type=os.getenv('DB_TYPE', 'sqlite'),
        sqlite_path=os.getenv('SQLITE_PATH', './data/veyra.db')
    )
    db = DatabaseManager(db_config)
    
    # Initialize agent orchestrator
    guardrail_config = GuardrailConfig(
        max_daily_trades=int(os.getenv('MAX_DAILY_TRADES', 5)),
        require_approval_above=float(os.getenv('APPROVAL_THRESHOLD', 10000))
    )
    orchestrator = AgentOrchestrator(guardrail_config)
    
    # Initialize data feed
    ws_config = WebSocketConfig(
        primary_provider=DataProvider.MOCK,
        mock_update_interval=2.0
    )
    feed_manager = DataFeedManager(ws_config).setup(DataProvider.MOCK)
    
    # Start data feed in background
    asyncio.create_task(feed_manager.start())
    
    print("✅ API Server ready")
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    if feed_manager:
        feed_manager.stop()
    if db:
        db.close()
    print("👋 Goodbye")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Veyra API",
    description="AI-powered financial management API",
    version="2.0.0",
    lifespan=lifespan
)

# Initialize auth
security_mgr = SSSSecurityManager()
app.add_middleware(AuthMiddleware, security_manager=security_mgr)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite, React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(fuel_router)

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/system/status", response_model=SystemStatus)
async def system_status() -> SystemStatus:
    """Get complete system status."""
    agents_status = orchestrator.get_status() if orchestrator else {}
    
    return SystemStatus(
        api_running=True,
        database_connected=db is not None,
        websocket_status="connected" if feed_manager else "disconnected",
        agents_running=len([a for a in agents_status.get('agents', {}).values() if a.get('running')]),
        pending_decisions=agents_status.get('pending_approvals', 0),
        timestamp=datetime.now().isoformat()
    )

# Portfolio endpoints
@app.get("/api/portfolio/summary")
async def portfolio_summary() -> PortfolioSummary:
    """Get portfolio summary."""
    if not db:
        raise HTTPException(503, "Database not available")
    
    summary = db.get_portfolio_value()
    
    return PortfolioSummary(
        total_value=summary.get('total', 0),
        cost_basis=summary.get('cost_basis', 0),
        unrealized_pnl=summary.get('unrealized_pnl', 0),
        by_account={k: v for k, v in summary.items() if isinstance(v, dict)}
    )

@app.get("/api/holdings", response_model=List[Holding])
async def get_holdings(account_type: Optional[str] = None) -> List[Holding]:
    """Get all holdings or filter by account type."""
    if not db:
        raise HTTPException(503, "Database not available")
    
    holdings = db.get_holdings(account_type)
    result = []
    for h in holdings:
        value = h['shares'] * (h.get('current_price') or h.get('avg_cost', 0))
        result.append(Holding(
            ticker=h['ticker'],
            name=h.get('name'),
            shares=h['shares'],
            avg_cost=h['avg_cost'],
            current_price=h.get('current_price'),
            account_type=h['account_type'],
            value=value
        ))
    return result

@app.get("/api/transactions", response_model=List[Transaction])
async def get_transactions(
    ticker: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Transaction]:
    """Get transactions with optional filters."""
    if not db:
        raise HTTPException(503, "Database not available")
    
    txns = db.get_transactions(start_date, end_date, ticker)
    return [
        Transaction(
            id=t['id'],
            ticker=t['ticker'],
            type=t['transaction_type'],
            shares=t.get('shares'),
            price=t.get('price'),
            amount=t['amount'],
            date=t['transaction_date'],
            account_type=t['account_type']
        ) for t in txns
    ]

# Tax endpoints
@app.get("/api/tax/summary")
async def tax_summary(tax_year: Optional[str] = None) -> Dict[str, Any]:
    """Get tax summary for current or specified tax year."""
    if not db:
        raise HTTPException(503, "Database not available")
    
    if not tax_year:
        today = date.today()
        tax_year = f"{today.year}-{(today.year + 1) % 100:02d}"
    
    harvester = TaxLossHarvester(db.conn)
    summary = harvester.get_harvest_summary()
    
    return summary

@app.get("/api/tax/harvest-opportunities")
async def harvest_opportunities() -> List[Dict[str, Any]]:
    """Get tax-loss harvesting opportunities."""
    if not db:
        raise HTTPException(503, "Database not available")
    
    harvester = TaxLossHarvester(db.conn)
    opportunities = harvester.find_opportunities()
    
    return [
        {
            "ticker": opp.ticker,
            "account_type": opp.account_type,
            "unrealized_loss": opp.unrealized_loss,
            "cgt_savings": opp.cgt_savings,
            "wash_sale_status": opp.wash_sale_status.value,
            "days_since_last_buy": opp.days_since_last_buy,
            "replacement_candidates": opp.replacement_candidates or [],
            "bed_and_isa_eligible": opp.bed_and_isa_eligible
        }
        for opp in opportunities[:10]  # Top 10
    ]

# Retirement endpoints
@app.post("/api/retirement/monte-carlo")
async def monte_carlo_simulation(request: MonteCarloRequest) -> Dict[str, Any]:
    """Run Monte Carlo retirement simulation."""
    planner = RetirementPlanner(db.conn if db else None)
    
    scenario = RetirementScenario(
        current_age=request.current_age,
        retirement_age=request.retirement_age,
        current_savings=request.current_savings,
        monthly_contribution=request.monthly_contribution,
        annual_withdrawal=request.annual_withdrawal,
        expected_return_mean=request.expected_return,
        expected_return_std=request.volatility,
        strategy=WithdrawalStrategy.PERCENTAGE
    )
    
    results = planner.run_monte_carlo(scenario, num_simulations=5000)
    
    return {
        "success_rate": results.success_rate,
        "probability_of_failure": results.probability_of_failure,
        "median_final_balance": results.median_final_balance,
        "p10_final_balance": results.p10_final_balance,
        "p90_final_balance": results.p90_final_balance,
        "median_depletion_age": results.median_depletion_age,
        "fire_number": results.fire_number,
        "years_to_fire": results.years_to_fire,
        "num_simulations": results.num_simulations
    }

@app.get("/api/retirement/fi-progress")
async def fi_progress(
    current_age: int = 35,
    retirement_age: int = 60,
    current_savings: float = 200000,
    monthly_contribution: float = 1500,
    annual_expenses: float = 45000
) -> Dict[str, Any]:
    """Get Financial Independence progress."""
    planner = RetirementPlanner(db.conn if db else None)
    
    scenario = RetirementScenario(
        current_age=current_age,
        retirement_age=retirement_age,
        current_savings=current_savings,
        monthly_contribution=monthly_contribution,
        annual_withdrawal=annual_expenses
    )
    
    return planner.analyze_fi_progress(scenario)

# Agent endpoints
@app.get("/api/agents/status")
async def agents_status() -> Dict[str, Any]:
    """Get all agent statuses."""
    if not orchestrator:
        raise HTTPException(503, "Agent orchestrator not available")
    
    return orchestrator.get_status()

@app.get("/api/agents/decisions/pending", response_model=List[Decision])
async def pending_decisions() -> List[Decision]:
    """Get pending decisions requiring approval."""
    if not orchestrator:
        raise HTTPException(503, "Agent orchestrator not available")
    
    decisions = orchestrator.get_pending_decisions()
    return [
        Decision(
            decision_id=d.decision_id,
            agent_name=d.agent_name,
            action_type=d.action_type.value,
            risk_level=d.risk_level.value,
            description=d.description,
            status=d.status,
            created_at=d.timestamp.isoformat()
        )
        for d in decisions
    ]

@app.post("/api/agents/decisions/{decision_id}/approve")
async def approve_decision(decision_id: str, approved_by: str = "api_user") -> Dict[str, bool]:
    """Approve a pending decision."""
    if not orchestrator:
        raise HTTPException(503, "Agent orchestrator not available")
    
    success = orchestrator.approve_decision(decision_id, approved_by)
    return {"approved": success}

@app.post("/api/agents/decisions/{decision_id}/reject")
async def reject_decision(decision_id: str, reason: str, rejected_by: str = "api_user") -> Dict[str, bool]:
    """Reject a pending decision."""
    if not orchestrator:
        raise HTTPException(503, "Agent orchestrator not available")
    
    success = orchestrator.reject_decision(decision_id, rejected_by, reason)
    return {"rejected": success}

# WebSocket status
@app.get("/api/websocket/status")
async def websocket_status() -> Dict[str, Any]:
    """Get WebSocket feed status."""
    if not feed_manager or not feed_manager.provider:
        return {"connected": False, "error": "Not initialized"}
    
    return {
        "connected": feed_manager.provider.connected,
        "provider": feed_manager.provider.__class__.__name__,
        "subscribed_tickers": list(feed_manager.provider._subscribed)
    }

# Kill switch
@app.post("/api/system/kill-switch")
async def trigger_kill_switch(reason: str = "api_request", triggered_by: str = "api_user") -> Dict[str, str]:
    """Emergency stop all agents."""
    if not orchestrator:
        raise HTTPException(503, "Agent orchestrator not available")
    
    orchestrator.kill_switch(triggered_by, reason)
    return {"status": "kill_switch_activated", "reason": reason}

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           FINANCIAL MASTER API SERVER                            ║
╠══════════════════════════════════════════════════════════════════╣
║  Endpoints:                                                      ║
║  - http://localhost:8000/api/health                              ║
║  - http://localhost:8000/api/portfolio/summary                   ║
║  - http://localhost:8000/api/agents/status                       ║
║  - http://localhost:8000/api/tax/harvest-opportunities           ║
║  Docs: http://localhost:8000/docs                                ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "19_API_Server:app",
        host="0.0.0.0",
        port=int(os.getenv('API_PORT', 8000)),
        reload=os.getenv('DEBUG', 'false').lower() == 'true',
        log_level="info"
    )
