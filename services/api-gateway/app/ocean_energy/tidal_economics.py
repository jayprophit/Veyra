"""Tidal Energy Economics"""
from typing import Dict

class TidalEconomics:
    """Analyze tidal barrage and stream projects"""
    
    def __init__(self, capacity_mw: float, resource_type: str = "stream"):
        self.capacity = capacity_mw
        self.resource = resource_type  # stream or barrage
    
    def capex_analysis(self) -> Dict:
        if self.resource == "barrage":
            cost_per_kw = 5000  # High civil works
        else:
            cost_per_kw = 6000   # Tidal stream turbines
        
        total = self.capacity * 1000 * cost_per_kw
        
        return {
            "total_capex": round(total, 0),
            "cost_per_kw": cost_per_kw,
            "resource_type": self.resource,
            "turbine_cost_share": 0.40 if self.resource == "stream" else 0.30,
            "civil_works_share": 0.50 if self.resource == "barrage" else 0.35
        }
    
    def lcoe(self, capacity_factor: float = 25) -> Dict:
        capex = self.capex_analysis()["total_capex"]
        
        annual_gen = self.capacity * 8760 * (capacity_factor / 100)
        
        # High O&M for marine environment
        fcr = 0.10
        om = self.capacity * 1000 * 200  # $200/kW-year
        
        total_annual = capex * fcr + om
        lcoe = total_annual / annual_gen if annual_gen > 0 else 0
        
        return {
            "lcoe_usd_per_mwh": round(lcoe, 2),
            "capacity_factor": capacity_factor,
            "annual_mwh": round(annual_gen, 0),
            "predictable_output": True,  # Tidal is highly predictable
            "grid_value": "High reliability"
        }
    
    def site_assessment(self, tidal_range_m: float = 5, basin_area_sqkm: float = 10) -> Dict:
        # Tidal barrage potential
        density = 1025  # kg/m3 seawater
        g = 9.81
        
        # Potential energy per tidal cycle
        volume = basin_area_sqkm * 1e6 * tidal_range_m  # m3
        energy_per_cycle = 0.5 * density * volume * g * tidal_range_m  # Joules
        
        # Two cycles per day
        annual_cycles = 705  # 365 * 2 * 0.97 (efficiency)
        annual_mwh = energy_per_cycle * annual_cycles / (3.6e9)
        
        implied_capacity = annual_mwh / (8760 * 0.25)  # Assuming 25% CF
        
        return {
            "potential_annual_mwh": round(annual_mwh, 0),
            "implied_capacity_mw": round(implied_capacity, 1),
            "tidal_range": tidal_range_m,
            "basin_area": basin_area_sqkm,
            "development_viable": tidal_range_m >= 5
        }
