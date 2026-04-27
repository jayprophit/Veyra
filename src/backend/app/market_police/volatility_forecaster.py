"""Volatility Forecaster - Predict volatility regimes"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import statistics

@dataclass
class VolatilityReading:
    timestamp: datetime
    realized_vol: float
    implied_vol: float
    vix: float
    vvix: float  # VIX of VIX

class VolatilityForecaster:
    """Forecast volatility regimes"""
    
    def __init__(self):
        self.readings: List[VolatilityReading] = []
    
    def add_reading(self, reading: VolatilityReading):
        self.readings.append(reading)
        # Keep last 100
        self.readings = self.readings[-100:]
    
    def forecast_volatility(self, days_ahead: int = 5) -> Dict:
        """Forecast volatility for next N days"""
        if len(self.readings) < 10:
            return {"error": "Insufficient data"}
        
        recent = self.readings[-10:]
        
        # Current levels
        avg_realized = statistics.mean([r.realized_vol for r in recent])
        avg_implied = statistics.mean([r.implied_vol for r in recent])
        avg_vix = statistics.mean([r.vix for r in recent])
        
        # Trend analysis
        first_half = self.readings[-10:-5]
        second_half = self.readings[-5:]
        
        vix_trend = statistics.mean([r.vix for r in second_half]) - statistics.mean([r.vix for r in first_half])
        
        # Forecast based on trend
        if vix_trend > 5:
            forecast_change = "increasing"
            forecast_vol = avg_vix * 1.2
        elif vix_trend < -5:
            forecast_change = "decreasing"
            forecast_vol = avg_vix * 0.85
        else:
            forecast_change = "stable"
            forecast_vol = avg_vix
        
        # Volatility of volatility (VVIX indicates uncertainty)
        recent_vvix = statistics.mean([r.vvix for r in recent])
        uncertainty = "HIGH" if recent_vvix > 120 else "MEDIUM" if recent_vvix > 100 else "LOW"
        
        return {
            "current_vix": round(avg_vix, 2),
            "forecast_vix": round(forecast_vol, 2),
            "forecast_days": days_ahead,
            "trend": forecast_change,
            "confidence": uncertainty,
            "realized_vs_implied": "BACKWARDATION" if avg_implied > avg_realized * 1.1 else "CONTANGO",
            "trading_implication": self._trading_implication(forecast_change, uncertainty)
        }
    
    def _trading_implication(self, trend: str, uncertainty: str) -> str:
        """Generate trading implication"""
        if trend == "increasing" and uncertainty == "HIGH":
            return "Reduce position size, increase cash"
        elif trend == "increasing":
            return "Hedge with VIX calls or SPY puts"
        elif trend == "decreasing" and uncertainty == "LOW":
            return "Good time for long positions"
        else:
            return "Normal operations"
    
    def detect_vol_regime_change(self) -> Dict:
        """Detect regime change in volatility"""
        if len(self.readings) < 30:
            return {"error": "Need 30+ readings"}
        
        old_regime = self.readings[-30:-15]
        new_regime = self.readings[-15:]
        
        old_vix = statistics.mean([r.vix for r in old_regime])
        new_vix = statistics.mean([r.vix for r in new_regime])
        
        change_pct = (new_vix - old_vix) / old_vix * 100
        
        if abs(change_pct) > 30:
            regime = "HIGH_VOL" if new_vix > old_vix else "LOW_VOL"
            return {
                "regime_change": True,
                "from_regime": "LOW" if new_vix > old_vix else "HIGH",
                "to_regime": regime,
                "change_pct": round(change_pct, 1),
                "implication": "Adjust strategies for new regime"
            }
        
        return {"regime_change": False, "current_regime": "STABLE"}
    
    def get_vol_percentile(self, lookback_days: int = 252) -> Dict:
        """Get current volatility percentile"""
        if len(self.readings) < lookback_days:
            lookback_days = len(self.readings)
        
        history = self.readings[-lookback_days:]
        current = self.readings[-1].vix if self.readings else 20
        
        vix_values = [r.vix for r in history]
        vix_values.sort()
        
        # Find percentile
        below_current = sum(1 for v in vix_values if v < current)
        percentile = (below_current / len(vix_values)) * 100
        
        return {
            "current_vix": current,
            "percentile": round(percentile, 1),
            "interpretation": "HIGH" if percentile > 80 else "LOW" if percentile < 20 else "NORMAL",
            "historical_range": {"min": min(vix_values), "max": max(vix_values)}
        }
