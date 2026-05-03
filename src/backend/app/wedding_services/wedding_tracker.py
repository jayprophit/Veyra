"""Wedding Services Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class Wedding:
    wedding_id: str
    service_type: str
    revenue: float
    cost: float
    date: date

class WeddingTracker:
    def __init__(self, name: str = "Wedding"):
        self.name = name
        self.weddings: List[Wedding] = []
    
    def add(self, w: Wedding):
        self.weddings.append(w)
    
    def get_metrics(self) -> Dict:
        if not self.weddings:
            return {'status': 'NO_DATA'}
        rev = sum(w.revenue for w in self.weddings)
        cost = sum(w.cost for w in self.weddings)
        return {
            'business': self.name,
            'weddings': len(self.weddings),
            'revenue': round(rev, 2),
            'cost': round(cost, 2),
            'profit': round(rev - cost, 2),
            'margin': round((rev - cost) / rev * 100, 1) if rev else 0
        }

def analyze_weddings(data: List[Dict]) -> Dict:
    t = WeddingTracker()
    for d in data:
        t.add(Wedding(d['id'], d['service'], d['revenue'], d.get('cost', 0), d.get('date', date.today())))
    return t.get_metrics()
