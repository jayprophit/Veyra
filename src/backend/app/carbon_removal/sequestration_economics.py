"""Carbon Sequestration Economics"""
from typing import Dict

class SequestrationEconomics:
    """CO2 storage and utilization"""
    
    def storage_options(self) -> Dict:
        return {
            "geological": {
                "cost_per_ton": 20,
                "capacity_gigatons": 10000,
                "permanence": "Millions of years",
                "risk": "Very low"
            },
            "mineralization": {
                "cost_per_ton": 100,
                "timeline": "Years",
                "approach": "Reactive rocks, concrete"
            },
            "biomass": {
                "cost_per_ton": 50,
                "timeline": "Centuries",
                "risk": "Reversal possible"
            },
            "ocean": {
                "cost_per_ton": 30,
                "approach": "Alkalinity enhancement",
                "concerns": "Ecosystem impacts"
            }
        }
    
    def utilization_revenue(self) -> Dict:
        return {
            "co2_to_fuel": {"price_per_ton": 200, "market": "Aviation"},
            "co2_to_plastics": {"price_per_ton": 800, "market": "Packaging"},
            "co2_to_concrete": {"price_per_ton": 100, "market": "Construction"},
            "enhanced_oil_recovery": {"price_per_ton": 20, "controversy": "Carbon neutral claims"}
        }
