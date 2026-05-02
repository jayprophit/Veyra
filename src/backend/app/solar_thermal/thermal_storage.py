"""Thermal Storage Systems"""
from typing import Dict

class ThermalStorage:
    """Molten salt and other thermal storage"""
    
    def storage_media(self) -> Dict:
        return {
            "molten_salt": {
                "composition": "60% NaNO3, 40% KNO3",
                "temperature_range_c": [290, 565],
                "cost_per_kwh": 15,
                "energy_density_kwh_m3": 70,
                "maturity": "Commercial"
            },
            "liquid_sodium": {
                "temperature_range_c": [270, 530],
                "advantage": "Higher conductivity",
                "cost_per_kwh": 25,
                "status": "Pilot"
            },
            "particle_storage": {
                "medium": "Sand/silica",
                "temperature_max_c": 1000,
                "cost_per_kwh": 5,
                "advantage": "Very low cost"
            }
        }
    
    def economics(self, hours: int = 12) -> Dict:
        return {
            "storage_cost_m_per_hour": 50,
            "total_storage_cost_m": hours * 50,
            "tank_cost_m": 20,
            "heat_exchangers_m": 15,
            "total_system_m": hours * 50 + 35,
            "incremental_lcoe_usd_kwh": hours * 0.01,
            "vs_battery_storage": {"advantage": "No degradation", "duration": "Unlimited"}
        }
    
    def applications_beyond_csp(self) -> Dict:
        return {
            "industrial_heat": {"temperature_c": 400, "market": "Steel, cement, chemicals"},
            "power_to_heat": {"efficiency": 0.95, "grid_flexibility": "High"},
            "seasonal_storage": {"potential": "Weeks", "efficiency": 0.60}
        }
