"""Photography & Video Business Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class PhotoShoot:
    shoot_id: str
    shoot_type: str
    revenue: float
    equipment: float
    editing: float
    date: date

class PhotoBusinessTracker:
    def __init__(self, name: str = "Photo Studio"):
        self.name = name
        self.shoots: List[PhotoShoot] = []
    
    def add(self, s: PhotoShoot):
        self.shoots.append(s)
    
    def get_metrics(self) -> Dict:
        if not self.shoots:
            return {'status': 'NO_DATA'}
        rev = sum(s.revenue for s in self.shoots)
        costs = sum(s.equipment + s.editing for s in self.shoots)
        return {
            'studio': self.name,
            'shoots': len(self.shoots),
            'revenue': round(rev, 2),
            'costs': round(costs, 2),
            'profit': round(rev - costs, 2),
            'margin': round((rev - costs) / rev * 100, 1) if rev else 0
        }

def analyze_photo_business(data: List[Dict]) -> Dict:
    t = PhotoBusinessTracker()
    for d in data:
        t.add(PhotoShoot(d['id'], d['type'], d['revenue'], d.get('equipment', 0), d.get('editing', 0), d.get('date', date.today())))
    return t.get_metrics()
