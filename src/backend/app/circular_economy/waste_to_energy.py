"""Waste to Energy - WTE facility economics"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class WTEFacility:
    facility_id: str
    capacity_mw: float
    waste_processed_tons_per_year: float
    electricity_generated_mwh: float
    revenue_per_mwh: float
    operating_cost_per_year: float

class WasteToEnergy:
    def __init__(self):
        self.facilities: List[WTEFacility] = []
    
    def add(self, f: WTEFacility):
        self.facilities.append(f)
    
    def calculate_profitability(self, f: WTEFacility) -> Dict:
        revenue = f.electricity_generated_mwh * f.revenue_per_mwh
        profit = revenue - f.operating_cost_per_year
        return {
            'facility_id': f.facility_id,
            'revenue': round(revenue, 2),
            'operating_cost': round(f.operating_cost_per_year, 2),
            'profit': round(profit, 2),
            'margin_pct': round(profit / revenue * 100, 1) if revenue else 0
        }
    
    def get_summary(self) -> Dict:
        if not self.facilities:
            return {'status': 'NO_FACILITIES'}
        return {
            'facilities': len(self.facilities),
            'total_capacity_mw': round(sum(f.capacity_mw for f in self.facilities), 1),
            'total_waste_processed': round(sum(f.waste_processed_tons_per_year for f in self.facilities), 0),
            'total_electricity_mwh': round(sum(f.electricity_generated_mwh for f in self.facilities), 0)
        }
