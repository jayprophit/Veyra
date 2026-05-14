"""Water Treatment Economics"""
from typing import Dict

class WaterTreatment:
    """Municipal and industrial water treatment"""
    
    def __init__(self, capacity_m3_per_day: float = 50000):
        self.capacity = capacity_m3_per_day
    
    def treatment_capex(self) -> Dict:
        cost_per_m3 = 800
        total = self.capacity * cost_per_m3
        return {
            "total_capex_millions": round(total / 1e6, 1),
            "per_m3_day": cost_per_m3
        }
    
    def operating_metrics(self) -> Dict:
        cost_per_m3 = 0.50
        annual_volume = self.capacity * 365
        opex = annual_volume * cost_per_m3
        
        return {
            "cost_per_m3": cost_per_m3,
            "annual_opex_millions": round(opex / 1e6, 1)
        }
