"""Battery Manufacturing Economics"""
from typing import Dict

class BatteryManufacturing:
    """Analyze gigafactory investments and cell production economics"""
    
    def __init__(self, annual_capacity_gwh: float = 35):
        self.capacity_gwh = annual_capacity_gwh
    
    def factory_capex(self, location: str = "united_states") -> Dict:
        costs_per_gwh = {
            "china": 50e6,
            "united_states": 100e6,
            "europe": 90e6
        }
        
        cost_per_gwh = costs_per_gwh.get(location, 100e6)
        equipment_cost = self.capacity_gwh * cost_per_gwh
        
        # Building, utilities, soft costs
        building = equipment_cost * 0.30
        utilities = equipment_cost * 0.15
        soft_costs = equipment_cost * 0.10
        
        total = equipment_cost + building + utilities + soft_costs
        
        return {
            "total_capex_millions": round(total / 1e6, 0),
            "per_gwh_capacity": round(cost_per_gwh / 1e6, 0),
            "equipment": round(equipment_cost / 1e6, 0),
            "building": round(building / 1e6, 0),
            "jobs_created": int(self.capacity_gwh * 100)
        }
    
    def unit_economics(self, cell_format: str = "4680") -> Dict:
        # Cost per kWh at cell level
        material_costs = {
            "cathode": 60,  # $/kWh
            "anode": 15,
            "electrolyte": 8,
            "separator": 5,
            "current_collectors": 7,
            "other_materials": 15
        }
        
        materials = sum(material_costs.values())
        labor = 8
        energy = 5
        depreciation = 12
        other = 10
        
        total_cost = materials + labor + energy + depreciation + other
        selling_price = 120  # $/kWh
        margin = selling_price - total_cost
        
        return {
            "cell_cost_per_kwh": round(total_cost, 0),
            "selling_price_per_kwh": selling_price,
            "gross_margin_per_kwh": round(margin, 0),
            "gross_margin_pct": round(margin / selling_price * 100, 1),
            "material_breakdown": material_costs
        }
    
    def factory_economics(self, utilization: float = 0.80) -> Dict:
        capex = self.factory_capex()["total_capex_millions"] * 1e6
        unit = self.unit_economics()
        
        annual_output = self.capacity_gwh * 1e6 * utilization  # kWh
        revenue = annual_output * unit["selling_price_per_kwh"] / 1e6  # $M
        cogs = annual_output * unit["cell_cost_per_kwh"] / 1e6
        
        gross_profit = revenue - cogs
        
        # OpEx
        r_and_d = revenue * 0.08
        sga = revenue * 0.12
        
        ebitda = gross_profit - r_and_d - sga
        
        return {
            "annual_revenue_millions": round(revenue, 0),
            "annual_cogs_millions": round(cogs, 0),
            "gross_profit_millions": round(gross_profit, 0),
            "ebitda_millions": round(ebitda, 0),
            "ebitda_margin_pct": round(ebitda / revenue * 100, 1),
            "utilization_rate": utilization
        }
    
    def market_position(self, market_share_target: float = 0.10) -> Dict:
        # Global battery demand
        total_demand_2030 = 3500  # GWh
        target_production = total_demand_2030 * market_share_target
        
        factories_needed = target_production / self.capacity_gwh
        
        factory_capex = self.factory_capex()["total_capex_millions"]
        total_investment = factories_needed * factory_capex
        
        return {
            "global_demand_2030_gwh": total_demand_2030,
            "target_market_share_pct": market_share_target * 100,
            "target_production_gwh": target_production,
            "factories_needed": round(factories_needed, 0),
            "total_investment_billions": round(total_investment / 1000, 1)
        }
