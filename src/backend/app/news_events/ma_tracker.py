"""Merger & Acquisition Tracker - M&A arbitrage and deal analysis"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class DealStatus(Enum):
    RUMORED = "rumored"
    ANNOUNCED = "announced"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    COMPLETED = "completed"
    TERMINATED = "terminated"

@dataclass
class MADeal:
    target: str
    acquirer: str
    offer_price: float
    target_price_before: float
    expected_close_date: datetime
    status: DealStatus
    regulatory_hurdles: List[str]
    termination_fee: float  # % of deal value
    probability_of_completion: float

class MergerAcquisitionTracker:
    """Track M&A deals and calculate arbitrage opportunities"""
    
    def __init__(self):
        self.active_deals: List[MADeal] = []
        self.regulatory_bodies = ["DOJ", "FTC", "EC", "CMA", "MOFCOM"]
    
    def add_deal(self, deal: MADeal):
        """Add M&A deal to tracker"""
        self.active_deals.append(deal)
    
    def calculate_merger_arbitrage_spread(self, deal: MADeal, 
                                        current_target_price: float) -> Dict:
        """Calculate risk arbitrage spread and return"""
        if deal.status in [DealStatus.COMPLETED, DealStatus.TERMINATED]:
            return {"error": "Deal is closed"}
        
        # Gross spread
        gross_spread = (deal.offer_price - current_target_price) / current_target_price * 100
        
        # Annualized return
        days_to_close = (deal.expected_close_date - datetime.utcnow()).days
        if days_to_close <= 0:
            days_to_close = 30  # Assume close imminent
        
        annualized_return = gross_spread * (365 / days_to_close)
        
        # Risk-adjusted (account for failure probability)
        prob_success = deal.probability_of_completion
        prob_failure = 1 - prob_success
        
        # Expected return if deal fails (typical -20% drop)
        expected_failure_return = -20
        
        expected_return = (gross_spread * prob_success + 
                          expected_failure_return * prob_failure)
        
        return {
            "target": deal.target,
            "acquirer": deal.acquirer,
            "offer_price": deal.offer_price,
            "current_price": current_target_price,
            "gross_spread_pct": round(gross_spread, 2),
            "days_to_close": days_to_close,
            "annualized_return_pct": round(annualized_return, 1),
            "probability_of_success": prob_success,
            "expected_return_pct": round(expected_return, 2),
            "risk_rating": self._calculate_risk_rating(deal, gross_spread),
            "recommendation": self._get_arbitrage_recommendation(expected_return, prob_success)
        }
    
    def _calculate_risk_rating(self, deal: MADeal, spread: float) -> str:
        """Calculate risk rating for deal"""
        risk_score = 0
        
        # Regulatory risk
        risk_score += len(deal.regulatory_hurdles) * 2
        
        # Spread size (larger = more risk premium demanded)
        if spread > 15:
            risk_score += 3
        elif spread > 8:
            risk_score += 2
        elif spread > 5:
            risk_score += 1
        
        # Time risk
        days_to_close = (deal.expected_close_date - datetime.utcnow()).days
        if days_to_close > 365:
            risk_score += 3
        elif days_to_close > 180:
            risk_score += 2
        elif days_to_close > 90:
            risk_score += 1
        
        if risk_score >= 8:
            return "HIGH"
        elif risk_score >= 5:
            return "MEDIUM"
        return "LOW"
    
    def _get_arbitrage_recommendation(self, expected_return: float, 
                                     prob_success: float) -> str:
        """Get arbitrage recommendation"""
        if expected_return > 15 and prob_success > 0.8:
            return "STRONG_BUY"
        elif expected_return > 8 and prob_success > 0.7:
            return "BUY"
        elif expected_return > 0 and prob_success > 0.6:
            return "SPECULATIVE"
        elif expected_return < -5:
            return "AVOID"
        return "NEUTRAL"
    
    def monitor_deal_developments(self, deal: MADeal, 
                                 news_items: List[Dict]) -> Dict:
        """Monitor deal for news that changes probability"""
        prob_change = 0
        alerts = []
        
        for news in news_items:
            headline = news.get("headline", "").lower()
            
            # Positive signals
            if any(word in headline for word in ["approved", "cleared", "blessed"]):
                prob_change += 0.15
                alerts.append({"type": "POSITIVE", "news": headline})
            elif "early termination" in headline:
                prob_change += 0.10
                alerts.append({"type": "POSITIVE", "news": "Accelerated timeline"})
            
            # Negative signals
            if any(word in headline for word in ["blocked", "rejected", "challenged"]):
                prob_change -= 0.20
                alerts.append({"type": "NEGATIVE", "news": headline})
            elif "second request" in headline:
                prob_change -= 0.10
                alerts.append({"type": "NEGATIVE", "news": "Extended review"})
            
            if "competing bid" in headline or "interloper" in headline:
                prob_change += 0.05  # Could be positive (higher price) or negative (delay)
                alerts.append({"type": "UNCERTAIN", "news": "New bidder emerged"})
        
        new_prob = max(0, min(1, deal.probability_of_completion + prob_change))
        
        return {
            "target": deal.target,
            "probability_change": round(prob_change, 2),
            "old_probability": deal.probability_of_completion,
            "new_probability": round(new_prob, 2),
            "alerts": alerts,
            "action_required": abs(prob_change) > 0.1
        }
    
    def get_universal_deal_summary(self) -> Dict:
        """Get summary of all active M&A deals"""
        active = [d for d in self.active_deals if d.status not in 
                 [DealStatus.COMPLETED, DealStatus.TERMINATED]]
        
        by_status = {}
        for deal in active:
            status = deal.status.value
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(deal)
        
        # Calculate average spread
        spreads = []
        for deal in active:
            arb = self.calculate_merger_arbitrage_spread(deal, deal.target_price_before)
            if "gross_spread_pct" in arb:
                spreads.append(arb["gross_spread_pct"])
        
        avg_spread = statistics.mean(spreads) if spreads else 0
        
        return {
            "total_active_deals": len(active),
            "by_status": {k: len(v) for k, v in by_status.items()},
            "avg_arbitrage_spread": round(avg_spread, 2),
            "high_opportunity_deals": sum(1 for s in spreads if s > 10),
            "closing_this_quarter": sum(1 for d in active 
                if (d.expected_close_date - datetime.utcnow()).days < 90)
        }

import statistics
