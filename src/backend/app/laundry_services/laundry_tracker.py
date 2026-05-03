"""Laundry & Dry Cleaning Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class LaundryOrder:
    order_id: str
    service_type: str
    weight_lbs: float
    price_per_lb: float
    detergent_cost: float
    date: date

class LaundryTracker:
    def __init__(self, name: str = "Laundry"):
        self.name = name
        self.orders: List[LaundryOrder] = []
    
    def add(self, o: LaundryOrder):
        self.orders.append(o)
    
    def get_metrics(self) -> Dict:
        if not self.orders:
            return {'status': 'NO_DATA'}
        weight = sum(o.weight_lbs for o in self.orders)
        revenue = sum(o.weight_lbs * o.price_per_lb for o in self.orders)
        costs = sum(o.detergent_cost for o in self.orders)
        return {
            'business': self.name,
            'orders': len(self.orders),
            'total_weight_lbs': round(weight, 1),
            'revenue': round(revenue, 2),
            'costs': round(costs, 2),
            'profit': round(revenue - costs, 2),
            'margin': round((revenue - costs) / revenue * 100, 1) if revenue else 0,
            'price_per_lb': round(revenue / weight, 2) if weight else 0
        }

def analyze_laundry(data: List[Dict]) -> Dict:
    t = LaundryTracker()
    for d in data:
        t.add(LaundryOrder(d['id'], d['type'], d['weight'], d.get('price', 2.50), d.get('detergent', 0.25), d.get('date', date.today())))
    return t.get_metrics()
