"""
E-commerce Business Tracker
============================
Track online store sales, margins, customer metrics
Shopify, WooCommerce, Amazon FBA
"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date


@dataclass
class EcommerceOrder:
    order_id: str
    revenue: float
    product_cost: float
    shipping_cost: float
    platform_fees: float
    date: date


class EcommerceTracker:
    """Track e-commerce business"""
    
    def __init__(self, store_name: str = "Store"):
        self.store_name = store_name
        self.orders: List[EcommerceOrder] = []
    
    def add_order(self, order: EcommerceOrder):
        self.orders.append(order)
    
    def get_metrics(self) -> Dict:
        if not self.orders:
            return {'status': 'NO_DATA'}
        
        revenue = sum(o.revenue for o in self.orders)
        costs = sum(o.product_cost + o.shipping_cost + o.platform_fees for o in self.orders)
        profit = revenue - costs
        
        return {
            'store': self.store_name,
            'total_orders': len(self.orders),
            'revenue': round(revenue, 2),
            'total_costs': round(costs, 2),
            'profit': round(profit, 2),
            'margin_pct': round(profit / revenue * 100, 1),
            'avg_order_value': round(revenue / len(self.orders), 2)
        }


# Usage
def analyze_ecommerce(orders: List[Dict]) -> Dict:
    tracker = EcommerceTracker()
    for o in orders:
        tracker.add_order(EcommerceOrder(
            order_id=o['id'],
            revenue=o['revenue'],
            product_cost=o.get('cost', 0),
            shipping_cost=o.get('shipping', 0),
            platform_fees=o.get('fees', 0),
            date=o.get('date', date.today())
        ))
    return tracker.get_metrics()
