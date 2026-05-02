"""E-Waste Recycling Economics"""
from typing import Dict

class RecyclingEconomics:
    """Electronics recycling business models"""
    
    def waste_stream(self) -> Dict:
        return {
            "global_generation_million_tons": 60,
            "formal_recycling_pct": 0.17,
            "informal_recycling_pct": 0.20,
            "landfill_storage_pct": 0.63,
            "value_in_waste_billion": 60,
            "growth_rate": 0.03
        }
    
    def recycling_processes(self) -> Dict:
        return {
            "manual_dismantling": {
                "cost_per_ton": 500,
                "recovery_rate_pct": 70,
                "labor_intensive": True,
                "location": "Developing countries"
            },
            "mechanical_shredding": {
                "cost_per_ton": 300,
                "recovery_rate_pct": 60,
                "capital_intensive": True,
                "separation": "Limited"
            },
            "advanced_pyrometallurgy": {
                "cost_per_ton": 800,
                "recovery_rate_pct": 95,
                "energy_intensive": True,
                "emissions": "Concerns"
            },
            "hydrometallurgy": {
                "cost_per_ton": 600,
                "recovery_rate_pct": 90,
                "selective": True,
                "chemicals": "Management needed"
            }
        }
    
    def business_models(self) -> Dict:
        return {
            "producer_responsibility": {
                "mechanism": "EPR fees",
                "coverage": "EU, some US states",
                "fee_per_kg": 0.50,
                "funding": "Built into product price"
            },
            "urban_mining": {
                "concept": "E-waste as ore",
                "gold_grade_vs_natural": 200,
                "copper_grade_vs_natural": 40,
                "value_proposition": "Higher grade than mines"
            }
        }
    
    def major_recyclers(self) -> Dict:
        return {
            "erico": {"capacity_tons": 100000, "focus": "Refining", "global": True},
            "umicore": {"capacity_tons": 50000, "focus": "Precious metals", "location": "Belgium"},
            "apple_daisy": {"focus": "In-house recovery", "capacity": "Limited", "innovation": "High"}
        }
