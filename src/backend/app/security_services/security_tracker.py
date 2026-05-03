"""Security Services Tracker"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class SecurityJob:
    id: str
    client: str
    hours: float
    hourly_rate: float

class SecurityTracker:
    def __init__(self, name: str = "Security"):
        self.name = name
        self.jobs: List[SecurityJob] = []
    
    def add(self, j: SecurityJob):
        self.jobs.append(j)
    
    def get_metrics(self) -> Dict:
        hours = sum(j.hours for j in self.jobs)
        revenue = sum(j.hours * j.hourly_rate for j in self.jobs)
        return {
            'company': self.name,
            'jobs': len(self.jobs),
            'total_hours': round(hours, 1),
            'revenue': round(revenue, 2),
            'effective_rate': round(revenue / hours, 2) if hours else 0
        }

def analyze_security(data: List[Dict]) -> Dict:
    t = SecurityTracker()
    for d in data:
        t.add(SecurityJob(d['id'], d['client'], d['hours'], d['rate']))
    return t.get_metrics()
