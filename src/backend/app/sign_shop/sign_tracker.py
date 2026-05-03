"""Sign Shop & Graphics Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class SignJob:
    job_id: str
    sign_type: str  # 'vinyl', 'channel', 'banner'
    size_sqft: float
    price_per_sqft: float
    material_cost: float
    labor_hours: float
    date: date

class SignShopTracker:
    def __init__(self, name: str = "Sign Shop"):
        self.name = name
        self.jobs: List[SignJob] = []
    
    def add(self, j: SignJob):
        self.jobs.append(j)
    
    def get_metrics(self) -> Dict:
        if not self.jobs:
            return {'status': 'NO_DATA'}
        revenue = sum(j.size_sqft * j.price_per_sqft for j in self.jobs)
        costs = sum(j.material_cost for j in self.jobs)
        labor = sum(j.labor_hours for j in self.jobs)
        return {
            'shop': self.name,
            'jobs': len(self.jobs),
            'revenue': round(revenue, 2),
            'material_costs': round(costs, 2),
            'profit': round(revenue - costs, 2),
            'margin': round((revenue - costs) / revenue * 100, 1) if revenue else 0,
            'total_labor_hours': round(labor, 1)
        }

def analyze_sign_shop(data: List[Dict]) -> Dict:
    t = SignShopTracker()
    for d in data:
        t.add(SignJob(d['id'], d['type'], d['size'], d.get('price', 15), d.get('cost', 0), d.get('hours', 0), d.get('date', date.today())))
    return t.get_metrics()
