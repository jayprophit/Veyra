"""Concentrated Solar Power Economics"""
from typing import Dict

class CSPEconomics:
    """CSP plants with thermal storage"""
    
    def technology_types(self) -> Dict:
        return {
            "parabolic_trough": {
                "maturity": "Commercial",
                "efficiency_pct": 15,
                "cost_per_kw": 4000,
                "storage_hours": 6,
                "dni_requirement": 2000
            },
            "solar_power_tower": {
                "maturity": "Commercial",
                "efficiency_pct": 23,
                "cost_per_kw": 5000,
                "storage_hours": 15,
                "dni_requirement": 2500
            },
            "dish_stirling": {
                "maturity": "Demonstration",
                "efficiency_pct": 30,
                "cost_per_kw": 6000,
                "modular": True
            }
        }
    
    def lcoe_analysis(self) -> Dict:
        return {
            "no_storage": {"lcoe_usd_kwh": 0.15, "capacity_factor": 0.25},
            "6hr_storage": {"lcoe_usd_kwh": 0.18, "capacity_factor": 0.40},
            "12hr_storage": {"lcoe_usd_kwh": 0.22, "capacity_factor": 0.55},
            "24hr_storage": {"lcoe_usd_kwh": 0.28, "capacity_factor": 0.70}
        }
    
    def market_regions(self) -> Dict:
        return {
            "morocco": {"capacity_mw": 580, "export_to_europe": True, "dni": 2500},
            "chile": {"capacity_mw": 110, "mining_offtake": True, "dni": 3000},
            "south_africa": {"capacity_mw": 500, "procurement": "REIPPPP", "dni": 2800},
            "australia": {"capacity_mw": 150, "hybrid_solar_pv": "Emerging", "dni": 2400}
        }
    
    def key_players(self) -> Dict:
        return {
            "abengoa": {"projects": 30, "technology": "Trough + tower", "origin": "Spain"},
            "brightsource": {"projects": 10, "technology": "Tower", "origin": "USA"},
            "acwa_power": {"projects": 15, "region": "MENA", "cost_leader": True}
        }
