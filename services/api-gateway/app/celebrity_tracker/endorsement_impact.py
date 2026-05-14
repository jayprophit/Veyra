"""Endorsement Impact Calculator"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Endorsement:
    celebrity: str
    brand: str
    ticker: str
    deal_value: float
    deal_duration_months: int
    announcement_date: datetime
    platform: str

class EndorsementImpactCalculator:
    """Calculate impact of celebrity endorsements on stocks"""
    
    def __init__(self):
        self.impact_factors = {
            "mega": 5.0,      # 100M+ followers
            "macro": 2.5,     # 10M-100M
            "mid": 1.0,       # 1M-10M
            "micro": 0.3,     # 100K-1M
            "nano": 0.1       # <100K
        }
    
    def calculate_impact(self, endorsement: Endorsement, 
                        market_cap: float) -> Dict:
        """Calculate expected endorsement impact"""
        # Determine tier
        if endorsement.deal_value > 10_000_000:
            tier = "mega"
        elif endorsement.deal_value > 1_000_000:
            tier = "macro"
        elif endorsement.deal_value > 100_000:
            tier = "mid"
        else:
            tier = "micro"
        
        base_impact = self.impact_factors[tier]
        
        # Adjust for market cap (smaller = bigger impact)
        market_cap_adj = min(3.0, 100 / (market_cap / 1_000_000_000)) if market_cap > 0 else 1.0
        
        expected_impact = base_impact * market_cap_adj
        
        # Timing
        announcement_age_days = (datetime.utcnow() - endorsement.announcement_date).days
        decay = max(0.3, 1 - (announcement_age_days / 30))
        
        current_impact = expected_impact * decay
        
        return {
            "ticker": endorsement.ticker,
            "celebrity_tier": tier,
            "expected_initial_impact_pct": round(expected_impact, 1),
            "current_expected_impact_pct": round(current_impact, 1),
            "impact_decay": round(decay, 2),
            "roi_estimate": self._estimate_roi(endorsement, market_cap),
            "recommendation": "HOLD" if current_impact > 2 else "SPECULATIVE_BUY" if expected_impact > 3 else "NEUTRAL"
        }
    
    def _estimate_roi(self, endorsement: Endorsement, market_cap: float) -> Dict:
        """Estimate ROI of endorsement deal"""
        # Assume impact drives sales
        sales_lift_pct = min(20, (endorsement.deal_value / 1_000_000))
        
        # Value created (simplified)
        value_created = market_cap * (sales_lift_pct / 100)
        
        roi = ((value_created - endorsement.deal_value) / endorsement.deal_value * 100) if endorsement.deal_value > 0 else 0
        
        return {
            "estimated_sales_lift_pct": round(sales_lift_pct, 1),
            "estimated_value_created": round(value_created, 0),
            "deal_cost": endorsement.deal_value,
            "roi_pct": round(roi, 1),
            "rating": "EXCELLENT" if roi > 200 else "GOOD" if roi > 100 else "FAIR" if roi > 0 else "POOR"
        }
    
    def compare_endorsements(self, endorsements: List[Endorsement], 
                            market_caps: Dict[str, float]) -> List[Dict]:
        """Compare multiple endorsements"""
        compared = []
        
        for end in endorsements:
            mc = market_caps.get(end.ticker, 1_000_000_000)
            analysis = self.calculate_impact(end, mc)
            compared.append(analysis)
        
        return sorted(compared, key=lambda x: x["expected_initial_impact_pct"], reverse=True)
