"""Hydroponics Economics"""
from typing import Dict

class Hydroponics:
    """Soil-less cultivation economics"""
    
    def system_types(self) -> Dict:
        return {
            "nft": {
                "full_name": "Nutrient Film Technique",
                "best_for": "Leafy greens",
                "capex_per_sqm": 200,
                "yield_multiplier": 10
            },
            "dwc": {
                "full_name": "Deep Water Culture",
                "best_for": "Lettuce, herbs",
                "capex_per_sqm": 150,
                "maintenance": "Low"
            },
            "aeroponics": {
                "best_for": "High value crops",
                "capex_per_sqm": 400,
                "yield_multiplier": 15,
                "water_use": "Minimal"
            }
        }
    
    def opex_breakdown(self) -> Dict:
        return {
            "nutrients": {"percent": 0.15, "cost_per_kg_produce": 0.30},
            "energy": {"percent": 0.25, "led_efficiency": "2.7 umol/J"},
            "labor": {"percent": 0.30, "automation_potential": 0.50},
            "seeds": {"percent": 0.10},
            "packaging": {"percent": 0.20}
        }
    
    def competitive_position(self) -> Dict:
        return {
            "vs_field_farming": {"water_use": 0.10, "yield_per_acre": 10, "energy": "Higher"},
            "vs_vertical": {"capex": "Lower", "scalability": "Better", "automation": "Less"},
            "premium_market": {"organic": True, "local": True, "pesticide_free": True}
        }
