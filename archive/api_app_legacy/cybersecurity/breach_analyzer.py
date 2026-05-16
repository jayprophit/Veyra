"""Breach Analyzer - Data breach impact analysis"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

@dataclass
class DataBreach:
    breach_id: str
    company: str
    records_exposed: int
    cost_per_record: float
    detection_date: datetime
    industry: str

class BreachAnalyzer:
    def __init__(self):
        self.breaches: List[DataBreach] = []
    
    def add(self, b: DataBreach):
        self.breaches.append(b)
    
    def calculate_impact(self, b: DataBreach) -> Dict:
        direct_cost = b.records_exposed * b.cost_per_record
        notification_cost = b.records_exposed * 0.50  # $0.50 per notification
        return {
            'breach_id': b.breach_id,
            'company': b.company,
            'records': b.records_exposed,
            'direct_cost': round(direct_cost, 2),
            'notification_cost': round(notification_cost, 2),
            'total_estimated': round(direct_cost + notification_cost, 2)
        }
    
    def get_summary(self) -> Dict:
        if not self.breaches:
            return {'status': 'NO_DATA'}
        impacts = [self.calculate_impact(b) for b in self.breaches]
        return {
            'total_breaches': len(self.breaches),
            'total_records': sum(b.records_exposed for b in self.breaches),
            'total_cost': round(sum(i['total_estimated'] for i in impacts), 2)
        }
