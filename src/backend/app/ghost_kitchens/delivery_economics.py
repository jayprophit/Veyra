"""Food Delivery Economics"""
from typing import Dict

class DeliveryEconomics:
    """Delivery platform and logistics economics"""
    
    def platform_economics(self, order_value: float = 30) -> Dict:
        commission = order_value * 0.30
        delivery_fee = 2.99
        service_fee = order_value * 0.10
        
        platform_revenue = commission + delivery_fee + service_fee
        
        driver_pay = 5.00
        insurance = 0.50
        support = 0.50
        tech_cost = 0.30
        
        platform_costs = driver_pay + insurance + support + tech_cost
        
        return {
            "platform_revenue": round(platform_revenue, 2),
            "platform_costs": round(platform_costs, 2),
            "platform_take": round(platform_revenue - platform_costs, 2),
            "take_rate_pct": round((platform_revenue - platform_costs) / order_value * 100, 1)
        }
    
    def market_leaders(self) -> Dict:
        return {
            "doordash": {"us_market_share": 0.65, "revenue_2024_billions": 9.0, "profit_status": "Profitable"},
            "uber_eats": {"us_market_share": 0.25, "revenue_2024_billions": 12.0, "profit_status": "Profitable"},
            "grubhub": {"us_market_share": 0.08, "parent": "Just Eat Takeaway", "status": "Struggling"},
            "instacart": {"focus": "Grocery", "revenue_2024_billions": 3.0, "ipo": 2023}
        }
    
    def delivery_robots(self) -> Dict:
        """Autonomous delivery economics"""
        return {
            "robot_cost": 5000,
            "daily_deliveries": 15,
            "operating_cost_per_day": 2.0,
            "payback_months": 8,
            "deployed_count": 2000,
            "companies": ["Starship Technologies", "Nuro", "Kiwibot"]
        }
