"""VWAP Executor - Volume Weighted Average Price"""
from typing import Dict, List

class VWAPExecutor:
    """Execute orders using VWAP strategy"""
    
    def calculate_vwap_schedule(self, order_size: float,
                                 volume_profile: List[float]) -> Dict:
        """Calculate VWAP order schedule based on historical volume"""
        total_vol = sum(volume_profile)
        if total_vol == 0:
            return {"error": "Invalid volume profile"}
        
        schedule = []
        for i, vol in enumerate(volume_profile):
            slice_pct = vol / total_vol
            slice_size = order_size * slice_pct
            schedule.append({
                "slice": i + 1,
                "target_volume": vol,
                "order_quantity": round(slice_size, 2),
                "percentage_of_day": round(slice_pct * 100, 1)
            })
        
        return {
            "total_order": order_size,
            "num_slices": len(volume_profile),
            "schedule": schedule,
            "expected_participation_rate": round(order_size / total_vol * 100, 2)
        }
    
    def vwap_performance(self, vwap_price: float,
                        benchmark_vwap: float) -> Dict:
        """Measure execution performance vs VWAP benchmark"""
        deviation = vwap_price - benchmark_vwap
        deviation_bps = (deviation / benchmark_vwap) * 10000 if benchmark_vwap else 0
        
        return {
            "vwap_price": vwap_price,
            "benchmark_vwap": benchmark_vwap,
            "deviation": round(deviation, 4),
            "deviation_bps": round(deviation_bps, 2),
            "performance": "better" if deviation < 0 else "worse"
        }
