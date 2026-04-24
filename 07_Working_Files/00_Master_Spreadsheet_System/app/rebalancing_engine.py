"""Portfolio Rebalancing Engine - Auto-rebalancing with tax efficiency"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

@dataclass
class TargetAllocation:
    symbol: str
    target_weight: float
    tolerance: float = 0.02  # 2% drift allowed
    
@dataclass
class RebalanceRecommendation:
    symbol: str
    current_weight: float
    target_weight: float
    action: str  # "BUY" or "SELL"
    shares: float
    estimated_value: float
    tax_impact: float = 0.0
    priority: int = 0

class RebalancingEngine:
    """SSS-Grade portfolio rebalancing"""
    
    def __init__(self, tax_loss_engine=None):
        self.tax_loss_engine = tax_loss_engine
        
    def analyze_drift(
        self,
        current_positions: Dict[str, float],
        target_allocations: List[TargetAllocation],
        portfolio_value: float
    ) -> List[Dict]:
        """Check allocation drift from targets"""
        drifts = []
        
        for target in target_allocations:
            current_value = current_positions.get(target.symbol, 0)
            current_weight = current_value / portfolio_value if portfolio_value > 0 else 0
            weight_diff = abs(current_weight - target.target_weight)
            
            drifts.append({
                "symbol": target.symbol,
                "current_weight": current_weight,
                "target_weight": target.target_weight,
                "drift": weight_diff,
                "needs_rebalance": weight_diff > target.tolerance
            })
        
        return sorted(drifts, key=lambda x: x["drift"], reverse=True)
    
    def generate_recommendations(
        self,
        current_positions: Dict[str, Dict],
        target_allocations: List[TargetAllocation],
        portfolio_value: float,
        prices: Dict[str, float],
        consider_tax: bool = True
    ) -> List[RebalanceRecommendation]:
        """Generate tax-efficient rebalancing trades"""
        
        recommendations = []
        cash_needed = 0.0
        cash_available = 0.0
        
        # Calculate current weights
        for target in target_allocations:
            pos = current_positions.get(target.symbol, {})
            current_shares = pos.get("shares", 0)
            current_price = prices.get(target.symbol, 0)
            current_value = current_shares * current_price
            current_weight = current_value / portfolio_value if portfolio_value > 0 else 0
            
            target_value = portfolio_value * target.target_weight
            weight_diff = target_value - current_value
            
            if abs(weight_diff) > (portfolio_value * target.tolerance):
                shares_to_trade = weight_diff / current_price if current_price > 0 else 0
                
                # Determine tax impact
                tax_impact = 0.0
                if consider_tax and self.tax_loss_engine and shares_to_trade < 0:
                    # Selling - check for tax loss harvesting opportunity
                    unrealized_pnl = pos.get("unrealized_pnl", 0)
                    if unrealized_pnl < 0:
                        tax_impact = abs(unrealized_pnl) * 0.20  # Estimated tax savings
                
                rec = RebalanceRecommendation(
                    symbol=target.symbol,
                    current_weight=current_weight,
                    target_weight=target.target_weight,
                    action="BUY" if shares_to_trade > 0 else "SELL",
                    shares=abs(shares_to_trade),
                    estimated_value=abs(weight_diff),
                    tax_impact=tax_impact,
                    priority=int(abs(weight_diff) / portfolio_value * 100)
                )
                
                recommendations.append(rec)
        
        # Sort by tax benefit (sell losers first), then by priority
        recommendations.sort(key=lambda x: (x.tax_impact * -1 if x.action == "SELL" else 0, -x.priority))
        
        return recommendations
    
    def optimize_cash_flow(
        self,
        recommendations: List[RebalanceRecommendation],
        available_cash: float
    ) -> List[RebalanceRecommendation]:
        """Optimize for available cash - may need to reduce some buys"""
        
        buys = [r for r in recommendations if r.action == "BUY"]
        sells = [r for r in recommendations if r.action == "SELL"]
        
        sell_proceeds = sum(r.estimated_value for r in sells)
        total_buy_required = sum(r.estimated_value for r in buys)
        
        # If we have enough cash + sells, execute all
        if available_cash + sell_proceeds >= total_buy_required:
            return recommendations
        
        # Need to prioritize - reduce lowest priority buys
        available_for_buys = available_cash + sell_proceeds
        sorted_buys = sorted(buys, key=lambda x: x.priority, reverse=True)
        
        final_recs = sells.copy()
        remaining = available_for_buys
        
        for buy in sorted_buys:
            if remaining >= buy.estimated_value:
                final_recs.append(buy)
                remaining -= buy.estimated_value
            else:
                # Partial fill
                ratio = remaining / buy.estimated_value if buy.estimated_value > 0 else 0
                if ratio > 0.1:  # At least 10% fill
                    buy.shares *= ratio
                    buy.estimated_value *= ratio
                    final_recs.append(buy)
                    remaining = 0
                break
        
        return final_recs
    
    def create_rebalancing_plan(
        self,
        portfolio_id: str,
        target_allocations: List[TargetAllocation],
        current_positions: Dict,
        prices: Dict[str, float],
        constraints: Optional[Dict] = None
    ) -> Dict:
        """Create comprehensive rebalancing plan"""
        
        portfolio_value = sum(
            pos.get("shares", 0) * prices.get(sym, 0) 
            for sym, pos in current_positions.items()
        )
        
        drift_analysis = self.analyze_drift(
            {sym: pos.get("shares", 0) * prices.get(sym, 0) 
             for sym, pos in current_positions.items()},
            target_allocations,
            portfolio_value
        )
        
        needs_rebalance = any(d["needs_rebalance"] for d in drift_analysis)
        
        if not needs_rebalance:
            return {
                "portfolio_id": portfolio_id,
                "needs_rebalance": False,
                "drift_analysis": drift_analysis,
                "message": "Portfolio within tolerance bands"
            }
        
        recommendations = self.generate_recommendations(
            current_positions, target_allocations, portfolio_value, prices
        )
        
        available_cash = constraints.get("available_cash", 0) if constraints else 0
        optimized = self.optimize_cash_flow(recommendations, available_cash)
        
        total_tax_savings = sum(
            r.tax_impact for r in optimized if r.action == "SELL" and r.tax_impact > 0
        )
        
        return {
            "portfolio_id": portfolio_id,
            "needs_rebalance": True,
            "portfolio_value": portfolio_value,
            "drift_analysis": drift_analysis,
            "recommendations": [
                {
                    "symbol": r.symbol,
                    "action": r.action,
                    "shares": round(r.shares, 4),
                    "estimated_value": round(r.estimated_value, 2),
                    "priority": r.priority,
                    "tax_savings": round(r.tax_impact, 2) if r.tax_impact > 0 else 0
                }
                for r in optimized
            ],
            "estimated_tax_savings": round(total_tax_savings, 2),
            "total_estimated_costs": round(
                sum(r.estimated_value * 0.001 for r in optimized), 2  # 0.1% commission
            ),
            "net_tax_benefit": round(total_tax_savings - sum(r.estimated_value * 0.001 for r in optimized), 2),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def execute_rebalancing(
        self,
        plan: Dict,
        broker_client,
        dry_run: bool = True
    ) -> Dict:
        """Execute rebalancing trades through broker"""
        
        results = []
        
        for rec in plan.get("recommendations", []):
            try:
                if not dry_run:
                    # Execute actual trade
                    order = broker_client.place_order(
                        symbol=rec["symbol"],
                        side=rec["action"],
                        quantity=rec["shares"],
                        order_type="MARKET"
                    )
                    status = "EXECUTED"
                else:
                    status = "SIMULATED"
                
                results.append({
                    "symbol": rec["symbol"],
                    "action": rec["action"],
                    "shares": rec["shares"],
                    "status": status,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                results.append({
                    "symbol": rec["symbol"],
                    "action": rec["action"],
                    "status": "FAILED",
                    "error": str(e)
                })
        
        return {
            "plan_id": plan.get("portfolio_id"),
            "dry_run": dry_run,
            "executions": results,
            "successful": sum(1 for r in results if r["status"] in ["EXECUTED", "SIMULATED"]),
            "failed": sum(1 for r in results if r["status"] == "FAILED")
        }

print("Rebalancing Engine loaded - SSS-grade tax-efficient rebalancing")
