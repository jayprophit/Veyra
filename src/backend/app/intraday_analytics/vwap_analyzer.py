"""VWAP Analyzer - Volume Weighted Average Price analysis"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, time
import statistics

@dataclass
class Tick:
    price: float
    volume: int
    timestamp: datetime
    bid: float
    ask: float

class VWAPAnalyzer:
    """Analyze VWAP for execution quality"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticks: List[Tick] = []
        self.vwap_data: Dict = {}
    
    def add_tick(self, tick: Tick):
        """Add intraday tick data"""
        self.ticks.append(tick)
    
    def calculate_vwap(self, start_time: time = None, end_time: time = None) -> Dict:
        """Calculate VWAP for period"""
        if not self.ticks:
            return {"error": "No tick data available"}
        
        # Filter by time if specified
        filtered_ticks = self.ticks
        if start_time and end_time:
            filtered_ticks = [
                t for t in self.ticks 
                if start_time <= t.timestamp.time() <= end_time
            ]
        
        if not filtered_ticks:
            return {"error": "No ticks in specified time range"}
        
        # Calculate VWAP
        total_pv = sum(t.price * t.volume for t in filtered_ticks)
        total_volume = sum(t.volume for t in filtered_ticks)
        
        vwap = total_pv / total_volume if total_volume > 0 else 0
        
        # Calculate standard deviation around VWAP
        prices = [t.price for t in filtered_ticks]
        std_dev = statistics.stdev(prices) if len(prices) > 1 else 0
        
        # Current price vs VWAP
        current_price = filtered_ticks[-1].price if filtered_ticks else 0
        deviation = ((current_price - vwap) / vwap) * 100 if vwap > 0 else 0
        
        return {
            "symbol": self.symbol,
            "vwap": round(vwap, 4),
            "current_price": round(current_price, 4),
            "deviation_bps": round(deviation * 100, 2),  # In basis points
            "total_volume": total_volume,
            "price_std": round(std_dev, 4),
            "interpretation": "ABOVE_VWAP" if deviation > 0.001 else "BELOW_VWAP" if deviation < -0.001 else "AT_VWAP",
            "signal": "SELL" if deviation > 0.005 else "BUY" if deviation < -0.005 else "NEUTRAL"
        }
    
    def calculate_intraday_vwap(self, interval_minutes: int = 30) -> List[Dict]:
        """Calculate VWAP for intraday intervals"""
        if not self.ticks:
            return []
        
        # Sort ticks by timestamp
        sorted_ticks = sorted(self.ticks, key=lambda x: x.timestamp)
        
        # Group by intervals
        interval_vwaps = []
        current_bucket = []
        current_start = sorted_ticks[0].timestamp.replace(second=0, microsecond=0)
        
        for tick in sorted_ticks:
            elapsed = (tick.timestamp - current_start).total_seconds() / 60
            
            if elapsed >= interval_minutes:
                # Calculate VWAP for current bucket
                if current_bucket:
                    total_pv = sum(t.price * t.volume for t in current_bucket)
                    total_vol = sum(t.volume for t in current_bucket)
                    vwap = total_pv / total_vol if total_vol > 0 else 0
                    avg_price = statistics.mean([t.price for t in current_bucket])
                    
                    interval_vwaps.append({
                        "start_time": current_start.isoformat(),
                        "end_time": tick.timestamp.isoformat(),
                        "vwap": round(vwap, 4),
                        "avg_price": round(avg_price, 4),
                        "volume": total_vol,
                        "tick_count": len(current_bucket),
                        "price_vs_vwap": round(((avg_price - vwap) / vwap) * 100, 3) if vwap > 0 else 0
                    })
                
                current_bucket = [tick]
                current_start = tick.timestamp.replace(second=0, microsecond=0)
            else:
                current_bucket.append(tick)
        
        return interval_vwaps
    
    def analyze_execution_quality(self, execution_price: float, 
                                 execution_volume: int,
                                 side: str) -> Dict:
        """Analyze execution quality vs VWAP"""
        vwap_data = self.calculate_vwap()
        
        if "error" in vwap_data:
            return vwap_data
        
        vwap = vwap_data["vwap"]
        
        # Calculate slippage
        if side == "buy":
            slippage = ((execution_price - vwap) / vwap) * 10000  # In bps
        else:  # sell
            slippage = ((vwap - execution_price) / vwap) * 10000
        
        # Grade the execution
        if slippage > 5:
            grade = "POOR"
        elif slippage > 2:
            grade = "FAIR"
        elif slippage > -2:
            grade = "GOOD"
        else:
            grade = "EXCELLENT"
        
        # Estimate market impact
        total_volume = vwap_data["total_volume"]
        participation_rate = (execution_volume / total_volume) * 100 if total_volume > 0 else 0
        
        estimated_impact = 0
        if participation_rate > 20:
            estimated_impact = 10  # 10 bps
        elif participation_rate > 10:
            estimated_impact = 5
        elif participation_rate > 5:
            estimated_impact = 2
        
        return {
            "symbol": self.symbol,
            "execution_price": execution_price,
            "vwap": vwap,
            "slippage_bps": round(slippage, 2),
            "execution_grade": grade,
            "participation_rate": round(participation_rate, 2),
            "estimated_market_impact_bps": estimated_impact,
            "recommendation": "REDUCE_SIZE" if grade == "POOR" else "ACCEPTABLE"
        }
    
    def get_volume_distribution(self, num_buckets: int = 13) -> List[Dict]:
        """Get volume distribution across trading hours"""
        if not self.ticks:
            return []
        
        # Define trading hours buckets (9:30 - 16:00 in 30-min intervals)
        total_volume = sum(t.volume for t in self.ticks)
        
        # Group by time bucket
        from collections import defaultdict
        bucket_volumes = defaultdict(int)
        
        for tick in self.ticks:
            hour = tick.timestamp.hour
            minute = tick.timestamp.minute
            # Create 30-min buckets
            bucket = f"{hour:02d}:{(minute // 30) * 30:02d}"
            bucket_volumes[bucket] += tick.volume
        
        # Calculate distribution
        distribution = []
        for bucket, volume in sorted(bucket_volumes.items()):
            pct = (volume / total_volume) * 100 if total_volume > 0 else 0
            distribution.append({
                "time_bucket": bucket,
                "volume": volume,
                "percentage": round(pct, 2),
                "intensity": "HIGH" if pct > 12 else "MODERATE" if pct > 8 else "LOW"
            })
        
        return distribution
