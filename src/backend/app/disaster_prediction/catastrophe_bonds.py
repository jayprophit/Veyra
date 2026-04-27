"""Catastrophe Bond Analyzer"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class CatBond:
    name: str
    coupon: float
    peril: str
    region: str
    trigger_level: float
    attachment: Decimal
    exhaustion: Decimal

class CatastropheBondAnalyzer:
    """Analyze catastrophe bond investments"""
    
    def __init__(self):
        self.peril_types = ["hurricane", "earthquake", "wildfire", "flood", "pandemic"]
    
    def analyze_opportunity(self, bond: CatBond, risk_prob: float) -> Dict:
        """Analyze cat bond investment"""
        # Expected loss calculation
        expected_loss = risk_prob * float(bond.exhaustion - bond.attachment)
        
        # Risk-adjusted return
        risk_adj_return = (bond.coupon - expected_loss) / max(risk_prob, 0.01)
        
        # Trigger probability
        trigger_prob = risk_prob * 100
        
        return {
            "bond": bond.name,
            "expected_yield": bond.coupon,
            "trigger_probability": round(trigger_prob, 2),
            "expected_loss": round(expected_loss, 2),
            "risk_adjusted_return": round(risk_adj_return, 2),
            "rating": self._rate_opportunity(bond.coupon, expected_loss, trigger_prob),
            "recommendation": self._recommend(bond, risk_prob)
        }
    
    def _rate_opportunity(self, coupon: float, expected_loss: float, trigger_prob: float) -> str:
        """Rate the investment opportunity"""
        margin = coupon - expected_loss
        if margin > 5 and trigger_prob < 10:
            return "EXCELLENT"
        elif margin > 3 and trigger_prob < 15:
            return "GOOD"
        elif margin > 1:
            return "FAIR"
        return "POOR"
    
    def _recommend(self, bond: CatBond, risk_prob: float) -> str:
        """Generate recommendation"""
        if risk_prob < 0.05 and bond.coupon > 5:
            return "BUY - Low risk, attractive yield"
        elif risk_prob < 0.1 and bond.coupon > 7:
            return "CONSIDER - Moderate risk, high yield"
        elif risk_prob > 0.2:
            return "AVOID - High trigger risk"
        return "HOLD - Fair pricing"
    
    def compare_bonds(self, bonds: List[CatBond], risks: Dict[str, float]) -> List[Dict]:
        """Compare multiple cat bond opportunities"""
        analyzed = []
        
        for bond in bonds:
            risk = risks.get(bond.peril, 0.1)
            analysis = self.analyze_opportunity(bond, risk)
            analyzed.append(analysis)
        
        return sorted(analyzed, key=lambda x: x["risk_adjusted_return"], reverse=True)
    
    def get_market_summary(self) -> Dict:
        """Get cat bond market summary"""
        return {
            "market_size_usd_billions": 45,
            "avg_coupon": 7.5,
            "avg_trigger_prob": 8.2,
            "demand_trend": "increasing",
            "primary_perils": ["hurricane", "earthquake"],
            "liquidity": "moderate"
        }
