"""Cleaning Services Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class CleaningJob:
    job_id: str
    job_type: str
    revenue: float
    labor_cost: float
    supplies: float
    date: date

class CleaningTracker:
    def __init__(self, name: str = "Cleaning"):
        self.name = name
        self.jobs: List[CleaningJob] = []
    
    def add(self, j: CleaningJob):
        self.jobs.append(j)
    
    def get_metrics(self) -> Dict:
        if not self.jobs:
            return {'status': 'NO_DATA'}
        rev = sum(j.revenue for j in self.jobs)
        costs = sum(j.labor_cost + j.supplies for j in self.jobs)
        return {
            'company': self.name,
            'jobs': len(self.jobs),
            'revenue': round(rev, 2),
            'costs': round(costs, 2),
            'profit': round(rev - costs, 2),
            'margin': round((rev - costs) / rev * 100, 1) if rev else 0
        }

def analyze_cleaning(data: List[Dict]) -> Dict:
    t = CleaningTracker()
    for d in data:
        t.add(CleaningJob(d['id'], d['type'], d['revenue'], d.get('labor', 0), d.get('supplies', 0), d.get('date', date.today())))
    return t.get_metrics()
