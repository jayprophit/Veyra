"""Cat Bonds - Catastrophe bond analysis"""
from typing import Dict

class CatBonds:
    """Analyze catastrophe bond investments"""
    
    def cat_bond_pricing(self, principal: float,
                        coupon: float,
                        attachment_prob: float,
                        expected_loss: float) -> Dict:
        """Price cat bond with risk metrics"""
        spread = expected_loss * 100  # Convert to basis points
        multiple = coupon / expected_loss if expected_loss > 0 else 0
        
        return {
            "principal": principal,
            "coupon_rate": coupon,
            "attachment_probability": attachment_prob,
            "expected_loss": expected_loss,
            "spread_multiple": round(multiple, 2),
            "annual_yield": f"{coupon * 100:.2f}%",
            "risk_rating": "high" if attachment_prob > 0.1 else "moderate" if attachment_prob > 0.05 else "low"
        }
    
    def loss_distribution(self, event_probabilities: Dict[str, float],
                         loss_amounts: Dict[str, float]) -> Dict:
        """Calculate expected loss distribution"""
        expected_loss = sum(p * loss_amounts.get(e, 0) for e, p in event_probabilities.items())
        
        return {
            "expected_annual_loss": round(expected_loss, 0),
            "covered_events": list(event_probabilities.keys()),
            "worst_case": max(loss_amounts.values()) if loss_amounts else 0,
            "stress_loss": round(expected_loss * 3, 0)  # 3x stress
        }
