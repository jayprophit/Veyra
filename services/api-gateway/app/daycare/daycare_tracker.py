"""Daycare & Childcare Tracker"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Child:
    id: str
    weekly_fee: float
    status: str

class DaycareTracker:
    def __init__(self, name: str = "Daycare"):
        self.name = name
        self.children: List[Child] = []
    
    def add(self, c: Child):
        self.children.append(c)
    
    def get_metrics(self) -> Dict:
        enrolled = [c for c in self.children if c.status == 'enrolled']
        weekly = sum(c.weekly_fee for c in enrolled)
        return {
            'daycare': self.name,
            'enrolled': len(enrolled),
            'weekly_revenue': round(weekly, 2),
            'monthly_revenue': round(weekly * 4.3, 2)
        }

def analyze_daycare(data: List[Dict]) -> Dict:
    t = DaycareTracker()
    for d in data:
        t.add(Child(d['id'], d['fee'], d.get('status', 'enrolled')))
    return t.get_metrics()
