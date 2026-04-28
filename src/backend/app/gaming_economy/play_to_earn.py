"""Play to Earn - P2E gaming economics"""
from typing import Dict

class PlayToEarn:
    """Analyze play-to-earn economics"""
    
    def calculate_yield(self, entry_cost: float, daily_earnings: float, days: int) -> Dict:
        """Calculate P2E yield"""
        total_earned = daily_earnings * days
        roi = (total_earned - entry_cost) / entry_cost if entry_cost > 0 else 0
        
        return {
            "entry_cost": entry_cost,
            "daily_earnings": daily_earnings,
            "period_days": days,
            "total_earned": total_earned,
            "roi": round(roi * 100, 1),
            "viable": roi > 0.2
        }
