"""Consumer 3D Printing"""
from typing import Dict

class ConsumerPrinting:
    """Desktop and prosumer 3D printing"""
    
    def printer_segments(self) -> Dict:
        return {
            "hobby": {"price_range": [200, 500], "market_share": 0.40, "brands": ["Creality", "Anycubic"]},
            "prosumer": {"price_range": [500, 2000], "market_share": 0.35, "brands": ["Prusa", "Bambu Lab"]},
            "professional": {"price_range": [2000, 10000], "market_share": 0.25, "brands": ["Formlabs", "Ultimaker"]}
        }
    
    def market_size(self) -> Dict:
        return {
            "total_units_2024": 2.2e6,
            "total_revenue_billions": 1.8,
            "cagr": 0.15,
            "installed_base": 12e6,
            "regional_split": {"asia": 0.45, "europe": 0.30, "americas": 0.25}
        }
    
    def material_economics(self) -> Dict:
        return {
            "pla": {"price_per_kg": 25, "margin": 0.60, "use_case": "Prototyping"},
            "abs": {"price_per_kg": 30, "margin": 0.55, "use_case": "Functional parts"},
            "petg": {"price_per_kg": 35, "margin": 0.50, "use_case": "Durability"},
            "resin": {"price_per_liter": 50, "margin": 0.70, "use_case": "Detail"}
        }
