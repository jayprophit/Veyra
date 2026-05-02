"""CO2 Utilization Economics"""
from typing import Dict

class CO2Utilization:
    """Converting captured CO2 to products"""
    
    def utilization_pathways(self) -> Dict:
        return {
            "fuels": {
                "product": "Methanol, jet fuel",
                "energy_required": "High",
                "market_size_tons": 10e6,
                "value_per_ton": 800,
                "carbon_benefit": "Circular if renewable energy"
            },
            "chemicals": {
                "product": "Urea, polymers, solvents",
                "market_size_tons": 200e6,
                "value_per_ton": 500,
                "maturity": "Commercial"
            },
            "building_materials": {
                "product": "Concrete, aggregates",
                "market_size_tons": 50e6,
                "value_per_ton": 100,
                "maturity": "Emerging"
            },
            "direct_use": {
                "product": "EOR, beverage, greenhouses",
                "market_size_tons": 250e6,
                "value_per_ton": 20,
                "carbon_benefit": "Limited (short cycle)"
            }
        }
    
    def economics_by_pathway(self) -> Dict:
        return {
            "concrete_curing": {
                "capex_per_ton_yearly": 100,
                "product_value": 100,
                "operating_margin": 0.10,
                "carbon_credit": 50,
                "total_value": 160
            },
            "synthetic_fuels": {
                "capex_per_ton_yearly": 500,
                "energy_cost_share": 0.70,
                "breakthrough_electricity_price": 0.02,
                "timeline": "2030+"
            }
        }
    
    def market_potential(self) -> Dict:
        return {
            "total_addressable_market_2050": 1e9,  # tons CO2/year
            "current_utilization": 230e6,
            "growth_rate": 0.15,
            "bottleneck": "Capture cost and scale"
        }
