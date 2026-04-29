"""Anaerobic Digestion Economics"""
from typing import Dict

class AnaerobicDigestion:
    """Biogas production from organic waste"""
    
    def __init__(self, capacity_tons_per_day: float = 100):
        self.capacity = capacity_tons_per_day
    
    def plant_capex(self) -> Dict:
        cost_per_ton = 150000
        plant_cost = self.capacity * cost_per_ton
        return {
            "total_capex_millions": round(plant_cost / 1e6, 1),
            "per_ton_day": cost_per_ton,
            "annual_capacity_tons": self.capacity * 365
        }
    
    def revenue_streams(self) -> Dict:
        biogas_m3_per_ton = 100
        annual_biogas = self.capacity * 365 * biogas_m3_per_ton
        energy_mwh = annual_biogas * 0.006  # 6 kWh per m3
        
        energy_revenue = energy_mwh * 80
        digestate_value = self.capacity * 365 * 10
        carbon_credits = energy_mwh * 0.5 * 50  # 0.5 tCO2/MWh
        
        total = energy_revenue + digestate_value + carbon_credits
        
        return {
            "energy_revenue": round(energy_revenue, 0),
            "digestate_value": round(digestate_value, 0),
            "carbon_credits": round(carbon_credits, 0),
            "total": round(total, 0)
        }
