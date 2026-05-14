"""Wave Energy Economics"""
from typing import Dict

class WaveEnergy:
    """Wave power generation costs and market"""
    
    def technology_types(self) -> Dict:
        return {
            "point_absorber": {
                "design": "Buoy-based",
                "efficiency": "Moderate",
                "cost_per_kw": 8000,
                "maintenance": "Challenging"
            },
            "attenuator": {
                "design": "Snake-like floating",
                "example": "Pelamis (defunct)",
                "lessons": "Survivability key"
            },
            "terminator": {
                "design": "Shore-mounted",
                "advantage": "Easier maintenance",
                "disadvantage": "Limited sites"
            },
            "oscillating_water_column": {
                "design": "Air compression",
                "maturity": "Proven, Lanzarote plant",
                "efficiency": "Lower"
            }
        }
    
    def cost_structure(self) -> Dict:
        return {
            "capex_per_kw": 6000,
            "foundation": 0.30,
            "device": 0.40,
            "electrical": 0.20,
            "installation": 0.10,
            "om_percent_annual": 0.07,
            "lcoe_usd_kwh": 0.30
        }
    
    def resource_potential(self) -> Dict:
        return {
            "global_wave_power_tw": 3,
            "recoverable_pct": 10,
            "best_regions": ["Europe Atlantic", "US West", "Australia", "Chile"],
            "us_potential_twh_yearly": 2500
        }
    
    def companies(self) -> Dict:
        return {
            "corpower": {"technology": "Point absorber", "location": "Sweden", "pilot": "Portugal"},
            "bombardier": {"wavegen": "OWC technology", "status": "Limited activity"},
            "aws_ocean": {"technology": "Archimedes wave swing", "location": "Netherlands"}
        }
