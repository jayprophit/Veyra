"""TWAP Executor - Time Weighted Average Price"""
from typing import Dict
from datetime import datetime, timedelta

class TWAPExecutor:
    """Execute orders using TWAP strategy"""
    
    def calculate_twap(self, order_size: float, 
                      start_time: datetime,
                      end_time: datetime,
                      num_slices: int = 10) -> Dict:
        """Calculate TWAP order schedule"""
        duration = (end_time - start_time).total_seconds()
        interval = duration / num_slices
        slice_size = order_size / num_slices
        
        schedule = []
        for i in range(num_slices):
            slice_time = start_time + timedelta(seconds=interval * i)
            schedule.append({
                "time": slice_time,
                "quantity": slice_size,
                "slice_number": i + 1
            })
        
        return {
            "total_order": order_size,
            "num_slices": num_slices,
            "slice_size": slice_size,
            "duration_minutes": duration / 60,
            "interval_seconds": interval,
            "schedule": schedule
        }
    
    def twap_performance(self, executed_price: float,
                        benchmark_twap: float) -> Dict:
        """Measure execution performance vs TWAP benchmark"""
        deviation = executed_price - benchmark_twap
        deviation_bps = (deviation / benchmark_twap) * 10000 if benchmark_twap else 0
        
        return {
            "executed_price": executed_price,
            "benchmark_twap": benchmark_twap,
            "deviation": round(deviation, 4),
            "deviation_bps": round(deviation_bps, 2),
            "performance": "better" if deviation < 0 else "worse",
            "savings": abs(deviation) if deviation < 0 else 0
        }
