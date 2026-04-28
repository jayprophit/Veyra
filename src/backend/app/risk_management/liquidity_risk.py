"""Liquidity Risk - Liquidity risk assessment"""
from typing import Dict

class LiquidityRisk:
    """Assess liquidity risk in portfolios"""
    
    def liquidity_score(self, avg_daily_volume: float,
                       position_size: float,
                       days_to_exit: int) -> Dict:
        """Calculate liquidity score for position"""
        if avg_daily_volume > 0:
            participation_rate = position_size / (avg_daily_volume * days_to_exit)
        else:
            participation_rate = float('inf')
        
        # Score based on participation (lower is better)
        if participation_rate < 0.1:
            score = 10  # Excellent
        elif participation_rate < 0.3:
            score = 7   # Good
        elif participation_rate < 0.5:
            score = 4   # Fair
        else:
            score = 1   # Poor
        
        return {
            "liquidity_score": score,
            "participation_rate": round(participation_rate * 100, 1),
            "days_to_exit": days_to_exit,
            "risk_level": "low" if score > 7 else "medium" if score > 4 else "high"
        }
    
    def bid_ask_impact(self, bid_ask_spread_pct: float,
                      position_value: float) -> Dict:
        """Calculate cost of bid-ask spread"""
        round_trip_cost = position_value * (bid_ask_spread_pct / 100) * 2
        
        return {
            "spread_pct": bid_ask_spread_pct,
            "entry_cost": round(position_value * (bid_ask_spread_pct / 100), 0),
            "round_trip_cost": round(round_trip_cost, 0),
            "impact": "minimal" if bid_ask_spread_pct < 0.1 else "moderate" if bid_ask_spread_pct < 0.5 else "significant"
        }
    
    def liquidity_adjusted_var(self, base_var: float,
                              liquidity_score: int) -> Dict:
        """Adjust VaR for liquidity risk"""
        # Liquidity multiplier (higher score = lower multiplier)
        multipliers = {10: 1.0, 7: 1.2, 4: 1.5, 1: 2.0}
        multiplier = multipliers.get(liquidity_score, 1.5)
        
        adjusted_var = base_var * multiplier
        
        return {
            "base_var": base_var,
            "liquidity_multiplier": multiplier,
            "liquidity_adjusted_var": round(adjusted_var, 0),
            "liquidity_premium": round((multiplier - 1) * 100, 0)
        }
