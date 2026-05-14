"""VIX Strategy - Trade VIX futures, options and related products"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class VIXSignal(Enum):
    LONG_VOLATILITY = "long_vol"
    SHORT_VOLATILITY = "short_vol"
    CONTANGO_ROLL = "contango_roll"
    BACKWARDATION_ROLL = "backwardation_roll"
    NEUTRAL = "neutral"

@dataclass
class VIXData:
    spot_vix: float
    front_month_future: float
    second_month_future: float
    vix_9d: float  # 9-day VIX (short-term)
    vix_3m: float  # 3-month VIX
    term_structure_slope: float
    timestamp: datetime

class VIXStrategy:
    """Generate VIX trading strategies"""
    
    def __init__(self):
        self.vix_history: List[VIXData] = []
        self.long_vol_threshold = 25  # Buy vol when VIX > 25
        self.short_vol_threshold = 15  # Sell vol when VIX < 15
    
    def add_data(self, data: VIXData):
        """Add VIX market data"""
        self.vix_history.append(data)
    
    def analyze_term_structure(self, data: VIXData) -> Dict:
        """Analyze VIX futures term structure"""
        spread = data.second_month_future - data.front_month_future
        spread_pct = (spread / data.front_month_future) * 100 if data.front_month_future > 0 else 0
        
        if spread > 0:
            structure = "CONTANGO"  # Futures > Spot (normal)
            roll_yield = -spread_pct  # Negative roll yield
        else:
            structure = "BACKWARDATION"  # Futures < Spot (inverted)
            roll_yield = abs(spread_pct)  # Positive roll yield
        
        return {
            "front_month": data.front_month_future,
            "second_month": data.second_month_future,
            "spread": round(spread, 2),
            "spread_pct": round(spread_pct, 2),
            "term_structure": structure,
            "roll_yield_annualized": round(roll_yield * 12, 2),  # Approximate
            "interpretation": "NORMAL_MARKET" if structure == "CONTANGO" else "STRESS_MARKET"
        }
    
    def generate_signal(self, data: VIXData) -> Dict:
        """Generate trading signal based on VIX analysis"""
        term = self.analyze_term_structure(data)
        
        signals = []
        confidence = 50
        
        # Mean reversion signal - VIX tends to mean revert
        if data.spot_vix > self.long_vol_threshold:
            signals.append(VIXSignal.SHORT_VOLATILITY)
            confidence += 20
        elif data.spot_vix < self.short_vol_threshold:
            signals.append(VIXSignal.LONG_VOLATILITY)
            confidence += 20
        else:
            signals.append(VIXSignal.NEUTRAL)
        
        # Term structure signal
        if term["term_structure"] == "CONTANGO" and term["spread_pct"] > 5:
            signals.append(VIXSignal.CONTANGO_ROLL)
            confidence += 10
        elif term["term_structure"] == "BACKWARDATION":
            signals.append(VIXSignal.BACKWARDATION_ROLL)
            confidence += 10
        
        # VIX 9d vs spot (short-term momentum)
        if data.vix_9d > data.spot_vix * 1.1:
            signals.append(VIXSignal.LONG_VOLATILITY)
            confidence += 5
        elif data.vix_9d < data.spot_vix * 0.9:
            signals.append(VIXSignal.SHORT_VOLATILITY)
            confidence += 5
        
        # Primary signal
        primary = [s for s in signals if s != VIXSignal.NEUTRAL]
        if not primary:
            primary_signal = VIXSignal.NEUTRAL
        else:
            # Count occurrences
            signal_counts = {}
            for s in primary:
                signal_counts[s] = signal_counts.get(s, 0) + 1
            primary_signal = max(signal_counts, key=signal_counts.get)
        
        return {
            "timestamp": data.timestamp.isoformat(),
            "spot_vix": data.spot_vix,
            "primary_signal": primary_signal.value,
            "confidence": min(100, confidence),
            "term_structure": term,
            "strategy_recommendation": self._get_strategy(primary_signal),
            "risk_level": "HIGH" if data.spot_vix > 30 else "MODERATE" if data.spot_vix > 20 else "LOW"
        }
    
    def _get_strategy(self, signal: VIXSignal) -> str:
        """Map signal to specific strategy"""
        strategies = {
            VIXSignal.LONG_VOLATILITY: "Buy VIX calls, VXX, or UVXY",
            VIXSignal.SHORT_VOLATILITY: "Sell VIX calls, buy SVXY, or short VXX",
            VIXSignal.CONTANGO_ROLL: "Short front month VIX futures, long back month",
            VIXSignal.BACKWARDATION_ROLL: "Long front month VIX futures, short back month",
            VIXSignal.NEUTRAL: "No position, wait for clearer signal"
        }
        return strategies.get(signal, "Hold")
    
    def calculate_expected_roll_cost(self, days_held: int = 30) -> Dict:
        """Calculate expected cost of holding VIX futures position"""
        if not self.vix_history:
            return {"error": "No data available"}
        
        latest = self.vix_history[-1]
        term = self.analyze_term_structure(latest)
        
        # In contango, rolling futures loses money
        daily_roll_cost = term["spread_pct"] / 30  # Assuming 30 days per roll
        total_roll_cost = daily_roll_cost * days_held
        
        return {
            "term_structure": term["term_structure"],
            "current_spread_pct": term["spread_pct"],
            "estimated_daily_decay": round(daily_roll_cost, 3),
            "estimated_roll_cost_30d": round(total_roll_cost, 2),
            "hold_recommendation": "AVOID_FUTURES" if term["term_structure"] == "CONTANGO" and total_roll_cost > 5 else "CAUTION"
        }
    
    def backtest_simple_strategy(self, lookback_days: int = 90) -> Dict:
        """Backtest simple mean-reversion strategy"""
        if len(self.vix_history) < lookback_days:
            return {"error": "Insufficient history"}
        
        recent_data = self.vix_history[-lookback_days:]
        
        signals_generated = 0
        profitable_signals = 0
        
        for i, data in enumerate(recent_data[:-5]):  # Look at 5-day forward return
            signal_data = self.generate_signal(data)
            
            if signal_data["primary_signal"] != "neutral":
                signals_generated += 1
                
                # Check if VIX moved as predicted over next 5 days
                future_vix = recent_data[i + 5].spot_vix if i + 5 < len(recent_data) else data.spot_vix
                
                if signal_data["primary_signal"] == "short_vol" and future_vix < data.spot_vix:
                    profitable_signals += 1
                elif signal_data["primary_signal"] == "long_vol" and future_vix > data.spot_vix:
                    profitable_signals += 1
        
        win_rate = (profitable_signals / signals_generated * 100) if signals_generated > 0 else 0
        
        return {
            "lookback_days": lookback_days,
            "signals_generated": signals_generated,
            "profitable_signals": profitable_signals,
            "win_rate": round(win_rate, 1),
            "strategy_assessment": "VIABLE" if win_rate > 55 else "MARGINAL" if win_rate > 45 else "POOR"
        }
