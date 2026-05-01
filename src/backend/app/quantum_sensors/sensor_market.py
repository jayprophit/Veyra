"""Quantum Sensor Market"""
from typing import Dict

class SensorMarket:
    """Market sizing for quantum sensing"""
    
    def market_overview(self) -> Dict:
        return {
            "market_2024": 0.5e9,
            "market_2030": 2.5e9,
            "cagr": 0.30,
            "drivers": ["Navigation", "Medical imaging", "Defense", "Resources"]
        }
    
    def technology_types(self) -> Dict:
        return {
            "atomic_clocks": {
                "accuracy": "1 second in 300M years",
                "market": "GPS, telecom",
                "price_range": "10K-1M"
            },
            "gravimeters": {
                "application": "Underground mapping",
                "sensitivity": "Microgal level",
                "market_size": 200e6
            },
            "magnetometers": {
                "application": "Brain imaging, mineral detection",
                "sensitivity": "femtotesla",
                "market_size": 300e6
            }
        }
    
    def key_companies(self) -> Dict:
        return {
            "coldquanta": {"focus": "Atomic clocks", "funding": 75e6},
            "muquans": {"focus": "Gravimetry", "location": "France"},
            "aqc": {"focus": "Medical imaging", "approach": "Diamond NV centers"}
        }
