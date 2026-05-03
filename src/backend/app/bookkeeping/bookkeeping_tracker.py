"""Bookkeeping Services Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class BookkeepingClient:
    client_id: str
    monthly_fee: float
    hours_per_month: float
    status: str

class BookkeepingTracker:
    def __init__(self, name: str = "Bookkeeping"):
        self.name = name
        self.clients: List[BookkeepingClient] = []
    
    def add(self, c: BookkeepingClient):
        self.clients.append(c)
    
    def get_metrics(self) -> Dict:
        if not self.clients:
            return {'status': 'NO_DATA'}
        active = [c for c in self.clients if c.status == 'active']
        revenue = sum(c.monthly_fee for c in active)
        hours = sum(c.hours_per_month for c in active)
        return {
            'business': self.name,
            'clients': len(active),
            'monthly_revenue': round(revenue, 2),
            'annual_revenue': round(revenue * 12, 2),
            'total_hours': round(hours, 1),
            'effective_rate': round(revenue / hours, 2) if hours else 0
        }

def analyze_bookkeeping(data: List[Dict]) -> Dict:
    t = BookkeepingTracker()
    for d in data:
        t.add(BookkeepingClient(d['id'], d['fee'], d.get('hours', 4), d.get('status', 'active')))
    return t.get_metrics()
