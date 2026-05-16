"""Liquidity Scorer - Score asset liquidity across dimensions"""
from typing import Dict
from dataclasses import dataclass

@dataclass
class LiquidityMetrics:
    avg_daily_volume: float
    bid_ask_spread_pct: float
    market_cap: float
    shares_outstanding: float
    float_pct: float
    institutional_ownership: float
    price_impact_1pct: float  # Price impact of 1% of ADV

class LiquidityScorer:
    """Score asset liquidity from 0-100"""
    
    def __init__(self):
        self.liquidity_thresholds = {
            "excellent": 80,
            "good": 60,
            "moderate": 40,
            "poor": 20
        }
    
    def calculate_liquidity_score(self, metrics: LiquidityMetrics) -> Dict:
        """Calculate composite liquidity score"""
        score = 50  # Base score
        
        # Volume score (max 20 points)
        if metrics.avg_daily_volume > 100e6:
            score += 20
        elif metrics.avg_daily_volume > 50e6:
            score += 15
        elif metrics.avg_daily_volume > 10e6:
            score += 10
        elif metrics.avg_daily_volume > 1e6:
            score += 5
        else:
            score -= 10
        
        # Spread score (max 20 points) - tighter = better
        if metrics.bid_ask_spread_pct < 0.05:
            score += 20
        elif metrics.bid_ask_spread_pct < 0.10:
            score += 15
        elif metrics.bid_ask_spread_pct < 0.20:
            score += 10
        elif metrics.bid_ask_spread_pct < 0.50:
            score += 5
        else:
            score -= 10
        
        # Market cap score (max 15 points)
        if metrics.market_cap > 100e9:
            score += 15
        elif metrics.market_cap > 10e9:
            score += 10
        elif metrics.market_cap > 1e9:
            score += 5
        
        # Float score (max 10 points)
        if metrics.float_pct > 0.9:
            score += 10
        elif metrics.float_pct > 0.7:
            score += 5
        elif metrics.float_pct < 0.3:
            score -= 5
        
        # Price impact score (max 15 points) - lower impact = better
        if metrics.price_impact_1pct < 0.1:
            score += 15
        elif metrics.price_impact_1pct < 0.3:
            score += 10
        elif metrics.price_impact_1pct < 0.5:
            score += 5
        else:
            score -= 5
        
        # Institutional ownership bonus (max 10 points)
        if metrics.institutional_ownership > 0.7:
            score += 10
        elif metrics.institutional_ownership > 0.5:
            score += 5
        
        final_score = max(0, min(100, score))
        
        return {
            "liquidity_score": round(final_score, 1),
            "rating": "EXCELLENT" if final_score >= 80 else "GOOD" if final_score >= 60 else "MODERATE" if final_score >= 40 else "POOR",
            "position_size_limit_pct": self._get_position_limit(final_score),
            "max_order_size_adv": self._get_max_order_size(final_score, metrics.avg_daily_volume),
            "time_to_liquidate_days": self._estimate_liquidation_time(final_score, metrics),
            "metrics_summary": {
                "daily_volume_millions": round(metrics.avg_daily_volume / 1e6, 1),
                "spread_bps": round(metrics.bid_ask_spread_pct * 100, 1),
                "market_cap_billions": round(metrics.market_cap / 1e9, 1)
            }
        }
    
    def _get_position_limit(self, score: float) -> float:
        """Get recommended position size limit"""
        if score >= 80:
            return 0.10  # 10% max
        elif score >= 60:
            return 0.07
        elif score >= 40:
            return 0.05
        else:
            return 0.03
    
    def _get_max_order_size(self, score: float, adv: float) -> float:
        """Get maximum order size as % of ADV"""
        if score >= 80:
            return 0.30  # 30% of ADV
        elif score >= 60:
            return 0.20
        elif score >= 40:
            return 0.10
        else:
            return 0.05
    
    def _estimate_liquidation_time(self, score: float, metrics: LiquidityMetrics) -> float:
        """Estimate days to liquidate full position"""
        # Assume 10% position that needs liquidation
        position_value = metrics.market_cap * 0.10
        daily_liquidation_capacity = metrics.avg_daily_volume * metrics.market_cap / metrics.shares_outstanding * 0.20
        
        if daily_liquidation_capacity == 0:
            return 999
        
        days = position_value / daily_liquidation_capacity
        
        # Adjust for liquidity score
        if score >= 80:
            days *= 0.8
        elif score < 40:
            days *= 2.0
        
        return round(days, 1)
    
    def compare_liquidity(self, assets: Dict[str, LiquidityMetrics]) -> Dict:
        """Compare liquidity across multiple assets"""
        results = []
        
        for symbol, metrics in assets.items():
            score_data = self.calculate_liquidity_score(metrics)
            results.append({
                "symbol": symbol,
                **score_data
            })
        
        results.sort(key=lambda x: x["liquidity_score"], reverse=True)
        
        return {
            "ranked_by_liquidity": results,
            "average_score": round(sum(r["liquidity_score"] for r in results) / len(results), 1) if results else 0,
            "least_liquid": results[-1]["symbol"] if results else None,
            "liquidity_concentration_risk": "HIGH" if results and results[-1]["liquidity_score"] < 30 else "LOW"
        }
