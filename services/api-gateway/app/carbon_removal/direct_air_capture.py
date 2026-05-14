"""Direct Air Capture Economics"""
from typing import Dict

class DirectAirCapture:
    """DAC technology costs and market"""
    
    def technology_comparison(self) -> Dict:
        return {
            "climeworks": {
                "approach": "Solid sorbent",
                "cost_per_ton": 600,
                "target_2030": 300,
                "capacity_tons_year": 4000
            },
            "carbon_engineering": {
                "approach": "Liquid solvent",
                "cost_per_ton": 500,
                "partner": "1PointFive",
                "capacity_tons_year": 500000
            },
            "orbital_materials": {
                "approach": "Metal-organic frameworks",
                "status": "R&D",
                "cost_target": 100
            }
        }
    
    def cost_breakdown(self, tons_per_year: int = 10000) -> Dict:
        capex = 500e6  # $500M plant
        fixed_om = 50e6  # $50M/year
        variable_om_per_ton = 200  # Energy, chemicals
        energy_mwh_per_ton = 2.5
        energy_cost_per_mwh = 30
        
        energy_cost = energy_mwh_per_ton * energy_cost_per_mwh
        cost_per_ton = variable_om_per_ton + energy_cost + (fixed_om / tons_per_year)
        
        return {
            "capex": capex,
            "annual_fixed_costs": fixed_om,
            "variable_cost_per_ton": variable_om_per_ton + energy_cost,
            "total_cost_per_ton": cost_per_ton,
            "breakeven_carbon_price": cost_per_ton
        }
    
    def market_outlook(self) -> Dict:
        return {
            "current_market": 2e9,  # $2B
            "2030_projection": 50e9,
            "2050_need_gigatons": 10,  # Gt CO2/year
            "current_capacity_million_tons": 0.01,
            "price_per_ton_today": 600,
            "price_per_ton_2030": 150
        }
