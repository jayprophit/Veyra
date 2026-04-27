"""Signal Generator - Generate trading signals from multiple factors"""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class SignalStrength(Enum):
    STRONG_BUY = 5
    BUY = 4
    WEAK_BUY = 3
    HOLD = 2
    WEAK_SELL = 1
    SELL = 0
    STRONG_SELL = -1

@dataclass
class FactorSignal:
    factor_name: str
    weight: float
    raw_score: float  # -1 to 1
    signal: SignalStrength

class SignalGenerator:
    """Generate composite trading signals from multiple factors"""
    
    def __init__(self):
        self.factors: Dict[str, float] = {
            "momentum": 0.20,
            "value": 0.20,
            "quality": 0.15,
            "growth": 0.15,
            "sentiment": 0.15,
            "technical": 0.15
        }
    
    def generate_composite_signal(self, factor_signals: List[FactorSignal]) -> Dict:
        """Generate composite signal from multiple factors"""
        if not factor_signals:
            return {"error": "No factor signals provided"}
        
        # Calculate weighted composite score
        weighted_sum = 0
        total_weight = 0
        
        for fs in factor_signals:
            factor_weight = self.factors.get(fs.factor_name, 0.1)
            weighted_sum += fs.raw_score * factor_weight
            total_weight += factor_weight
        
        composite_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Convert to signal
        if composite_score > 0.6:
            signal = SignalStrength.STRONG_BUY
        elif composite_score > 0.3:
            signal = SignalStrength.BUY
        elif composite_score > 0.1:
            signal = SignalStrength.WEAK_BUY
        elif composite_score > -0.1:
            signal = SignalStrength.HOLD
        elif composite_score > -0.3:
            signal = SignalStrength.WEAK_SELL
        elif composite_score > -0.6:
            signal = SignalStrength.SELL
        else:
            signal = SignalStrength.STRONG_SELL
        
        # Calculate confidence based on factor agreement
        scores = [fs.raw_score for fs in factor_signals]
        score_variance = sum((s - composite_score) ** 2 for s in scores) / len(scores)
        confidence = max(0, min(100, 100 - (score_variance * 200)))
        
        # Identify strongest contributing factors
        sorted_factors = sorted(factor_signals, key=lambda x: abs(x.raw_score) * x.weight, reverse=True)
        top_factors = [f.factor_name for f in sorted_factors[:3]]
        
        return {
            "composite_score": round(composite_score, 3),
            "signal": signal.name,
            "signal_value": signal.value,
            "confidence": round(confidence, 1),
            "interpretation": self._interpret_signal(signal),
            "num_factors": len(factor_signals),
            "top_contributing_factors": top_factors,
            "factor_breakdown": [
                {
                    "factor": fs.factor_name,
                    "score": round(fs.raw_score, 3),
                    "weight": self.factors.get(fs.factor_name, 0.1),
                    "contribution": round(fs.raw_score * self.factors.get(fs.factor_name, 0.1), 3)
                }
                for fs in factor_signals
            ]
        }
    
    def _interpret_signal(self, signal: SignalStrength) -> str:
        """Interpret signal strength"""
        interpretations = {
            SignalStrength.STRONG_BUY: "Strong conviction to buy - multiple factors aligned",
            SignalStrength.BUY: "Clear buy signal - factors support entry",
            SignalStrength.WEAK_BUY: "Tentative buy - limited factor support",
            SignalStrength.HOLD: "Neutral - no clear directional bias",
            SignalStrength.WEAK_SELL: "Tentative sell - limited factor support",
            SignalStrength.SELL: "Clear sell signal - factors suggest exit",
            SignalStrength.STRONG_SELL: "Strong conviction to sell - multiple factors aligned"
        }
        return interpretations.get(signal, "Unknown signal")
    
    def screen_universe(self, universe_data: List[Dict]) -> List[Dict]:
        """Screen universe and generate signals for all stocks"""
        results = []
        
        for stock_data in universe_data:
            symbol = stock_data.get("symbol")
            
            # Build factor signals from data
            factor_signals = []
            
            # Momentum factor
            if "momentum_12m" in stock_data:
                mom_score = max(-1, min(1, stock_data["momentum_12m"] / 0.5))
                factor_signals.append(FactorSignal("momentum", 0.20, mom_score, 
                    SignalStrength.STRONG_BUY if mom_score > 0.5 else SignalStrength.BUY if mom_score > 0.2 else SignalStrength.HOLD))
            
            # Value factor
            if "pe_ratio" in stock_data:
                pe = stock_data["pe_ratio"]
                value_score = 1 if pe < 15 else 0.5 if pe < 20 else 0 if pe < 30 else -0.5
                factor_signals.append(FactorSignal("value", 0.20, value_score,
                    SignalStrength.BUY if value_score > 0 else SignalStrength.HOLD))
            
            # Quality factor
            if "roe" in stock_data:
                roe = stock_data["roe"]
                quality_score = 1 if roe > 0.20 else 0.5 if roe > 0.15 else 0 if roe > 0.10 else -0.5
                factor_signals.append(FactorSignal("quality", 0.15, quality_score,
                    SignalStrength.BUY if quality_score > 0 else SignalStrength.HOLD))
            
            # Generate composite
            if factor_signals:
                composite = self.generate_composite_signal(factor_signals)
                results.append({
                    "symbol": symbol,
                    "signal": composite["signal"],
                    "score": composite["composite_score"],
                    "confidence": composite["confidence"]
                })
        
        # Sort by composite score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def get_top_picks(self, universe_data: List[Dict], n: int = 10) -> Dict:
        """Get top buy and sell picks"""
        all_signals = self.screen_universe(universe_data)
        
        buys = [s for s in all_signals if "BUY" in s["signal"]]
        sells = [s for s in all_signals if "SELL" in s["signal"]]
        
        return {
            "top_longs": buys[:n],
            "top_shorts": sells[:n],
            "total_bullish": len(buys),
            "total_bearish": len(sells),
            "neutral_count": len(all_signals) - len(buys) - len(sells),
            "market_bias": "BULLISH" if len(buys) > len(sells) * 1.5 else "BEARISH" if len(sells) > len(buys) * 1.5 else "NEUTRAL"
        }
