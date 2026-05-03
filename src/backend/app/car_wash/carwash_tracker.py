"""Car Wash & Detailing Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class CarWash:
    wash_id: str
    service_type: str  # 'basic', 'deluxe', 'detail'
    revenue: float
    soap_cost: float
    water_cost: float
    labor_minutes: int
    date: date

class CarWashTracker:
    def __init__(self, name: str = "Car Wash"):
        self.name = name
        self.washes: List[CarWash] = []
    
    def add(self, w: CarWash):
        self.washes.append(w)
    
    def get_metrics(self) -> Dict:
        if not self.washes:
            return {'status': 'NO_DATA'}
        revenue = sum(w.revenue for w in self.washes)
        costs = sum(w.soap_cost + w.water_cost for w in self.washes)
        return {
            'business': self.name,
            'washes': len(self.washes),
            'revenue': round(revenue, 2),
            'costs': round(costs, 2),
            'profit': round(revenue - costs, 2),
            'margin': round((revenue - costs) / revenue * 100, 1) if revenue else 0,
            'avg_per_wash': round(revenue / len(self.washes), 2)
        }

def analyze_carwash(data: List[Dict]) -> Dict:
    t = CarWashTracker()
    for d in data:
        t.add(CarWash(d['id'], d['type'], d['revenue'], d.get('soap', 0.50), d.get('water', 0.25), d.get('minutes', 15), d.get('date', date.today())))
    return t.get_metrics()
