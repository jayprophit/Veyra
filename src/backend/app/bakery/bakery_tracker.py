"""Bakery & Pastry Shop Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class BakedGood:
    item_id: str
    item_type: str
    quantity: int
    unit_price: float
    ingredient_cost: float
    date: date

class BakeryTracker:
    def __init__(self, name: str = "Bakery"):
        self.name = name
        self.items: List[BakedGood] = []
    
    def add(self, i: BakedGood):
        self.items.append(i)
    
    def get_metrics(self) -> Dict:
        if not self.items:
            return {'status': 'NO_DATA'}
        revenue = sum(i.quantity * i.unit_price for i in self.items)
        costs = sum(i.ingredient_cost for i in self.items)
        items_sold = sum(i.quantity for i in self.items)
        return {
            'bakery': self.name,
            'transactions': len(self.items),
            'items_sold': items_sold,
            'revenue': round(revenue, 2),
            'ingredient_costs': round(costs, 2),
            'profit': round(revenue - costs, 2),
            'margin': round((revenue - costs) / revenue * 100, 1) if revenue else 0,
            'avg_transaction': round(revenue / len(self.items), 2)
        }

def analyze_bakery(data: List[Dict]) -> Dict:
    t = BakeryTracker()
    for d in data:
        t.add(BakedGood(d['id'], d['type'], d['qty'], d['price'], d.get('cost', 0), d.get('date', date.today())))
    return t.get_metrics()
