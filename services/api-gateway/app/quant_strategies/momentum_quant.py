"""Quantitative Momentum - Factor-based momentum strategies"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import statistics

@dataclass
class MomentumScore:
    symbol: str
    price_momentum: float
    earnings_momentum: float
    volume_momentum: float
    relative_strength: float
    composite_score: float

class QuantitativeMomentum:
    """Multi-factor quantitative momentum strategy"""
    
    def __init__(self):
        self.lookback_months = [3, 6, 12]  # Multiple timeframes
        self.weights = {
            "price_3m": 0.3,
            "price_6m": 0.2,
            "price_12m": 0.2,
            "earnings": 0.2,
            "volume": 0.1
        }
    
    def calculate_price_momentum(self, prices: List[float]) -> Dict:
        """Calculate price momentum across timeframes"""
        if len(prices) < 252:  # Need ~1 year of data
            return {"error": "Insufficient price history"}
        
        current = prices[-1]
        
        # Calculate returns
        ret_3m = (current - prices[-63]) / prices[-63] if len(prices) >= 63 else 0
        ret_6m = (current - prices[-126]) / prices[-126] if len(prices) >= 126 else 0
        ret_12m = (current - prices[-252]) / prices[-252] if len(prices) >= 252 else 0
        
        # Skip most recent month (reversal effect)
        ret_ex_recent = (prices[-21] - prices[-252]) / prices[-252] if len(prices) >= 252 else 0
        
        return {
            "return_3m": round(ret_3m * 100, 2),
            "return_6m": round(ret_6m * 100, 2),
            "return_12m": round(ret_12m * 100, 2),
            "return_ex_recent": round(ret_ex_recent * 100, 2),
            "trend_consistency": self._check_trend_consistency(ret_3m, ret_6m, ret_12m)
        }
    
    def _check_trend_consistency(self, ret_3m: float, ret_6m: float, 
                                  ret_12m: float) -> str:
        """Check if momentum is consistent across timeframes"""
        positive_count = sum([ret_3m > 0, ret_6m > 0, ret_12m > 0])
        
        if positive_count == 3:
            return "STRONG_UP"
        elif positive_count == 0:
            return "STRONG_DOWN"
        elif ret_3m > 0 and ret_6m > 0:
            return "ACCELERATING"
        elif ret_3m < 0 and ret_12m > 0:
            return "DECELERATING"
        return "MIXED"
    
    def calculate_earnings_momentum(self, earnings_history: List[float]) -> float:
        """Calculate earnings momentum from surprise history"""
        if len(earnings_history) < 4:
            return 0
        
        # Recent earnings surprises
        recent = earnings_history[-4:]
        
        # Weight recent quarters more
        weights = [0.4, 0.3, 0.2, 0.1]
        weighted_surprise = sum(e * w for e, w in zip(recent, weights))
        
        return weighted_surprise
    
    def calculate_volume_momentum(self, prices: List[float], 
                                 volumes: List[float]) -> float:
        """Calculate volume-confirmed momentum"""
        if len(prices) != len(volumes) or len(prices) < 20:
            return 0
        
        # Price change
        price_change = (prices[-1] - prices[-20]) / prices[-20]
        
        # Volume trend
        recent_vol = statistics.mean(volumes[-5:])
        avg_vol = statistics.mean(volumes[-20:])
        
        volume_surge = recent_vol / avg_vol if avg_vol > 0 else 1
        
        # Volume confirms if price up + volume up, or price down + volume down
        if price_change > 0 and volume_surge > 1.2:
            return price_change * volume_surge  # Confirmed up
        elif price_change < 0 and volume_surge > 1.2:
            return price_change * volume_surge  # Confirmed down
        else:
            return price_change * 0.5  # Weak confirmation
    
    def calculate_relative_strength(self, symbol_returns: List[float],
                                   benchmark_returns: List[float]) -> float:
        """Calculate relative strength vs benchmark"""
        if len(symbol_returns) != len(benchmark_returns) or len(symbol_returns) == 0:
            return 1.0
        
        # RS = symbol return / benchmark return
        symbol_ret = statistics.mean(symbol_returns)
        bench_ret = statistics.mean(benchmark_returns)
        
        if bench_ret == 0:
            return 1.0 if symbol_ret > 0 else 0.5
        
        rs = (1 + symbol_ret) / (1 + bench_ret)
        return rs
    
    def generate_composite_score(self, symbol: str,
                                price_data: List[float],
                                earnings_data: List[float] = None,
                                volume_data: List[float] = None,
                                benchmark_returns: List[float] = None) -> MomentumScore:
        """Generate composite momentum score"""
        
        # Price momentum
        price_mom = self.calculate_price_momentum(price_data)
        if "error" in price_mom:
            price_mom_score = 0
        else:
            price_mom_score = (
                price_mom["return_3m"] * self.weights["price_3m"] +
                price_mom["return_6m"] * self.weights["price_6m"] +
                price_mom["return_12m"] * self.weights["price_12m"]
            )
        
        # Earnings momentum
        earn_mom = self.calculate_earnings_momentum(earnings_data) if earnings_data else 0
        
        # Volume momentum
        vol_mom = self.calculate_volume_momentum(price_data, volume_data) if volume_data else 0
        
        # Relative strength
        rs = self.calculate_relative_strength(
            [(price_data[i] - price_data[i-1]) / price_data[i-1] for i in range(1, len(price_data))],
            benchmark_returns
        ) if benchmark_returns else 1.0
        
        # Composite score (0-100)
        composite = (
            abs(price_mom_score) * 0.5 +
            abs(earn_mom) * 25 +
            abs(vol_mom) * 25 +
            (rs - 1) * 50  # RS contribution
        )
        
        return MomentumScore(
            symbol=symbol,
            price_momentum=round(price_mom_score, 2),
            earnings_momentum=round(earn_mom, 2),
            volume_momentum=round(vol_mom * 100, 2),
            relative_strength=round(rs, 2),
            composite_score=round(min(100, max(0, composite)), 2)
        )
    
    def rank_universe(self, scores: List[MomentumScore]) -> List[Dict]:
        """Rank universe by momentum score"""
        ranked = sorted(scores, key=lambda x: x.composite_score, reverse=True)
        
        return [
            {
                "symbol": s.symbol,
                "composite_score": s.composite_score,
                "price_momentum": s.price_momentum,
                "earnings_momentum": s.earnings_momentum,
                "relative_strength": s.relative_strength,
                "tier": "LEADER" if s.composite_score > 70 else "CONTENDER" if s.composite_score > 50 else "LAGGARD",
                "recommendation": "STRONG_BUY" if s.composite_score > 75 else "BUY" if s.composite_score > 60 else "HOLD"
            }
            for s in ranked
        ]
    
    def detect_momentum_reversal(self, recent_scores: List[MomentumScore]) -> List[Dict]:
        """Detect stocks losing momentum"""
        reversals = []
        
        for score in recent_scores:
            # Declining momentum indicators
            if score.price_momentum < -10 and score.composite_score < 40:
                reversals.append({
                    "symbol": score.symbol,
                    "signal": "MOMENTUM_REVERSAL",
                    "composite_score": score.composite_score,
                    "price_momentum": score.price_momentum,
                    "action": "REDUCE" if score.composite_score > 30 else "EXIT"
                })
        
        return reversals
