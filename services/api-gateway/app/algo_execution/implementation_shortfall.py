"""Implementation Shortfall - Arrival price benchmark"""
from typing import Dict

class ImplementationShortfall:
    """Calculate implementation shortfall costs"""
    
    def calculate_is(self, arrival_price: float,
                    avg_execution_price: float,
                    order_size: float,
                    side: str) -> Dict:
        """Calculate implementation shortfall"""
        if side == "buy":
            shortfall = avg_execution_price - arrival_price
        else:
            shortfall = arrival_price - avg_execution_price
        
        shortfall_bps = (shortfall / arrival_price) * 10000 if arrival_price else 0
        total_cost = shortfall * order_size
        
        return {
            "arrival_price": arrival_price,
            "avg_execution_price": avg_execution_price,
            "order_size": order_size,
            "side": side,
            "shortfall": round(shortfall, 4),
            "shortfall_bps": round(shortfall_bps, 2),
            "total_cost": round(total_cost, 2),
            "quality": "excellent" if shortfall_bps < 5 else "good" if shortfall_bps < 15 else "poor"
        }
    
    def component_analysis(self, shortfall_bps: float,
                          spread_bps: float,
                          market_impact_bps: float,
                          timing_cost_bps: float) -> Dict:
        """Break down IS into components"""
        components = {
            "spread_cost": spread_bps,
            "market_impact": market_impact_bps,
            "timing_cost": timing_cost_bps,
            "residual": shortfall_bps - spread_bps - market_impact_bps - timing_cost_bps
        }
        
        return {
            "total_shortfall_bps": shortfall_bps,
            "components": {k: round(v, 2) for k, v in components.items()},
            "largest_component": max(components.items(), key=lambda x: abs(x[1]))[0]
        }
