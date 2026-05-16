"""Auto Repair & Mechanic Shop Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class RepairJob:
    job_id: str
    service_type: str
    labor_revenue: float
    parts_revenue: float
    parts_cost: float
    labor_hours: float
    date: date

class MechanicShopTracker:
    def __init__(self, name: str = "Auto Shop"):
        self.name = name
        self.jobs: List[RepairJob] = []
    
    def add(self, j: RepairJob):
        self.jobs.append(j)
    
    def get_metrics(self) -> Dict:
        if not self.jobs:
            return {'status': 'NO_DATA'}
        labor_rev = sum(j.labor_revenue for j in self.jobs)
        parts_rev = sum(j.parts_revenue for j in self.jobs)
        parts_cost = sum(j.parts_cost for j in self.jobs)
        hours = sum(j.labor_hours for j in self.jobs)
        total_rev = labor_rev + parts_rev
        profit = total_rev - parts_cost
        return {
            'shop': self.name,
            'jobs': len(self.jobs),
            'labor_revenue': round(labor_rev, 2),
            'parts_revenue': round(parts_rev, 2),
            'total_revenue': round(total_rev, 2),
            'parts_cost': round(parts_cost, 2),
            'profit': round(profit, 2),
            'margin': round(profit / total_rev * 100, 1) if total_rev else 0,
            'total_hours': round(hours, 1),
            'labor_rate': round(labor_rev / hours, 2) if hours else 0
        }

def analyze_mechanic_shop(data: List[Dict]) -> Dict:
    t = MechanicShopTracker()
    for d in data:
        t.add(RepairJob(d['id'], d['type'], d['labor'], d.get('parts_rev', 0), d.get('parts_cost', 0), d.get('hours', 1), d.get('date', date.today())))
    return t.get_metrics()
