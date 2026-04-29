"""Enhanced Geothermal Systems Economics"""
from typing import Dict

class EGSEconomics:
    """Analyze EGS project investments"""
    
    def __init__(self, capacity_mw: float, depth_m: float = 4000):
        self.capacity = capacity_mw
        self.depth = depth_m  # Drilling depth
    
    def drilling_cost(self) -> Dict:
        # Cost per meter increases with depth
        base_cost = 1000  # $/m for first 2000m
        deep_cost = 2000   # $/m beyond 2000m
        
        if self.depth <= 2000:
            cost = self.depth * base_cost
        else:
            cost = 2000 * base_cost + (self.depth - 2000) * deep_cost
        
        wells_needed = max(2, int(self.capacity / 5))  # 5MW per well pair
        total_drilling = cost * wells_needed
        
        return {
            "total_drilling_cost": round(total_drilling, 0),
            "cost_per_well": round(cost, 0),
            "wells_required": wells_needed,
            "depth": self.depth,
            "cost_per_kw": round(total_drilling / (self.capacity * 1000), 0)
        }
    
    def plant_capex(self) -> Dict:
        surface_plant = self.capacity * 1000 * 1500  # $1500/kW
        stimulation = self.capacity * 1000 * 500     # Reservoir stimulation
        
        drilling = self.drilling_cost()["total_drilling_cost"]
        total = surface_plant + drilling + stimulation
        
        return {
            "total_capex": round(total, 0),
            "surface_plant": round(surface_plant, 0),
            "drilling": round(drilling, 0),
            "stimulation": round(stimulation, 0),
            "cost_per_kw": round(total / (self.capacity * 1000), 0)
        }
    
    def lcoe(self, capacity_factor: float = 90) -> Dict:
        capex = self.plant_capex()["total_capex"]
        
        # Fixed charges
        fcr = 0.10
        annual_capital = capex * fcr
        
        # O&M
        om_fixed = self.capacity * 1000 * 100  # $100/kW-year
        
        # No fuel cost for geothermal
        total_annual = annual_capital + om_fixed
        generation = self.capacity * 8760 * (capacity_factor / 100)
        
        lcoe = total_annual / generation
        
        return {
            "lcoe_usd_per_mwh": round(lcoe, 2),
            "capacity_factor": capacity_factor,
            "annual_mwh": round(generation, 0),
            "capital_component_pct": round(annual_capital / total_annual * 100, 1)
        }
    
    vs_solar_wind(self, solar_lcoe: float = 40, wind_lcoe: float = 35) -> Dict:
        geo_lcoe = self.lcoe()["lcoe_usd_per_mwh"]
        
        # Value of baseload vs intermittent
        grid_value_premium = 20  # $/MWh for firm power
        effective_geo_cost = geo_lcoe - grid_value_premium
        
        return {
            "geothermal_lcoe": geo_lcoe,
            "solar_lcoe": solar_lcoe,
            "wind_lcoe": wind_lcoe,
            "premium_vs_solar": round(geo_lcoe - solar_lcoe, 2),
            "effective_cost_with_firm_value": round(effective_geo_cost, 2),
            "competitive": effective_geo_cost <= solar_lcoe
        }
