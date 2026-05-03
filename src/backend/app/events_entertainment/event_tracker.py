"""Event Planner Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class Event:
    event_id: str
    event_type: str
    revenue: float
    costs: float
    date: date

class EventTracker:
    def __init__(self, name: str = "Events"):
        self.name = name
        self.events: List[Event] = []
    
    def add(self, e: Event):
        self.events.append(e)
    
    def get_metrics(self) -> Dict:
        if not self.events:
            return {'status': 'NO_DATA'}
        rev = sum(e.revenue for e in self.events)
        costs = sum(e.costs for e in self.events)
        return {
            'company': self.name,
            'events': len(self.events),
            'revenue': round(rev, 2),
            'costs': round(costs, 2),
            'profit': round(rev - costs, 2),
            'margin': round((rev - costs) / rev * 100, 1) if rev else 0
        }

def analyze_events(data: List[Dict]) -> Dict:
    t = EventTracker()
    for d in data:
        t.add(Event(d['id'], d['type'], d['revenue'], d.get('costs', 0), d.get('date', date.today())))
    return t.get_metrics()
