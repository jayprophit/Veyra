"""Satellite Manufacturing Economics"""
from typing import Dict

class SatelliteManufacturing:
    """Analyze satellite production costs and economics"""
    
    def __init__(self, satellite_type: str = "small"):
        self.sat_type = satellite_type  # small, medium, large, constellation
    
    def manufacturing_cost(self, quantity: int = 1) -> Dict:
        base_costs = {
            "cubesat": {"base": 50000, "components": 30000},
            "small": {"base": 500000, "components": 300000},
            "medium": {"base": 5000000, "components": 3000000},
            "large": {"base": 50000000, "components": 30000000}
        }
        
        base = base_costs.get(self.sat_type, base_costs["small"])
        total_base = base["base"] + base["components"]
        
        # Learning curve effect
        learning_rate = 0.90  # 10% cost reduction per doubling
        doublings = quantity.bit_length() - 1
        multiplier = learning_rate ** doublings
        
        unit_cost = total_base * multiplier
        total_program_cost = unit_cost * quantity
        
        return {
            "unit_cost": round(unit_cost, 0),
            "total_program_cost": round(total_program_cost, 0),
            "quantity": quantity,
            "learning_curve_discount": round((1 - multiplier) * 100, 1),
            "base_cost_no_learning": total_base
        }
    
    def component_breakdown(self) -> Dict:
        return {
            "bus_structure": 0.15,
            "power_system": 0.20,
            "propulsion": 0.10,
            "avionics": 0.25,
            "payload": 0.20,
            "thermal": 0.10
        }
    
    def market_analysis(self) -> Dict:
        return {
            "annual_satellites_launched": 2500,
            "market_size_billions": 30,
            "growth_rate": 0.15,
            "constellation_drivers": ["Starlink", "OneWeb", "Kuiper"],
            "manufacturing_leaders": ["Airbus", "Lockheed Martin", "Boeing", "Northrop Grumman"],
            "new_entrants": ["Terran Orbital", "Rocket Lab", "Momentus"]
        }
    
    def factory_economics(self, annual_capacity: int = 100) -> Dict:
        # Satellite factory investment
        factory_capex = 100e6  # $100M for modern satellite factory
        
        avg_satellite_value = 2e6  # $2M average
        annual_output_value = annual_capacity * avg_satellite_value
        
        margin = 0.20
        annual_profit = annual_output_value * margin
        
        return {
            "factory_capex_millions": factory_capex / 1e6,
            "annual_capacity": annual_capacity,
            "annual_output_value_millions": annual_output_value / 1e6,
            "annual_profit_millions": annual_profit / 1e6,
            "payback_years": round(factory_capex / annual_profit, 1),
            "utilization_for_profit": "70%+"
        }
