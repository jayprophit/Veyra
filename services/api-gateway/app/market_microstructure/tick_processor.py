"""Tick Processor - High-frequency tick data analysis"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Tick:
    timestamp: datetime
    price: float
    size: float
    side: str  # 'buy' or 'sell'

class TickProcessor:
    """Process and analyze tick-level data"""
    
    def calculate_vwap(self, ticks: List[Tick]) -> Dict:
        """Calculate VWAP from tick data"""
        if not ticks:
            return {"vwap": 0, "total_volume": 0, "tick_count": 0}
        
        total_value = sum(t.price * t.size for t in ticks)
        total_volume = sum(t.size for t in ticks)
        
        vwap = total_value / total_volume if total_volume > 0 else 0
        
        return {
            "vwap": round(vwap, 4),
            "total_volume": total_volume,
            "tick_count": len(ticks),
            "avg_tick_size": total_volume / len(ticks) if ticks else 0
        }
    
    def trade_flow_imbalance(self, ticks: List[Tick], window: int = 100) -> Dict:
        """Analyze buy vs sell flow"""
        recent = ticks[-window:] if len(ticks) > window else ticks
        
        buy_volume = sum(t.size for t in recent if t.side == "buy")
        sell_volume = sum(t.size for t in recent if t.side == "sell")
        
        total = buy_volume + sell_volume
        if total > 0:
            buy_ratio = buy_volume / total
            sell_ratio = sell_volume / total
        else:
            buy_ratio = sell_ratio = 0
        
        return {
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "buy_ratio": round(buy_ratio, 3),
            "sell_ratio": round(sell_ratio, 3),
            "flow_signal": "accumulation" if buy_ratio > 0.6 else "distribution" if sell_ratio > 0.6 else "neutral"
        }
    
    def tick_intensity(self, ticks: List[Tick], seconds: int = 60) -> Dict:
        """Calculate trading intensity"""
        if len(ticks) < 2:
            return {"ticks_per_second": 0, "volume_per_second": 0}
        
        time_span = (ticks[-1].timestamp - ticks[0].timestamp).total_seconds()
        
        if time_span > 0:
            tps = len(ticks) / time_span
            vps = sum(t.size for t in ticks) / time_span
        else:
            tps = vps = 0
        
        return {
            "ticks_per_second": round(tps, 2),
            "volume_per_second": round(vps, 2),
            "duration_seconds": time_span,
            "intensity": "high" if tps > 100 else "medium" if tps > 20 else "low"
        }
    
    def large_trade_detection(self, ticks: List[Tick], 
                            threshold_std: float = 2.0) -> Dict:
        """Detect unusually large trades"""
        if len(ticks) < 10:
            return {"large_trades": [], "count": 0}
        
        sizes = [t.size for t in ticks]
        avg_size = sum(sizes) / len(sizes)
        variance = sum((s - avg_size) ** 2 for s in sizes) / len(sizes)
        std_size = variance ** 0.5
        
        threshold = avg_size + (threshold_std * std_size)
        
        large = [t for t in ticks if t.size > threshold]
        
        return {
            "threshold": round(threshold, 2),
            "large_trades_detected": len(large),
            "large_trade_ratio": len(large) / len(ticks) if ticks else 0,
            "avg_trade_size": round(avg_size, 2),
            "significance": "institutional_activity" if len(large) > len(ticks) * 0.05 else "normal"
        }
    
    def price_velocity(self, ticks: List[Tick], window: int = 50) -> Dict:
        """Calculate price change velocity"""
        if len(ticks) < window:
            return {"velocity": 0, "acceleration": 0}
        
        recent = ticks[-window:]
        price_change = (recent[-1].price - recent[0].price) / recent[0].price if recent[0].price else 0
        
        # Calculate per-tick velocity
        velocity = price_change / window if window > 0 else 0
        
        # Compare to previous window for acceleration
        if len(ticks) >= window * 2:
            prev = ticks[-window*2:-window]
            prev_change = (prev[-1].price - prev[0].price) / prev[0].price if prev[0].price else 0
            acceleration = velocity - (prev_change / window if window > 0 else 0)
        else:
            acceleration = 0
        
        return {
            "velocity_bps_per_tick": round(velocity * 10000, 4),
            "acceleration": round(acceleration * 10000, 4),
            "direction": "up" if velocity > 0 else "down" if velocity < 0 else "flat",
            "momentum": "increasing" if acceleration > 0 and velocity > 0 else "decreasing" if acceleration < 0 and velocity > 0 else "reversing" if velocity * acceleration < 0 else "steady"
        }
