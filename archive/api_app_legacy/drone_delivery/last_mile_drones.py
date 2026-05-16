"""Last Mile Drone Delivery"""
from typing import Dict

class LastMileDrones:
    """Analyze drone delivery economics"""
    
    def drone_costs(self) -> Dict:
        return {
            "aircraft": 10000,
            "ground_station": 50000,
            "maintenance_annual": 2000,
            "battery_cycles": 500,
            "battery_cost": 500
        }
    
    def delivery_economics(self, daily_deliveries: int = 50) -> Dict:
        delivery_fee = 5.00
        cost_per_delivery = 0.50  # electricity, wear
        
        daily_revenue = daily_deliveries * delivery_fee
        daily_cost = daily_deliveries * cost_per_delivery
        
        return {
            "revenue_per_day": daily_revenue,
            "cost_per_day": daily_cost,
            "profit_per_day": daily_revenue - daily_cost,
            "annual_profit": (daily_revenue - daily_cost) * 365
        }
    
    def vs_traditional(self, distance_miles: float = 5) -> Dict:
        driver_cost = 15.00 + (distance_miles * 0.60)  # Base + mileage
        drone_cost = 5.00  # Drone delivery fee
        
        return {
            "driver_delivery": driver_cost,
            "drone_delivery": drone_cost,
            "savings": driver_cost - drone_cost,
            "savings_pct": round((driver_cost - drone_cost) / driver_cost * 100, 0)
        }
