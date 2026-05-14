"""Atmospheric Water Generation Economics"""
from typing import Dict

class AWGEconomics:
    """Air-to-water technology costs"""
    
    def technology_types(self) -> Dict:
        return {
            "cooling_condensation": {
                "efficiency": "Energy intensive",
                "cost_per_liter": 0.10,
                "best_for": "High humidity",
                "humidity_required_pct": 60
            },
            "desiccant_based": {
                "efficiency": "Lower energy",
                "cost_per_liter": 0.05,
                "works_at_low_humidity": True,
                "humidity_required_pct": 30
            },
            "hybrid_systems": {
                "approach": "Solar + desiccant",
                "cost_per_liter": 0.03,
                "off_grid": True
            }
        }
    
    def system_costs(self, capacity_liters_daily: int = 1000) -> Dict:
        return {
            "residential": {"cost_per_liter_capacity": 2, "unit_cost": 2000, "payback_years": 3},
            "commercial": {"cost_per_liter_capacity": 1, "unit_cost": 10000, "applications": "Hotels, offices"},
            "utility_scale": {"cost_per_liter_capacity": 0.50, "plant_cost_millions": 10, "output_mld": 1}
        }
    
    def market_opportunity(self) -> Dict:
        return {
            "water_stressed_population": 2e9,
            "addressable_market_value": 50e9,
            "current_penetration": 0.001,
            "growth_drivers": ["Scarcity", "Decentralization", "Quality concerns"]
        }
    
    def key_companies(self) -> Dict:
        return {
            "zero_mass_water": {"approach": "Solar + hygroscopic", "funding": 100e6, "focus": "Residential"},
            "watergen": {"approach": "Cooling", "market": "Emergency/disaster", "products": "Mobile units"},
            "source": {"approach": "Hydropanel", "cost": 2000, "output": 5, "target": "Off-grid homes"}
        }
