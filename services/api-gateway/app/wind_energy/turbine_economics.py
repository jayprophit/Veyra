"""Turbine Economics - Wind turbine investment analysis"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class TurbineSpecs:
    capacity_mw: float
    hub_height_m: float
    rotor_diameter_m: float
    capacity_factor: float
    lifespan_years: int = 25

class TurbineEconomics:
    """Analyze wind turbine investments"""
    
    def __init__(self, turbine: TurbineSpecs, cost_per_mw: float = 1.3e6):
        self.turbine = turbine
        self.cost_per_mw = cost_per_mw
    
    def annual_energy_output(self) -> float:
        """Calculate annual MWh production"""
        hours_per_year = 8760
        return self.turbine.capacity_mw * hours_per_year * (self.turbine.capacity_factor / 100)
    
    def capital_cost(self) -> Dict:
        """Calculate total capital expenditure"""
        turbine_cost = self.turbine.capacity_mw * self.cost_per_mw
        installation = turbine_cost * 0.15  # 15% installation
        grid_connection = turbine_cost * 0.10  # 10% grid
        
        total = turbine_cost + installation + grid_connection
        
        return {
            "turbine_cost": round(turbine_cost, 0),
            "installation": round(installation, 0),
            "grid_connection": round(grid_connection, 0),
            "total_capex": round(total, 0),
            "cost_per_kw": round(total / (self.turbine.capacity_mw * 1000), 0)
        }
    
    def lcoe(self, opex_per_mwh: float = 25, discount_rate: float = 0.06) -> Dict:
        """Calculate Levelized Cost of Energy"""
        capex = self.capital_cost()["total_capex"]
        annual_output = self.annual_energy_output()
        
        # O&M costs
        annual_opex = annual_output * opex_per_mwh
        
        # NPV of costs
        total_npv_costs = capex
        for year in range(1, self.turbine.lifespan_years + 1):
            total_npv_costs += annual_opex / ((1 + discount_rate) ** year)
        
        # NPV of energy production
        total_npv_energy = sum(
            annual_output / ((1 + discount_rate) ** year)
            for year in range(1, self.turbine.lifespan_years + 1)
        )
        
        lcoe_value = total_npv_costs / total_npv_energy if total_npv_energy > 0 else 0
        
        return {
            "lcoe_usd_per_mwh": round(lcoe_value, 2),
            "annual_output_mwh": round(annual_output, 0),
            "annual_opex": round(annual_opex, 0),
            "capacity_factor": self.turbine.capacity_factor
        }
    
    def revenue_projection(self, ppa_price_per_mwh: float, years: int = 25) -> Dict:
        """Project revenue with inflation"""
        annual_output = self.annual_energy_output()
        inflation_rate = 0.02
        
        revenues = []
        for year in range(1, years + 1):
            price = ppa_price_per_mwh * ((1 + inflation_rate) ** (year - 1))
            revenue = annual_output * price
            revenues.append({"year": year, "revenue": round(revenue, 0), "price": round(price, 2)})
        
        total_revenue = sum(r["revenue"] for r in revenues)
        
        return {
            "revenues": revenues[:5],  # First 5 years
            "total_25yr_revenue": round(total_revenue, 0),
            "avg_annual_revenue": round(total_revenue / years, 0)
        }
