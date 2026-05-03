"""Coffee Shop & Cafe Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class CafeSale:
    sale_id: str
    item_category: str  # 'coffee', 'pastry', 'food'
    revenue: float
    cost: float
    date: date

class CafeTracker:
    def __init__(self, name: str = "Cafe"):
        self.name = name
        self.sales: List[CafeSale] = []
    
    def add(self, s: CafeSale):
        self.sales.append(s)
    
    def get_metrics(self) -> Dict:
        if not self.sales:
            return {'status': 'NO_DATA'}
        revenue = sum(s.revenue for s in self.sales)
        costs = sum(s.cost for s in self.sales)
        by_category = {}
        for s in self.sales:
            c = s.item_category
            if c not in by_category:
                by_category[c] = {'count': 0, 'revenue': 0}
            by_category[c]['count'] += 1
            by_category[c]['revenue'] += s.revenue
        return {
            'cafe': self.name,
            'sales': len(self.sales),
            'revenue': round(revenue, 2),
            'costs': round(costs, 2),
            'profit': round(revenue - costs, 2),
            'margin': round((revenue - costs) / revenue * 100, 1) if revenue else 0,
            'by_category': by_category,
            'avg_ticket': round(revenue / len(self.sales), 2)
        }

def analyze_cafe(data: List[Dict]) -> Dict:
    t = CafeTracker()
    for d in data:
        t.add(CafeSale(d['id'], d['category'], d['revenue'], d.get('cost', 0), d.get('date', date.today())))
    return t.get_metrics()
