"""Recycling Arbitrage - Commodity recycling economics"""
from typing import Dict

class RecyclingArbitrage:
    """Analyze recycling arbitrage opportunities"""
    
    def scrap_metal_spread(self, virgin_price: float,
                          scrap_price: float,
                          processing_cost: float,
                          volume_tons: float) -> Dict:
        """Calculate scrap metal processing arbitrage"""
        spread = virgin_price - scrap_price - processing_cost
        total_profit = spread * volume_tons
        margin_pct = (spread / virgin_price) * 100 if virgin_price > 0 else 0
        
        return {
            "virgin_price": virgin_price,
            "scrap_price": scrap_price,
            "spread_per_ton": round(spread, 0),
            "total_profit": round(total_profit, 0),
            "margin_percent": round(margin_pct, 2),
            "viable": spread > 0
        }
    
    def plastic_reclaim_value(self, bale_cost: float,
                            processing_cost_per_lb: float,
                            pellet_market_price: float,
                            yield_rate: float) -> Dict:
        """Value plastic recycling economics"""
        cost_per_lb = bale_cost + processing_cost_per_lb
        revenue_per_lb = pellet_market_price * yield_rate
        margin = revenue_per_lb - cost_per_lb
        
        return {
            "input_cost_per_lb": round(cost_per_lb, 2),
            "revenue_per_lb": round(revenue_per_lb, 2),
            "margin_per_lb": round(margin, 2),
            "margin_percent": round((margin / cost_per_lb) * 100, 1) if cost_per_lb > 0 else 0,
            "profitable": margin > 0
        }
