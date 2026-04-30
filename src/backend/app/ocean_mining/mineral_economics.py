"""Mineral Economics"""
from typing import Dict

class MineralEconomics:
    """Mineral pricing and demand analysis"""
    
    def __init__(self, mineral: str = "cobalt"):
        self.mineral = mineral
    
    def demand_forecast(self) -> Dict:
        demands = {
            "cobalt": {
                "current_demand_kt": 170,
                "ev_battery_share": 0.40,
                "2030_demand_kt": 400,
                "cagr": 0.13
            },
            "nickel": {
                "current_demand_mt": 3.0,
                "ev_battery_share": 0.10,
                "2030_demand_mt": 5.5,
                "cagr": 0.08
            },
            "copper": {
                "current_demand_mt": 25,
                "ev_share": 0.05,
                "2030_demand_mt": 35,
                "cagr": 0.04
            }
        }
        return demands.get(self.mineral, demands["cobalt"])
    
    def supply_sources(self) -> Dict:
        return {
            "land_based": {"share": 0.98, "risk": "Environmental, social"},
            "ocean_mining": {"share": 0.00, "potential": "High", "timeline": "2025+"},
            "recycling": {"share": 0.02, "growth": "Increasing"}
        }
