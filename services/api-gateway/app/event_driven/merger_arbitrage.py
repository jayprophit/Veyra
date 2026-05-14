"""Merger Arbitrage - Analyze and trade pending mergers"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MergerDeal:
    acquirer: str
    target: str
    target_price: float
    offer_price: float
    deal_type: str  # cash, stock, mixed
    announced_date: datetime
    expected_close: datetime
    regulatory_status: str  # pending, approved, blocked
    shareholder_approved: bool
    termination_date: datetime
    termination_fee_pct: float
    probability_success: float  # Market implied probability

class MergerArbitrage:
    """Analyze merger arbitrage opportunities"""
    
    def __init__(self):
        self.deals: List[MergerDeal] = []
    
    def add_deal(self, deal: MergerDeal):
        """Add merger deal to tracker"""
        self.deals.append(deal)
    
    def calculate_spread(self, deal: MergerDeal) -> Dict:
        """Calculate merger arbitrage spread"""
        if deal.offer_price <= 0:
            return {"error": "Invalid offer price"}
        
        absolute_spread = deal.offer_price - deal.target_price
        spread_pct = (absolute_spread / deal.target_price) * 100
        
        # Annualize return
        days_until = (deal.expected_close - datetime.utcnow()).days
        if days_until <= 0:
            annualized_return = 0
        else:
            annualized_return = spread_pct * (365 / days_until)
        
        # Risk-adjusted return (probability weighted)
        expected_return = annualized_return * (deal.probability_success / 100)
        
        return {
            "target": deal.target,
            "acquirer": deal.acquirer,
            "current_price": deal.target_price,
            "offer_price": deal.offer_price,
            "absolute_spread": round(absolute_spread, 2),
            "spread_pct": round(spread_pct, 2),
            "days_until_close": days_until,
            "annualized_return": round(annualized_return, 1),
            "probability_success": deal.probability_success,
            "expected_return": round(expected_return, 1),
            "risk_adjusted": "ATTRACTIVE" if expected_return > 15 else "MARGINAL" if expected_return > 8 else "POOR"
        }
    
    def assess_deal_risk(self, deal: MergerDeal) -> Dict:
        """Assess risk factors for merger completion"""
        risk_score = 0
        risk_factors = []
        positive_factors = []
        
        # Regulatory risk
        if deal.regulatory_status == "blocked":
            risk_score += 50
            risk_factors.append("Deal blocked by regulators")
        elif deal.regulatory_status == "approved":
            risk_score -= 10
            positive_factors.append("Regulatory approval received")
        else:
            risk_score += 15  # Pending = uncertainty
        
        # Shareholder approval
        if deal.shareholder_approved:
            risk_score -= 10
            positive_factors.append("Shareholder approval obtained")
        else:
            risk_score += 10
            risk_factors.append("Shareholder vote pending")
        
        # Time risk
        days_remaining = (deal.expected_close - datetime.utcnow()).days
        if days_remaining < 0:
            risk_score += 40
            risk_factors.append("Deal delayed past expected close")
        elif days_remaining > 180:
            risk_score += 10
            risk_factors.append("Long time horizon increases uncertainty")
        
        # Termination fee protection
        if deal.termination_fee_pct > 3:
            risk_score -= 5
            positive_factors.append(f"Strong termination fee ({deal.termination_fee_pct}%)")
        
        # Market implied probability
        if deal.probability_success < 60:
            risk_score += 20
            risk_factors.append("Market pricing low probability of success")
        elif deal.probability_success > 85:
            risk_score -= 15
            positive_factors.append("High market confidence")
        
        risk_level = "HIGH" if risk_score > 30 else "MODERATE" if risk_score > 10 else "LOW"
        
        return {
            "target": deal.target,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "positive_factors": positive_factors,
            "recommendation": "AVOID" if risk_score > 40 else "CAUTION" if risk_score > 20 else "ACCEPTABLE"
        }
    
    def find_best_opportunities(self, min_expected_return: float = 10.0) -> List[Dict]:
        """Find best risk-adjusted merger arbitrage opportunities"""
        opportunities = []
        
        for deal in self.deals:
            spread = self.calculate_spread(deal)
            risk = self.assess_deal_risk(deal)
            
            if "error" in spread:
                continue
            
            if spread["expected_return"] >= min_expected_return and risk["risk_score"] < 35:
                opportunities.append({
                    "target": deal.target,
                    "acquirer": deal.acquirer,
                    "spread_pct": spread["spread_pct"],
                    "annualized_return": spread["annualized_return"],
                    "expected_return": spread["expected_return"],
                    "days_until_close": spread["days_until_close"],
                    "risk_level": risk["risk_level"],
                    "risk_factors": len(risk["risk_factors"]),
                    "overall_score": round(spread["expected_return"] - risk["risk_score"], 1)
                })
        
        return sorted(opportunities, key=lambda x: x["overall_score"], reverse=True)
    
    def get_deal_flow_summary(self, days: int = 30) -> Dict:
        """Get summary of recent deal flow"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        recent_deals = [d for d in self.deals if d.announced_date > cutoff]
        pending_deals = [d for d in self.deals if d.expected_close > datetime.utcnow()]
        
        # Calculate aggregate statistics
        total_deal_value = sum(d.offer_price for d in recent_deals)
        avg_spread = sum(self.calculate_spread(d)["spread_pct"] for d in pending_deals) / len(pending_deals) if pending_deals else 0
        
        return {
            "new_deals_30d": len(recent_deals),
            "pending_deals": len(pending_deals),
            "total_deal_value": round(total_deal_value / 1e9, 2),  # In billions
            "average_spread": round(avg_spread, 2),
            "market_activity": "HIGH" if len(recent_deals) > 10 else "NORMAL" if len(recent_deals) > 5 else "LOW",
            "best_opportunities": self.find_best_opportunities()[:5]
        }
