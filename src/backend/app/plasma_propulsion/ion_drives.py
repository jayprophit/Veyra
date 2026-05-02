"""Ion Drive Economics"""
from typing import Dict

class IonDrives:
    """Electric propulsion for spacecraft"""
    
    def thruster_types(self) -> Dict:
        return {
            "gridded_ion": {
                "isp_seconds": 3000,
                "thrust_mn": 100,
                "efficiency_pct": 65,
                "applications": ["Deep space", "Station keeping"],
                "heritage": "Dawn, BepiColombo"
            },
            "hall_effect": {
                "isp_seconds": 2000,
                "thrust_mn": 200,
                "efficiency_pct": 55,
                "advantage": "Higher thrust density",
                "applications": ["LEO", "GEO insertion"]
            },
            "helicon": {
                "isp_seconds": 5000,
                "electrodes": "None",
                "advantage": "No erosion",
                "status": "Development"
            }
        }
    
    def mission_economics(self, delta_v_m_s: int = 5000, mass_tons: int = 5) -> Dict:
        return {
            "chemical_rocket_mass_kg": mass_tons * 1000 * 0.80,  # 80% fuel
            "electric_rocket_mass_kg": mass_tons * 1000 * 0.20,  # 20% fuel
            "launch_cost_savings_m": (mass_tons * 1000 * 0.60 * 10000) / 1e6,
            "trip_time_months": 12,  # vs 3 for chemical
            "power_required_kw": 5,
            "solar_array_cost_m": 5
        }
    
    def market_segments(self) -> Dict:
        return {
            "satellite_propulsion": {
                "market_2024_m": 200,
                "growth": 0.15,
                "drivers": ["Constellation deployment", "Station keeping"]
            },
            "deep_space": {
                "market": "Small but strategic",
                "value": "Enable missions otherwise impossible"
            }
        }
