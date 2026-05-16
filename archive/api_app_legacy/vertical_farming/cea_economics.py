"""Controlled Environment Agriculture Economics"""
from typing import Dict

class ControlledEnvironmentEconomics:
    """Analyze vertical farming facility investments"""
    
    def __init__(self, facility_sqm: float, crop_type: str = "leafy_greens"):
        self.area = facility_sqm
        self.crop = crop_type
    
    def capex_analysis(self) -> Dict:
        # $ per sqm for different system types
        costs = {
            "leafy_greens": 1500,
            "tomatoes": 2000,
            "strawberries": 2500,
            "herbs": 1200,
            "microgreens": 800
        }
        
        cost_per_sqm = costs.get(self.crop, 1500)
        total = self.area * cost_per_sqm
        
        return {
            "total_capex": round(total, 0),
            "per_sqm": cost_per_sqm,
            "breakdown": {
                "hvac": round(total * 0.25, 0),
                "lighting": round(total * 0.30, 0),
                "racking": round(total * 0.20, 0),
                "automation": round(total * 0.15, 0),
                "other": round(total * 0.10, 0)
            }
        }
    
    def production_economics(self) -> Dict:
        # Yields vs traditional farming
        yield_multipliers = {
            "leafy_greens": 350,
            "tomatoes": 20,
            "strawberries": 15,
            "herbs": 100,
            "microgreens": 500
        }
        
        multiplier = yield_multipliers.get(self.crop, 100)
        
        # Energy costs (major opex driver)
        energy_kwh_per_kg = 3.5 if self.crop == "leafy_greens" else 5.0
        electricity_price = 0.10  # $/kWh
        
        # Annual production per sqm
        annual_kg_per_sqm = {
            "leafy_greens": 50,
            "tomatoes": 40,
            "strawberries": 15,
            "herbs": 25,
            "microgreens": 100
        }.get(self.crop, 30)
        
        total_annual_kg = annual_kg_per_sqm * self.area
        energy_cost_annual = total_annual_kg * energy_kwh_per_kg * electricity_price
        
        return {
            "annual_production_kg": round(total_annual_kg, 0),
            "vs_traditional_multiplier": multiplier,
            "energy_cost_annual": round(energy_cost_annual, 0),
            "energy_cost_per_kg": round(energy_kwh_per_kg * electricity_price, 2)
        }
    
    def profitability_analysis(self, wholesale_price_per_kg: float) -> Dict:
        production = self.production_economics()
        capex = self.capex_analysis()
        
        revenue = production["annual_production_kg"] * wholesale_price_per_kg
        
        # Operating costs
        energy = production["energy_cost_annual"]
        labor = revenue * 0.25
        inputs = revenue * 0.10
        maintenance = revenue * 0.05
        
        total_opex = energy + labor + inputs + maintenance
        ebitda = revenue - total_opex
        
        # Simple payback
        payback = capex["total_capex"] / ebitda if ebitda > 0 else float('inf')
        
        return {
            "annual_revenue": round(revenue, 0),
            "annual_ebitda": round(ebitda, 0),
            "ebitda_margin": round(ebitda / revenue * 100, 1),
            "payback_years": round(payback, 1),
            "profitable": ebitda > 0
        }
    
    def vs_field_farming(self, field_yield_per_hectare: float, field_cost_per_kg: float) -> Dict:
        # Compare to traditional agriculture
        production = self.production_economics()
        
        # Land use efficiency
        sqm_per_hectare = 10000
        vertical_yield_per_hectare = production["annual_production_kg"] * (sqm_per_hectare / self.area)
        
        land_efficiency = vertical_yield_per_hectare / field_yield_per_hectare
        
        # Cost comparison
        vertical_cost = self.profitability_analysis(3.0)["annual_ebitda"]  # Using sample price
        cost_premium = (production["energy_cost_per_kg"] / field_cost_per_kg - 1) * 100
        
        return {
            "land_use_efficiency": round(land_efficiency, 0),
            "vertical_yield_per_hectare": round(vertical_yield_per_hectare, 0),
            "water_savings_pct": 95,
            "pesticide_free": True,
            "cost_premium_pct": round(cost_premium, 0)
        }
