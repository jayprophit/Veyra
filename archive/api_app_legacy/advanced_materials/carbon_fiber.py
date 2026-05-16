"""Carbon Fiber Economics"""
from typing import Dict

class CarbonFiber:
    """Analyze carbon fiber manufacturing and markets"""
    
    def __init__(self, fiber_type: str = "standard"):
        self.fiber_type = fiber_type  # standard, intermediate, high_modulus
    
    def production_economics(self, plant_capacity_tons: float = 3000) -> Dict:
        costs = {
            "standard": {"precursor_cost": 3.00, "conversion_cost": 4.00, "selling_price": 15.00},
            "intermediate": {"precursor_cost": 4.00, "conversion_cost": 6.00, "selling_price": 25.00},
            "high_modulus": {"precursor_cost": 8.00, "conversion_cost": 15.00, "selling_price": 80.00}
        }
        
        c = costs.get(self.fiber_type, costs["standard"])
        
        total_cost_per_kg = c["precursor_cost"] + c["conversion_cost"]
        margin_per_kg = c["selling_price"] - total_cost_per_kg
        
        annual_revenue = plant_capacity_tons * 1000 * c["selling_price"]
        annual_profit = plant_capacity_tons * 1000 * margin_per_kg
        
        # Plant capex
        capex_per_ton = 10000  # $10M per 1000 tons
        plant_capex = plant_capacity_tons * capex_per_ton
        
        return {
            "fiber_type": self.fiber_type,
            "plant_capacity_tons": plant_capacity_tons,
            "cost_per_kg": total_cost_per_kg,
            "selling_price_per_kg": c["selling_price"],
            "margin_per_kg": margin_per_kg,
            "margin_pct": round(margin_per_kg / c["selling_price"] * 100, 1),
            "annual_revenue_millions": annual_revenue / 1e6,
            "annual_profit_millions": annual_profit / 1e6,
            "plant_capex_millions": plant_capex / 1e6,
            "payback_years": round(plant_capex / annual_profit, 1)
        }
    
    def end_use_markets(self) -> Dict:
        return {
            "aerospace": {"volume_kt": 25, "price_premium": 2.0, "growth_rate": 0.08},
            "automotive": {"volume_kt": 15, "price_premium": 1.0, "growth_rate": 0.15},
            "wind_energy": {"volume_kt": 35, "price_premium": 0.8, "growth_rate": 0.12},
            "sports": {"volume_kt": 10, "price_premium": 1.2, "growth_rate": 0.05},
            "pressure_vessels": {"volume_kt": 8, "price_premium": 1.0, "growth_rate": 0.20}
        }
    
    def vs_alternatives(self, application: str = "automotive") -> Dict:
        return {
            "carbon_fiber": {"weight": 1.0, "strength": 10.0, "cost": 15.00},
            "steel": {"weight": 8.0, "strength": 1.0, "cost": 2.00},
            "aluminum": {"weight": 3.0, "strength": 0.5, "cost": 4.00},
            "fiberglass": {"weight": 2.5, "strength": 2.0, "cost": 3.00},
            "application": application,
            "weight_savings": "60-70% vs steel"
        }
