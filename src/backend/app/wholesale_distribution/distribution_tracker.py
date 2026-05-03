"""Wholesale & Distribution Tracker"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date

@dataclass
class WholesaleOrder:
    order_id: str
    customer: str
    revenue: float
    cost_of_goods: float
    shipping: float
    date: date

class WholesaleTracker:
    def __init__(self, name: str = "Distribution"):
        self.name = name
        self.orders: List[WholesaleOrder] = []
    
    def add_order(self, o: WholesaleOrder):
        self.orders.append(o)
    
    def get_metrics(self) -> Dict:
        if not self.orders:
            return {'status': 'NO_DATA'}
        revenue = sum(o.revenue for o in self.orders)
        cogs = sum(o.cost_of_goods for o in self.orders)
        shipping = sum(o.shipping for o in self.orders)
        profit = revenue - cogs - shipping
        return {
            'company': self.name,
            'orders': len(self.orders),
            'revenue': round(revenue, 2),
            'cogs': round(cogs, 2),
            'shipping': round(shipping, 2),
            'profit': round(profit, 2),
            'margin_pct': round(profit / revenue * 100, 1) if revenue else 0,
            'avg_order': round(revenue / len(self.orders), 2)
        }

def analyze_wholesale(orders: List[Dict]) -> Dict:
    t = WholesaleTracker()
    for o in orders:
        t.add_order(WholesaleOrder(o['id'], o['customer'], o['revenue'], o.get('cogs', o['revenue'] * 0.6), o.get('shipping', 0), o.get('date', date.today())))
    return t.get_metrics()
