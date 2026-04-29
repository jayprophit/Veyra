"""Carbon Trading Markets"""
from typing import Dict

class CarbonTrading:
    """Analyze compliance and voluntary carbon markets"""
    
    def __init__(self, market_type: str = "compliance"):
        self.market_type = market_type  # compliance or voluntary
    
    def market_overview(self) -> Dict:
        markets = {
            "compliance": {
                "eu_ets_price": 80,  # EUR/tonne
                "uk_ets_price": 45,
                "rggi_price": 15,  # Regional Greenhouse Gas Initiative
                "ca_cap_trade": 30,
                "total_value_billions": 850
            },
            "voluntary": {
                "vcs_price": 8,
                "gold_standard_price": 12,
                "car_ex_price": 3,  # Chicago Exchange
                "total_value_billions": 15
            }
        }
        
        return markets.get(self.market_type, markets["compliance"])
    
    def trading_strategy(self, position_size_tonnes: int = 10000) -> Dict:
        prices = self.market_overview()
        
        if self.market_type == "compliance":
            entry = prices.get("eu_ets_price", 80) * 1.1  # 10% premium for forward
            exit_target = entry * 1.25  # 25% upside target
            stop_loss = entry * 0.85
        else:
            entry = prices.get("vcs_price", 8)
            exit_target = entry * 1.50
            stop_loss = entry * 0.70
        
        position_value = position_size_tonnes * entry
        profit_target = position_size_tonnes * (exit_target - entry)
        
        return {
            "entry_price": round(entry, 2),
            "exit_target": round(exit_target, 2),
            "stop_loss": round(stop_loss, 2),
            "position_value": round(position_value, 0),
            "profit_potential": round(profit_target, 0),
            "risk_reward_ratio": round((exit_target - entry) / (entry - stop_loss), 2)
        }
    
    def arbitrage_opportunities(self) -> Dict:
        # Price differentials between markets
        spreads = {
            "eu_vs_uk": 35,  # EUR/tonne spread
            "compliance_vs_voluntary": 70,
            "vintage_2020_vs_2024": 5
        }
        
        return {
            "spreads": spreads,
            "arbitrage_potential": "High in fragmented markets",
            "transportation_cost": 2,  # $/tonne
            "verification_cost": 1,
            "net_arbitrage_margin": round(spreads["eu_vs_uk"] - 3, 0)
        }
    
    def hedging_strategy(self, carbon_intensity_tonnes_per_year: float) -> Dict:
        annual_exposure = carbon_intensity_tonnes_per_year
        
        # Hedge 80% of exposure
        hedge_volume = annual_exposure * 0.80
        
        # Futures pricing
        current_price = 80
        futures_price_1y = 85
        futures_price_2y = 90
        
        # Cost of carry
        storage = 0
        financing = current_price * 0.05  # 5% cost of capital
        
        return {
            "annual_exposure_tonnes": annual_exposure,
            "hedge_volume_tonnes": hedge_volume,
            "hedge_ratio": 0.80,
            "futures_prices": {
                "current": current_price,
                "1_year": futures_price_1y,
                "2_year": futures_price_2y
            },
            "cost_of_carry": round(financing, 2),
            "hedge_cost_pct": round((futures_price_1y - current_price) / current_price * 100, 1)
        }
