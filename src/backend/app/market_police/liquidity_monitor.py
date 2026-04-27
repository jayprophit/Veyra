"""Liquidity Monitor - Track market liquidity stress"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LiquidityMetrics:
    timestamp: datetime
    bid_ask_spread_pct: float
    market_depth: int
    volume: float
    turnover: float
    hui_heubel_ratio: float

class LiquidityMonitor:
    """Monitor market liquidity and detect stress"""
    
    def __init__(self):
        self.metrics_history: List[LiquidityMetrics] = []
        self.stress_thresholds = {
            "spread": 0.5,      # 0.5% spread
            "depth": 1000,      # 1000 contracts/shares
            "turnover": 0.01    # 1% daily turnover
        }
    
    def add_metrics(self, metrics: LiquidityMetrics):
        self.metrics_history.append(metrics)
        self.metrics_history = self.metrics_history[-100:]  # Keep last 100
    
    def assess_liquidity_stress(self, metrics: LiquidityMetrics) -> Dict:
        """Assess current liquidity stress"""
        stress_scores = {}
        
        # Bid-ask spread stress
        if metrics.bid_ask_spread_pct > 1.0:
            stress_scores["spread"] = 40
        elif metrics.bid_ask_spread_pct > 0.5:
            stress_scores["spread"] = 25
        elif metrics.bid_ask_spread_pct > 0.2:
            stress_scores["spread"] = 10
        else:
            stress_scores["spread"] = 0
        
        # Market depth stress
        if metrics.market_depth < 500:
            stress_scores["depth"] = 35
        elif metrics.market_depth < 1000:
            stress_scores["depth"] = 20
        elif metrics.market_depth < 2000:
            stress_scores["depth"] = 10
        else:
            stress_scores["depth"] = 0
        
        # Turnover stress (lower = more stress)
        if metrics.turnover < 0.005:
            stress_scores["turnover"] = 25
        elif metrics.turnover < 0.01:
            stress_scores["turnover"] = 15
        else:
            stress_scores["turnover"] = 0
        
        # Hui-Heubel ratio (liquidity measure)
        if metrics.hui_heubel_ratio > 100:
            stress_scores["hui_heubel"] = 20
        elif metrics.hui_heubel_ratio > 50:
            stress_scores["hui_heubel"] = 10
        else:
            stress_scores["hui_heubel"] = 0
        
        total_stress = sum(stress_scores.values())
        
        # Determine stress level
        if total_stress >= 80:
            level = "CRITICAL"
        elif total_stress >= 60:
            level = "SEVERE"
        elif total_stress >= 40:
            level = "HIGH"
        elif total_stress >= 20:
            level = "MODERATE"
        else:
            level = "NORMAL"
        
        return {
            "stress_level": level,
            "stress_score": total_stress,
            "components": stress_scores,
            "timestamp": metrics.timestamp.isoformat(),
            "warning": level in ["HIGH", "SEVERE", "CRITICAL"],
            "recommendation": self._liquidity_recommendation(level)
        }
    
    def _liquidity_recommendation(self, level: str) -> str:
        """Get recommendation based on liquidity"""
        recs = {
            "NORMAL": "Normal trading conditions",
            "MODERATE": "Use limit orders, avoid market orders",
            "HIGH": "Reduce position sizes, wider stops",
            "SEVERE": "Avoid new entries, exit large positions gradually",
            "CRITICAL": "Emergency exit only - expect slippage"
        }
        return recs.get(level, "Unknown")
    
    def detect_flash_crash_conditions(self, recent_metrics: List[LiquidityMetrics]) -> Dict:
        """Detect conditions that could lead to flash crash"""
        if len(recent_metrics) < 5:
            return {"error": "Insufficient data"}
        
        # Check for rapid deterioration
        spreads = [m.bid_ask_spread_pct for m in recent_metrics]
        depths = [m.market_depth for m in recent_metrics]
        
        spread_trend = (spreads[-1] - spreads[0]) / spreads[0] if spreads[0] > 0 else 0
        depth_trend = (depths[0] - depths[-1]) / depths[0] if depths[0] > 0 else 0
        
        flash_crash_risk = 0
        
        # Spreads widening rapidly
        if spread_trend > 1.0:  # Doubled
            flash_crash_risk += 40
        
        # Depth evaporating
        if depth_trend > 0.5:  # Lost 50%
            flash_crash_risk += 40
        
        # Both happening together
        if spread_trend > 0.5 and depth_trend > 0.3:
            flash_crash_risk += 20
        
        return {
            "flash_crash_risk_score": min(100, flash_crash_risk),
            "risk_level": "EXTREME" if flash_crash_risk > 80 else "HIGH" if flash_crash_risk > 60 else "MODERATE" if flash_crash_risk > 40 else "LOW",
            "spread_trend_pct": round(spread_trend * 100, 1),
            "depth_trend_pct": round(depth_trend * 100, 1),
            "conditions": self._flash_crash_conditions(flash_crash_risk)
        }
    
    def _flash_crash_conditions(self, risk: int) -> List[str]:
        """Describe flash crash conditions"""
        if risk > 80:
            return ["Spreads widening rapidly", "Market depth evaporating", "CASCADE RISK"]
        elif risk > 60:
            return ["Significant liquidity stress", "Use extreme caution"]
        elif risk > 40:
            return ["Declining liquidity", "Reduce exposure"]
        return ["Normal conditions"]
    
    def get_liquidity_ranking(self, assets: List[Dict]) -> List[Dict]:
        """Rank assets by liquidity score"""
        ranked = []
        
        for asset in assets:
            # Calculate liquidity score
            spread_score = max(0, 100 - asset.get("spread_pct", 0) * 20)
            depth_score = min(100, asset.get("depth", 0) / 100)
            volume_score = min(100, asset.get("volume", 0) / 1000000)
            
            total_score = (spread_score + depth_score + volume_score) / 3
            
            ranked.append({
                "symbol": asset.get("symbol"),
                "liquidity_score": round(total_score, 1),
                "tier": "EXCELLENT" if total_score > 80 else "GOOD" if total_score > 60 else "FAIR" if total_score > 40 else "POOR",
                "components": {
                    "spread": round(spread_score, 1),
                    "depth": round(depth_score, 1),
                    "volume": round(volume_score, 1)
                }
            })
        
        return sorted(ranked, key=lambda x: x["liquidity_score"], reverse=True)
