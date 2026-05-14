"""High-Altitude Balloon Economics"""
from typing import Dict

class HABSEconomics:
    """Stratospheric balloon operations"""
    
    def platform_types(self) -> Dict:
        return {
            "weather_balloons": {
                "altitude_km": 30,
                "duration_hours": 2,
                "cost": 1000,
                "payload_kg": 5,
                "recoverable": False
            },
            "super_pressure": {
                "altitude_km": 20,
                "duration_months": 6,
                "cost": 100000,
                "payload_kg": 50,
                "recoverable": False
            },
            "stratollites": {
                "altitude_km": 20,
                "duration_months": 12,
                "cost": 500000,
                "payload_kg": 100,
                "station_keeping": True
            }
        }
    
    def applications(self) -> Dict:
        return {
            "remote_sensing": {
                "resolution_m": 0.5,
                "revisit": "Persistent",
                "cost_vs_satellite": 0.10,
                "market": "Agriculture, security"
            },
            "communications": {
                "coverage_radius_km": 200,
                "latency_ms": 10,
                "backhaul": "Ground or laser",
                "market": "Rural broadband"
            },
            "weather_monitoring": {
                "instruments": ["Temperature", "Humidity", "Wind"],
                "altitude_coverage": "Gap filling",
                "market": "Forecast improvement"
            }
        }
    
    def operators(self) -> Dict:
        return {
            "world_view": {"focus": "Earth imaging", "funding": 50e6, "flights": 100},
            "zero2infinity": {"focus": "Spain/EU", "applications": "Telecom + sensing"},
            "sceye": {"focus": "Stationary platforms", "persistence": "Months", "target": "MENA connectivity"}
        }
