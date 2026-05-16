"""Gym Business Tracker"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Member:
    id: str
    fee: float
    status: str

class GymTracker:
    def __init__(self, name: str = "Gym"):
        self.name = name
        self.members: List[Member] = []
    
    def add(self, m: Member):
        self.members.append(m)
    
    def get_metrics(self) -> Dict:
        active = [m for m in self.members if m.status == 'active']
        revenue = sum(m.fee for m in active)
        return {
            'gym': self.name,
            'active_members': len(active),
            'monthly_revenue': round(revenue, 2),
            'annual_projection': round(revenue * 12, 2)
        }

def analyze_gym(data: List[Dict]) -> Dict:
    t = GymTracker()
    for d in data:
        t.add(Member(d['id'], d['fee'], d.get('status', 'active')))
    return t.get_metrics()
