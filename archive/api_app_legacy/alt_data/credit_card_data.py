"""Credit Card Data - Consumer spending analytics"""
from typing import Dict

class CreditCardData:
    """Analyze credit card spending patterns"""
    
    def spending_velocity(self, current_month: float,
                         previous_month: float,
                         year_ago: float) -> Dict:
        """Calculate spending velocity trends"""
        mom_change = (current_month - previous_month) / previous_month * 100 if previous_month > 0 else 0
        yoy_change = (current_month - year_ago) / year_ago * 100 if year_ago > 0 else 0
        
        return {
            "current_month": current_month,
            "mom_change_percent": round(mom_change, 1),
            "yoy_change_percent": round(yoy_change, 1),
            "trend": "accelerating" if mom_change > 0 and yoy_change > 0 else "decelerating" if mom_change < 0 else "mixed"
        }
    
    def category_breakdown(self, spending: Dict[str, float]) -> Dict:
        """Analyze spending by category"""
        total = sum(spending.values())
        breakdown = {k: round(v / total * 100, 1) for k, v in spending.items()} if total > 0 else {}
        
        # Identify growth categories (would need historical data)
        top_category = max(spending.items(), key=lambda x: x[1])[0] if spending else None
        
        return {
            "total_spending": total,
            "category_breakdown": breakdown,
            "top_category": top_category,
            "discretionary_pct": round((spending.get("entertainment", 0) + spending.get("travel", 0)) / total * 100, 1) if total > 0 else 0
        }
    
    def default_risk_indicator(self, credit_utilization: float,
                               missed_payments: int,
                               credit_score_change: float) -> Dict:
        """Predict default risk from credit behavior"""
        risk_score = (credit_utilization * 50) + (missed_payments * 20) + abs(min(0, credit_score_change))
        
        if risk_score > 80:
            risk_level = "high"
        elif risk_score > 50:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "credit_utilization": credit_utilization,
            "warning": risk_level == "high"
        }
