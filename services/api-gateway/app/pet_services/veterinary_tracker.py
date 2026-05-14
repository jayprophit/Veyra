"""Pet Services & Veterinary Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class PetVisit:
    visit_id: str
    service_type: str
    revenue: float
    supplies: float
    date: date

class PetServicesTracker:
    def __init__(self, name: str = "Pet Services"):
        self.name = name
        self.visits: List[PetVisit] = []
    
    def add(self, v: PetVisit):
        self.visits.append(v)
    
    def get_metrics(self) -> Dict:
        if not self.visits:
            return {'status': 'NO_DATA'}
        rev = sum(v.revenue for v in self.visits)
        costs = sum(v.supplies for v in self.visits)
        return {
            'company': self.name,
            'visits': len(self.visits),
            'revenue': round(rev, 2),
            'costs': round(costs, 2),
            'profit': round(rev - costs, 2),
            'margin': round((rev - costs) / rev * 100, 1) if rev else 0
        }

def analyze_pet_services(data: List[Dict]) -> Dict:
    t = PetServicesTracker()
    for d in data:
        t.add(PetVisit(d['id'], d['service'], d['revenue'], d.get('supplies', 0), d.get('date', date.today())))
    return t.get_metrics()
