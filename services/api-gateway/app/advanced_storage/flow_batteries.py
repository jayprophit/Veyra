"""Flow Battery Economics"""
from typing import Dict

class FlowBatteries:
    """Grid-scale flow battery systems"""
    
    def technology_types(self) -> Dict:
        return {
            "vanadium_redox": {
                "maturity": "Commercial",
                "efficiency": 0.75,
                "lifetime_years": 20,
                "cost_per_kwh": 400,
                "leaders": ["VRB Energy", "Invinity"]
            },
            "iron_chromium": {
                "advantage": "Abundant materials",
                "cost_per_kwh": 250,
                "developer": "ESS Inc",
                "deployment": "100MWh+ projects"
            },
            "zinc_bromine": {
                "advantage": "High energy density",
                "safety": "Non-flammable",
                "companies": ["Redflow", "Primus Power"]
            }
        }
    
    def use_cases(self) -> Dict:
        return {
            "long_duration_storage": {
                "duration_hours": 8,
                "applications": ["Solar shifting", "Wind firming"],
                "lcoe_target": 0.05
            },
            "grid_services": {
                "frequency_regulation": "Fast response",
                "peak_shaving": "Daily cycling",
                "capacity_deferral": "Avoid substation upgrades"
            }
        }
    
    def market_outlook(self) -> Dict:
        return {
            "market_2024": 500e6,
            "market_2030": 5e9,
            "cagr": 0.45,
            "driver": "Renewable integration"
        }
