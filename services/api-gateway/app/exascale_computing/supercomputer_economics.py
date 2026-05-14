"""Supercomputer Economics"""
from typing import Dict

class SupercomputerEconomics:
    """Exascale system costs and ROI"""
    
    def system_costs(self) -> Dict:
        return {
            "frontier": {"flops": 1.1e18, "cost": 600e6, "location": "ORNL"},
            "aurora": {"flops": 2.0e18, "cost": 500e6, "location": "ANL"},
            "el_capitan": {"flops": 2.0e18, "cost": 600e6, "location": "LLNL"}
        }
    
    def operating_costs(self) -> Dict:
        return {
            "power_consumption_mw": 30,
            "annual_energy_cost": 30e6,
            "cooling_infrastructure": 50e6,
            "staff_annual": 20e6,
            "total_annual": 100e6
        }
    
    def utilization_models(self) -> Dict:
        return {
            "national_labs": {"funding": "DOE", "primary_use": "Simulation"},
            "cloud_rental": {"price_per_hour": 10000, "market_growing": True},
            "ai_training": {"demand": "Exploding", "premium_pricing": True}
        }
