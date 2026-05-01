"""Small Modular Reactor Economics"""
from typing import Dict

class SMREconomics:
    """SMR cost and deployment analysis"""
    
    def reactor_comparison(self) -> Dict:
        return {
            "nuscale": {
                "capacity_mw": 77,
                "modules_per_plant": 4,
                "cost_per_kw": 5500,
                "deployment": "2029",
                "backer": "Fluor"
            },
            " Rolls-Royce": {
                "capacity_mw": 470,
                "approach": "Integrated",
                "cost_per_kw": 4500,
                "location": "UK"
            },
            "x_energy": {
                "design": "Pebble bed",
                "coolant": "Helium",
                "funding": 1.2e9,
                "demonstration": "2030"
            },
            "terrestrial": {
                "design": "Integral PWR",
                "capacity_mw": 300,
                "cost_target": 4000
            }
        }
    
    def cost_structure(self) -> Dict:
        return {
            "overnight_cost": {"per_kw": 5000, "per_plant_300mw": 1.5e9},
            "learning_curve": {"cost_reduction_per_doubling": 0.15},
            "om_per_mwh": 15,
            "fuel_cost_per_mwh": 8,
            "decommissioning_fund": 0.02
        }
    
    def advantages_vs_large(self) -> Dict:
        return {
            "construction_time": {"smr_years": 4, "large_years": 10},
            "financing": {"lower_upfront": True, "modular_investment": True},
            "siting": {"smaller_footprint": True, "cooling_requirements": "Lower"},
            "load_following": {"flexibility": "Better for renewables integration"}
        }
