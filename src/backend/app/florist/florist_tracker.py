"""Florist & Flower Shop Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class FlowerSale:
    sale_id: str
    arrangement_type: str
    revenue: float
    flower_cost: float
    labor_minutes: int
    date: date

class FloristTracker:
    def __init__(self, name: str = "Florist"):
        self.name = name
        self.sales: List[FlowerSale] = []
    
    def add(self, s: FlowerSale):
        self.sales.append(s)
    
    def get_metrics(self) -> Dict:
        if not self.sales:
            return {'status': 'NO_DATA'}
        revenue = sum(s.revenue for s in self.sales)
        costs = sum(s.flower_cost for s in self.sales)
        profit = revenue - costs
        return {
            'shop': self.name,
            'sales': len(self.sales),
            'revenue': round(revenue, 2),
            'flower_costs': round(costs, 2),
            'profit': round(profit, 2),
            'margin': round(profit / revenue * 100, 1) if revenue else 0,
            'avg_sale': round(revenue / len(self.sales), 2)
        }

def analyze_florist(data: List[Dict]) -> Dict:
    t = FloristTracker()
    for d in data:
        t.add(FlowerSale(d['id'], d['type'], d['revenue'], d.get('cost', 0), d.get('minutes', 30), d.get('date', date.today())))
    return t.get_metrics()
