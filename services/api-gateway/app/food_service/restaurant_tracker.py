"""
Restaurant & Food Service Tracker
==================================
Track restaurant revenue, costs, table turnover
Food cost, labor cost, profit margins
"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date


@dataclass
class RestaurantSale:
    order_id: str
    amount: float
    food_cost: float
    category: str  # 'dine_in', 'takeout', 'delivery'
    date: date


class RestaurantTracker:
    """Track restaurant business"""
    
    def __init__(self, name: str = "Restaurant"):
        self.name = name
        self.sales: List[RestaurantSale] = []
    
    def add_sale(self, sale: RestaurantSale):
        self.sales.append(sale)
    
    def get_health_report(self) -> Dict:
        if not self.sales:
            return {'status': 'NO_DATA'}
        
        total = sum(s.amount for s in self.sales)
        food_cost = sum(s.food_cost for s in self.sales)
        
        by_category = {}
        for s in self.sales:
            c = s.category
            if c not in by_category:
                by_category[c] = 0
            by_category[c] += s.amount
        
        return {
            'restaurant': self.name,
            'total_revenue': round(total, 2),
            'food_cost': round(food_cost, 2),
            'food_cost_pct': round(food_cost / total * 100, 1),
            'gross_margin_pct': round((total - food_cost) / total * 100, 1),
            'by_category': by_category
        }


# Usage
def analyze_restaurant(sales_data: List[Dict]) -> Dict:
    tracker = RestaurantTracker()
    for s in sales_data:
        tracker.add_sale(RestaurantSale(
            order_id=s['id'],
            amount=s['amount'],
            food_cost=s.get('food_cost', s['amount'] * 0.30),
            category=s.get('category', 'dine_in'),
            date=s.get('date', date.today())
        ))
    return tracker.get_health_report()
