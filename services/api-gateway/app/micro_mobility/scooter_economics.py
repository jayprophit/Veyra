"""E-Scooter Economics"""
from typing import Dict

class ScooterEconomics:
    """Scooter sharing unit economics"""
    
    def unit_costs(self) -> Dict:
        return {
            "scooter_cost": 500,
            "lifetime_months": 12,
            "rides_per_day": 4,
            "average_ride_value": 3.50,
            "charging_cost_per_day": 2.00,
            "maintenance_per_month": 30
        }
    
    def lifetime_revenue(self) -> Dict:
        c = self.unit_costs()
        daily_revenue = c["rides_per_day"] * c["average_ride_value"]
        daily_profit = daily_revenue - c["charging_cost_per_day"] - (c["maintenance_per_month"] / 30)
        
        lifetime_days = c["lifetime_months"] * 30
        lifetime_profit = daily_profit * lifetime_days
        
        return {
            "total_revenue": daily_revenue * lifetime_days,
            "total_profit": lifetime_profit,
            "roi_pct": round((lifetime_profit / c["scooter_cost"]) * 100, 0)
        }
