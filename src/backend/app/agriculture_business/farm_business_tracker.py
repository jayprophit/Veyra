"""Farm & Agriculture Business Tracker"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date

@dataclass
class FarmHarvest:
    harvest_id: str
    crop_type: str
    quantity: float
    unit_price: float
    input_costs: float
    date: date

class FarmBusinessTracker:
    def __init__(self, name: str = "Farm"):
        self.name = name
        self.harvests: List[FarmHarvest] = []
    
    def add_harvest(self, h: FarmHarvest):
        self.harvests.append(h)
    
    def get_farm_metrics(self) -> Dict:
        if not self.harvests:
            return {'status': 'NO_DATA'}
        revenue = sum(h.quantity * h.unit_price for h in self.harvests)
        costs = sum(h.input_costs for h in self.harvests)
        profit = revenue - costs
        by_crop = {}
        for h in self.harvests:
            c = h.crop_type
            if c not in by_crop:
                by_crop[c] = {'revenue': 0, 'costs': 0}
            by_crop[c]['revenue'] += h.quantity * h.unit_price
            by_crop[c]['costs'] += h.input_costs
        return {
            'farm': self.name,
            'total_revenue': round(revenue, 2),
            'total_costs': round(costs, 2),
            'profit': round(profit, 2),
            'margin_pct': round(profit / revenue * 100, 1) if revenue else 0,
            'by_crop': by_crop,
            'harvests': len(self.harvests)
        }

def analyze_farm(harvests: List[Dict]) -> Dict:
    t = FarmBusinessTracker()
    for h in harvests:
        t.add_harvest(FarmHarvest(h['id'], h['crop'], h['quantity'], h['price'], h.get('costs', 0), h.get('date', date.today())))
    return t.get_farm_metrics()
