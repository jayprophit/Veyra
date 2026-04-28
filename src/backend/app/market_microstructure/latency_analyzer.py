"""Latency Analyzer - HFT latency and execution quality"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LatencyEvent:
    event_type: str
    timestamp: datetime
    duration_ms: float

class LatencyAnalyzer:
    """Analyze execution latency and HFT metrics"""
    
    def round_trip_time(self, events: List[LatencyEvent]) -> Dict:
        """Calculate round-trip latency statistics"""
        durations = [e.duration_ms for e in events if e.duration_ms > 0]
        if not durations:
            return {"avg_rtt": 0, "min_rtt": 0, "max_rtt": 0}
        
        return {
            "avg_rtt_ms": round(sum(durations) / len(durations), 3),
            "min_rtt_ms": round(min(durations), 3),
            "max_rtt_ms": round(max(durations), 3)
        }
    
    def execution_quality(self, target_price: float, 
                         actual_price: float) -> Dict:
        """Calculate execution quality metrics"""
        slippage = abs(actual_price - target_price)
        slippage_bps = (slippage / target_price) * 10000 if target_price else 0
        
        return {
            "target_price": target_price,
            "actual_price": actual_price,
            "slippage": round(slippage, 4),
            "slippage_bps": round(slippage_bps, 2),
            "quality": "excellent" if slippage_bps < 1 else "good" if slippage_bps < 5 else "poor"
        }
    
    def hft_advantage(self, colocation_latency: float, 
                     retail_latency: float) -> Dict:
        """Calculate HFT latency advantage"""
        advantage_ms = retail_latency - colocation_latency
        return {
            "colocation_latency_ms": colocation_latency,
            "retail_latency_ms": retail_latency,
            "advantage_ms": advantage_ms,
            "advantage_ratio": retail_latency / colocation_latency if colocation_latency > 0 else 0
        }
