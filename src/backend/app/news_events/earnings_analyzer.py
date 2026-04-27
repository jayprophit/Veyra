"""Earnings Analyzer - Predict and trade earnings reactions"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class EarningsSurprise(Enum):
    MAJOR_BEAT = "major_beat"
    BEAT = "beat"
    INLINE = "inline"
    MISS = "miss"
    MAJOR_MISS = "major_miss"

@dataclass
class EarningsResult:
    ticker: str
    report_date: datetime
    eps_estimate: float
    eps_actual: float
    revenue_estimate: float
    revenue_actual: float
    guidance: str  # RAISED, LOWERED, UNCHANGED

class EarningsAnalyzer:
    """Analyze earnings and predict price reactions"""
    
    def __init__(self):
        self.history: Dict[str, List[EarningsResult]] = {}
        self.reaction_patterns = self._load_reaction_patterns()
    
    def _load_reaction_patterns(self) -> Dict:
        """Load historical reaction patterns"""
        return {
            "major_beat": {"avg_move": 8.5, "next_day_reversal": 0.3},
            "beat": {"avg_move": 4.2, "next_day_reversal": 0.25},
            "inline": {"avg_move": 0.5, "next_day_reversal": 0.5},
            "miss": {"avg_move": -5.8, "next_day_reversal": 0.35},
            "major_miss": {"avg_move": -12.3, "next_day_reversal": 0.4}
        }
    
    def categorize_surprise(self, result: EarningsResult) -> EarningsSurprise:
        """Categorize earnings surprise"""
        eps_surprise = (result.eps_actual - result.eps_estimate) / abs(result.eps_estimate) * 100 if result.eps_estimate != 0 else 0
        
        if eps_surprise > 15:
            return EarningsSurprise.MAJOR_BEAT
        elif eps_surprise > 5:
            return EarningsSurprise.BEAT
        elif eps_surprise > -5:
            return EarningsSurprise.INLINE
        elif eps_surprise > -15:
            return EarningsSurprise.MISS
        else:
            return EarningsSurprise.MAJOR_MISS
    
    def predict_reaction(self, result: EarningsResult, 
                        historical_volatility: float) -> Dict:
        """Predict price reaction to earnings"""
        surprise = self.categorize_surprise(result)
        pattern = self.reaction_patterns.get(surprise.value, {})
        
        base_move = pattern.get("avg_move", 0)
        
        # Adjust for guidance
        guidance_mult = {
            "RAISED": 1.3,
            "UNCHANGED": 1.0,
            "LOWERED": 0.7
        }.get(result.guidance, 1.0)
        
        expected_move = base_move * guidance_mult
        
        # Adjust for historical volatility
        if historical_volatility > 50:
            volatility_adj = 1.3
        elif historical_volatility > 30:
            volatility_adj = 1.1
        else:
            volatility_adj = 0.9
        
        adjusted_move = expected_move * volatility_adj
        
        return {
            "ticker": result.ticker,
            "surprise_category": surprise.value,
            "eps_surprise_pct": round((result.eps_actual - result.eps_estimate) / result.eps_estimate * 100, 1) if result.eps_estimate else 0,
            "revenue_surprise_pct": round((result.revenue_actual - result.revenue_estimate) / result.revenue_estimate * 100, 1) if result.revenue_estimate else 0,
            "expected_move_pct": round(adjusted_move, 1),
            "direction": "UP" if adjusted_move > 0 else "DOWN",
            "confidence": "HIGH" if abs(adjusted_move) > 5 else "MEDIUM",
            "guidance_impact": result.guidance,
            "next_day_reversal_prob": pattern.get("next_day_reversal", 0.3)
        }
    
    def get_trading_strategy(self, prediction: Dict, 
                           current_price: float,
                           risk_tolerance: str = "MODERATE") -> Dict:
        """Generate trading strategy for earnings"""
        expected_move = prediction["expected_move_pct"]
        direction = prediction["direction"]
        
        if risk_tolerance == "CONSERVATIVE":
            # Play the aftermath, not the event
            return {
                "strategy": "POST_EARNINGS_MOMENTUM",
                "action": "WAIT",
                "entry": f"After direction confirmed (30min post-open)",
                "target": round(expected_move * 0.6, 1),
                "stop": round(-expected_move * 0.3, 1) if expected_move > 0 else round(-expected_move * 0.3, 1),
                "timeframe": "1-3 days"
            }
        
        elif risk_tolerance == "AGGRESSIVE":
            # Trade the initial move
            if direction == "UP":
                return {
                    "strategy": "PREMIUM_COLLECTOR",
                    "action": "SELL_PUTS",
                    "strike": round(current_price * 0.95, 2),
                    "credit_target": "2-3%",
                    "risk": "Assignment if major miss"
                }
            else:
                return {
                    "strategy": "PREMIUM_COLLECTOR",
                    "action": "SELL_CALLS",
                    "strike": round(current_price * 1.05, 2),
                    "credit_target": "2-3%",
                    "risk": "Assignment if major beat"
                }
        
        else:  # MODERATE
            if abs(expected_move) > 8:
                return {
                    "strategy": "STRADDLE",
                    "action": "BUY_STRADDLE",
                    "rationale": "Large expected move, direction uncertain",
                    "breakeven_up": round(current_price * (1 + abs(expected_move)/100), 2),
                    "breakeven_down": round(current_price * (1 - abs(expected_move)/100), 2),
                    "max_loss": "Premium paid"
                }
            else:
                return {
                    "strategy": "POST_EARNINGS_DRIFT",
                    "action": f"BUY_{direction}",
                    "entry": "Next day open",
                    "target": round(expected_move * 0.5, 1),
                    "holding_period": "2-5 days"
                }
    
    def analyze_earnings_season(self, results: List[EarningsResult]) -> Dict:
        """Analyze patterns across earnings season"""
        beats = sum(1 for r in results if self.categorize_surprise(r) in [EarningsSurprise.BEAT, EarningsSurprise.MAJOR_BEAT])
        misses = sum(1 for r in results if self.categorize_surprise(r) in [EarningsSurprise.MISS, EarningsSurprise.MAJOR_MISS])
        
        beat_rate = beats / len(results) * 100 if results else 0
        
        # Sector performance
        sector_performance = {}
        
        return {
            "total_reports": len(results),
            "beat_rate": round(beat_rate, 1),
            "miss_rate": round(misses / len(results) * 100, 1) if results else 0,
            "season_sentiment": "BULLISH" if beat_rate > 65 else "BEARISH" if beat_rate < 45 else "MIXED",
            "guidance_trend": self._analyze_guidance_trend(results),
            "avg_surprise_pct": round(statistics.mean([
                (r.eps_actual - r.eps_estimate) / r.eps_estimate * 100 
                for r in results if r.eps_estimate
            ]), 2) if results else 0
        }
    
    def _analyze_guidance_trend(self, results: List[EarningsResult]) -> str:
        """Analyze guidance trend across earnings season"""
        raised = sum(1 for r in results if r.guidance == "RAISED")
        lowered = sum(1 for r in results if r.guidance == "LOWERED")
        
        if raised > lowered * 1.5:
            return "STRONGLY_POSITIVE"
        elif raised > lowered:
            return "POSITIVE"
        elif lowered > raised * 1.5:
            return "STRONGLY_NEGATIVE"
        elif lowered > raised:
            return "NEGATIVE"
        return "NEUTRAL"

import statistics
