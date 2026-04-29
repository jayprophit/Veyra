"""Delivery Automation Economics"""
from typing import Dict

class DeliveryAutomation:
    """Autonomous delivery vehicles and drones"""
    
    def sidewalk_robot(self, daily_deliveries: int = 50) -> Dict:
        capex = 10000
        annual_opex = 3000
        
        revenue_per_delivery = 2
        annual_revenue = daily_deliveries * 365 * revenue_per_delivery
        
        return {
            "capex": capex,
            "annual_opex": annual_opex,
            "annual_revenue": annual_revenue,
            "payback_months": round(capex / ((annual_revenue - annual_opex) / 12), 1)
        }
    
    def drone_delivery(self, package_weight_kg: float = 2) -> Dict:
        capex = 15000
        range_km = 10
        speed_kmh = 60
        
        trips_per_day = 20
        revenue_per_trip = 5
        annual_revenue = trips_per_day * 365 * revenue_per_trip
        
        return {
            "capex": capex,
            "range_km": range_km,
            "speed_kmh": speed_kmh,
            "annual_revenue": annual_revenue,
            "use_case": "Medical supplies, urgent delivery"
        }
    
    def autonomous_truck(self, miles_per_year: float = 100000) -> Dict:
        capex = 250000  # $250k vs $150k conventional
        premium = 100000
        
        driver_cost_savings = 80000  # No driver
        fuel_savings = 10000  # More efficient
        
        annual_savings = driver_cost_savings + fuel_savings
        
        return {
            "truck_premium": premium,
            "annual_savings": annual_savings,
            "payback_years": round(premium / annual_savings, 1),
            "regulatory_status": "Testing on highways"
        }
