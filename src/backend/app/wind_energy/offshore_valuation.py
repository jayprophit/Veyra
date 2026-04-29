"""Offshore Wind Valuation - Marine wind farm investments"""
from typing import Dict

class OffshoreValuation:
    """Analyze offshore wind farm investments"""
    
    def __init__(self, capacity_mw: float, water_depth_m: float, distance_to_shore_km: float):
        self.capacity_mw = capacity_mw
        self.depth = water_depth_m
        self.distance = distance_to_shore_km
    
    def foundation_cost(self) -> Dict:
        if self.depth < 30:
            cost_per_mw = 2.5e6  # Fixed bottom
            foundation_type = "Fixed Bottom (Monopile)"
        elif self.depth < 60:
            cost_per_mw = 3.5e6  # Jacket
            foundation_type = "Jacket Foundation"
        else:
            cost_per_mw = 5.0e6  # Floating
            foundation_type = "Floating Platform"
        
        return {
            "type": foundation_type,
            "cost_per_mw": cost_per_mw,
            "total_foundation": cost_per_mw * self.capacity_mw
        }
    
    def transmission_cost(self) -> float:
        ac_cost = 0.5e6 * self.distance  # AC for <50km
        dc_cost = 0.8e6 * self.distance  # DC for >50km
        return ac_cost if self.distance < 50 else dc_cost
    
    def total_capex(self) -> Dict:
        foundation = self.foundation_cost()
        turbine = self.capacity_mw * 1.5e6
        transmission = self.transmission_cost()
        installation = self.capacity_mw * 0.5e6
        
        total = foundation["total_foundation"] + turbine + transmission + installation
        
        return {
            "total_capex": total,
            "per_mw": total / self.capacity_mw,
            "breakdown": {
                "turbines": turbine,
                "foundation": foundation["total_foundation"],
                "transmission": transmission,
                "installation": installation
            }
        }
