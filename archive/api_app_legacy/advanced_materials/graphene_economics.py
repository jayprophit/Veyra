"""Graphene Economics"""
from typing import Dict

class GrapheneEconomics:
    """Analyze graphene production and applications"""
    
    def __init__(self, quality: str = "industrial"):
        self.quality = quality  # research, industrial, electronic
    
    def production_cost(self, annual_output_kg: float = 1000) -> Dict:
        costs = {
            "research": {"cost_per_gram": 500, "method": "mechanical exfoliation"},
            "industrial": {"cost_per_gram": 50, "method": "chemical vapor deposition"},
            "electronic": {"cost_per_gram": 200, "method": "CVD on copper"}
        }
        
        data = costs.get(self.quality, costs["industrial"])
        
        # Scale effects
        if annual_output_kg > 1000:
            scale_factor = 0.5
        elif annual_output_kg > 100:
            scale_factor = 0.7
        else:
            scale_factor = 1.0
        
        adjusted_cost = data["cost_per_gram"] * scale_factor
        
        return {
            "quality_grade": self.quality,
            "production_method": data["method"],
            "cost_per_gram": adjusted_cost,
            "cost_per_kg": adjusted_cost * 1000,
            "annual_output_kg": annual_output_kg,
            "total_annual_cost": adjusted_cost * 1000 * annual_output_kg
        }
    
    def application_markets(self) -> Dict:
        return {
            "batteries": {
                "market_size_2030_billions": 5,
                "value_add": "2x energy density",
                "timeline": "2025-2027"
            },
            "composites": {
                "market_size_2030_billions": 3,
                "value_add": "50% weight reduction",
                "timeline": "Current"
            },
            "electronics": {
                "market_size_2030_billions": 8,
                "value_add": "Flexible, conductive",
                "timeline": "2026-2028"
            },
            "coatings": {
                "market_size_2030_billions": 2,
                "value_add": "Corrosion resistant",
                "timeline": "Current"
            }
        }
    
    def investment_landscape(self) -> Dict:
        return {
            "public_companies": {
                "graphene_3d_lab": {"market_cap": 50e6, "focus": "Composites"},
                "haydale": {"market_cap": 30e6, "focus": "Functionalization"},
                "nano_xplore": {"market_cap": 100e6, "focus": "Batteries"}
            },
            "private_companies": {
                "graphenea": {"funding": 20e6, "focus": "CVD graphene"},
                "vorbeck": {"funding": 15e6, "focus": "Conductive inks"},
                "xg_sciences": {"funding": 50e6, "focus": "Graphene nanoplatelets"}
            },
            "total_market_2030": 18e9  # $18B
        }
