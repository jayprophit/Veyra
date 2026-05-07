"""Analytics API Endpoints - Connect analytics to dashboard"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from auth_security_system import TokenData, Permission, require_permissions
from advanced_analytics import (
    AdvancedAnalytics, RiskMetrics, 
    PortfolioOptimizer, MonteCarloSimulator
)
from database_layer import DatabaseManager

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
analytics = AdvancedAnalytics()
optimizer = PortfolioOptimizer()
mc_sim = MonteCarloSimulator()

def get_db():
    db = DatabaseManager()
    db.connect()
    return db

@router.get("/portfolio/{portfolio_id}/risk")
async def get_risk_metrics(
    portfolio_id: str,
    user: TokenData = Depends(require_permissions(Permission.READ_PORTFOLIO))
) -> Dict[str, Any]:
    """Get portfolio risk metrics"""
    try:
        db = get_db()
        portfolio = db.get_portfolio(user.user_id, portfolio_id)
        
        returns = pd.Series(portfolio.get('returns', []))
        
        metrics = analytics.calculate_all_risk_metrics(
            returns=returns,
            weights=portfolio.get('weights'),
            risk_free_rate=0.045,
            period="daily"
        )
        
        return {
            "portfolio_id": portfolio_id,
            "metrics": metrics.to_dict(),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio/{portfolio_id}/optimize")
async def optimize_portfolio(
    portfolio_id: str,
    target_return: Optional[float] = None,
    risk_free_rate: float = 0.045,
    user: TokenData = Depends(require_permissions(Permission.WRITE_PORTFOLIO))
) -> Dict[str, Any]:
    """Optimize portfolio using Markowitz"""
    try:
        db = get_db()
        portfolio = db.get_portfolio(user.user_id, portfolio_id)
        
        result = optimizer.optimize_mean_variance(
            returns=pd.DataFrame(portfolio['returns_history']),
            target_return=target_return,
            risk_free_rate=risk_free_rate
        )
        
        return {
            "portfolio_id": portfolio_id,
            "optimal_weights": result.optimal_weights.tolist(),
            "expected_return": result.expected_return,
            "risk": result.risk,
            "sharpe_ratio": result.sharpe_ratio,
            "recommendations": result.rebalance_recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/{portfolio_id}/efficient-frontier")
async def get_efficient_frontier(
    portfolio_id: str,
    num_portfolios: int = 100,
    user: TokenData = Depends(require_permissions(Permission.READ_PORTFOLIO))
) -> Dict[str, Any]:
    """Get efficient frontier data for charts"""
    try:
        db = get_db()
        portfolio = db.get_portfolio(user.user_id, portfolio_id)
        
        returns_df = pd.DataFrame(portfolio['returns_history'])
        frontier = optimizer.generate_efficient_frontier(
            returns_df, num_portfolios=num_portfolios
        )
        
        return {
            "portfolio_id": portfolio_id,
            "frontier": frontier
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio/{portfolio_id}/monte-carlo")
async def run_monte_carlo(
    portfolio_id: str,
    initial_value: float,
    years: int = 30,
    simulations: int = 10000,
    user: TokenData = Depends(require_permissions(Permission.READ_PORTFOLIO))
) -> Dict[str, Any]:
    """Run Monte Carlo retirement simulation"""
    try:
        db = get_db()
        portfolio = db.get_portfolio(user.user_id, portfolio_id)
        
        weights = np.array(portfolio['weights'])
        returns = pd.DataFrame(portfolio['returns_history'])
        
        results = mc_sim.simulate_retirement_scenarios(
            initial_portfolio_value=initial_value,
            annual_withdrawal=initial_value * 0.04,
            years=years,
            weights=weights,
            expected_returns=returns.mean(),
            cov_matrix=returns.cov()
        )
        
        return {
            "portfolio_id": portfolio_id,
            "success_probability": results['success_probability'],
            "median_final_value": results['median_final_value'],
            "percentile_5": results['percentile_5'],
            "percentile_95": results['percentile_95'],
            "chart_data": results['chart_data']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/scenario-analysis")
async def scenario_analysis(
    portfolio_id: str,
    user: TokenData = Depends(require_permissions(Permission.READ_PORTFOLIO))
) -> Dict[str, Any]:
    """Run scenario stress tests"""
    scenarios = {
        "2008_crisis": {"stock": -0.37, "bond": 0.05},
        "covid_crash": {"stock": -0.34, "bond": 0.08},
        "inflation_shock": {"stock": -0.15, "bond": -0.20},
        "tech_bubble": {"stock": -0.78, "bond": 0.10}
    }
    
    results = {}
    for name, impacts in scenarios.items():
        # Calculate realistic impact based on scenario
        stock_impact = impacts.get("stock", 0)
        bond_impact = impacts.get("bond", 0)
        
        # Calculate portfolio impact (weighted average)
        portfolio_impact = (stock_impact * 0.7) + (bond_impact * 0.3)
        
        # Estimate recovery time based on severity
        if abs(portfolio_impact) > 0.5:
            recovery_time = "12-18 months"
        elif abs(portfolio_impact) > 0.2:
            recovery_time = "6-12 months"
        else:
            recovery_time = "3-6 months"
        
        results[name] = {
            "estimated_impact": round(portfolio_impact * 100, 2),  # Convert to percentage
            "recovery_time": recovery_time,
            "stock_impact": round(stock_impact * 100, 2),
            "bond_impact": round(bond_impact * 100, 2)
        }
    
    return {"scenarios": results}

print("Analytics API endpoints loaded")
