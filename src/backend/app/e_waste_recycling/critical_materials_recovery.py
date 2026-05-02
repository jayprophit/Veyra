"""Critical Materials Recovery Economics"""
from typing import Dict

class CriticalMaterialsRecovery:
    """Strategic material recycling"""
    
    def material_targets(self) -> Dict:
        return {
            "lithium": {
                "source": "EV batteries",
                "recovery_rate_target": 0.95,
                "current_rate": 0.50,
                "price_per_kg": 20,
                "value_in_waste_stream": "High"
            },
            "cobalt": {
                "source": "Batteries + electronics",
                "recovery_rate": 0.85,
                "price_per_kg": 30,
                "supply_risk": "High (DRC dominance)"
            },
            "rare_earths": {
                "source": "Magnets, screens",
                "recovery_rate": 0.30,
                "challenge": "Separation complexity",
                "price_per_kg": 100
            },
            "gold": {
                "source": "PCBs, connectors",
                "recovery_rate": 0.98,
                "grade_ppm": 200,
                "drives_economics": True
            }
        }
    
    def recycling_value(self, device_type: str = "smartphone") -> Dict:
        values = {
            "smartphone": {"weight_g": 200, "recoverable_value_usd": 1.50, "gold_mg": 34},
            "laptop": {"weight_g": 2000, "recoverable_value_usd": 8, "gold_mg": 200},
            "ev_battery": {"weight_kg": 300, "recoverable_value_usd": 1500, "lithium_kg": 6}
        }
        return values.get(device_type, values["smartphone"])
    
    def strategic_imperative(self) -> Dict:
        return {
            "supply_security": {
                "china_dominance": "Critical for rare earths",
                "drc_cobalt": "ESG concerns",
                "recycling_as_hedge": "Diversification"
            },
            "eu_critical_raw_materials_act": {
                "recycling_target_2030": 0.20,
                "current": 0.05,
                "investment_incentives": "Available"
            },
            "us_inflation_reduction_act": {
                "recycled_content_credit": True,
                "domestic_processing": "Incentivized"
            }
        }
