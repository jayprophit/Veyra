"""Shipping Rates - Baltic Dry Index and freight analytics"""
from typing import Dict

class ShippingRates:
    """Analyze shipping rates and freight markets"""
    
    def baltic_dry_signal(self, bdi_current: float,
                         bdi_200dma: float,
                         commodity_demand: str) -> Dict:
        """Generate trading signals from Baltic Dry Index"""
        deviation = (bdi_current - bdi_200dma) / bdi_200dma
        
        signals = {
            "commodity": "buy" if deviation > 0.1 else "hold",
            "shipping_stocks": "buy" if deviation > 0.15 else "neutral",
            "dry_bulk": "overbought" if deviation > 0.3 else "oversold" if deviation < -0.2 else "neutral"
        }
        
        return {
            "bdi_current": bdi_current,
            "bdi_200dma": bdi_200dma,
            "deviation_pct": round(deviation * 100, 1),
            "trading_signals": signals,
            "trend": "bullish" if bdi_current > bdi_200dma else "bearish",
            "commodity_demand_proxy": commodity_demand
        }
    
    def freight_contract_value(self, route: str,
                              days_at_sea: int,
                              daily_rate: float,
                              fuel_cost_per_day: float) -> Dict:
        """Value freight shipping contracts"""
        revenue = days_at_sea * daily_rate
        fuel_cost = days_at_sea * fuel_cost_per_day
        
        # Route risk adjustments
        risk_multipliers = {
            "suez": 1.1, "panama": 1.05, "cape": 1.2, "strait_malacca": 1.15
        }
        risk_adj = risk_multipliers.get(route.lower(), 1.0)
        adjusted_revenue = revenue * risk_adj
        
        return {
            "route": route,
            "gross_revenue": round(adjusted_revenue, 0),
            "fuel_cost": round(fuel_cost, 0),
            "net_revenue": round(adjusted_revenue - fuel_cost, 0),
            "risk_adjusted": risk_adj > 1.0,
            "days_at_sea": days_at_sea
        }
    
    def container_arbitrage(self, origin_rate: float,
                           destination_rate: float,
                           container_capacity: int,
                           reposition_cost: float) -> Dict:
        """Container shipping arbitrage"""
        rate_diff = destination_rate - origin_rate
        potential_profit = rate_diff * container_capacity
        net_profit = potential_profit - reposition_cost
        
        return {
            "origin_rate": origin_rate,
            "destination_rate": destination_rate,
            "rate_spread": round(rate_diff, 0),
            "potential_profit": round(potential_profit, 0),
            "reposition_cost": reposition_cost,
            "net_arbitrage": round(net_profit, 0),
            "viable": net_profit > 0
        }
