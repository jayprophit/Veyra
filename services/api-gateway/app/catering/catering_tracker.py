"""Catering & Food Service Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class CateringEvent:
    event_id: str
    event_type: str  # 'wedding', 'corporate', 'private'
    guests: int
    price_per_guest: float
    food_cost: float
    staff_cost: float
    date: date

class CateringTracker:
    def __init__(self, name: str = "Catering"):
        self.name = name
        self.events: List[CateringEvent] = []
    
    def add(self, e: CateringEvent):
        self.events.append(e)
    
    def get_metrics(self) -> Dict:
        if not self.events:
            return {'status': 'NO_DATA'}
        guests = sum(e.guests for e in self.events)
        revenue = sum(e.guests * e.price_per_guest for e in self.events)
        costs = sum(e.food_cost + e.staff_cost for e in self.events)
        return {
            'business': self.name,
            'events': len(self.events),
            'total_guests': guests,
            'revenue': round(revenue, 2),
            'costs': round(costs, 2),
            'profit': round(revenue - costs, 2),
            'margin': round((revenue - costs) / revenue * 100, 1) if revenue else 0,
            'avg_event_size': round(guests / len(self.events), 0),
            'price_per_guest': round(revenue / guests, 2) if guests else 0
        }

def analyze_catering(data: List[Dict]) -> Dict:
    t = CateringTracker()
    for d in data:
        t.add(CateringEvent(d['id'], d['type'], d['guests'], d['price'], d.get('food_cost', 0), d.get('staff', 0), d.get('date', date.today())))
    return t.get_metrics()
