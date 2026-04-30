"""Autonomous Trucking Economics"""
from typing import Dict

class AutonomousTrucking:
    """Self-driving truck fleet economics"""
    
    def __init__(self, route_type: str = "hub_to_hub"):
        self.route_type = route_type  # hub_to_hub, long_haul, dedicated
    
    def truck_economics(self, fleet_size: int = 50) -> Dict:
        # Autonomous truck premium
        base_truck_cost = 250000
        autonomy_premium = 150000  # Sensors, software, compute
        total_truck_cost = base_truck_cost + autonomy_premium
        
        # Driver cost savings (biggest factor)
        driver_cost_per_mile = 0.70
        miles_per_year = 100000
        annual_driver_savings = driver_cost_per_mile * miles_per_year
        
        # Other savings
        fuel_efficiency_gain = 0.10  # 10% better mpg
        fuel_cost_per_mile = 0.50
        annual_fuel_savings = fuel_cost_per_mile * miles_per_year * fuel_efficiency_gain
        
        # Additional costs
        monitoring_center_annual = 20000
        maintenance_premium = 10000
        
        net_annual_savings = annual_driver_savings + annual_fuel_savings - monitoring_center_annual - maintenance_premium
        
        total_fleet_cost = fleet_size * total_truck_cost
        total_annual_savings = fleet_size * net_annual_savings
        
        return {
            "truck_cost": total_truck_cost,
            "autonomy_premium": autonomy_premium,
            "annual_driver_savings": annual_driver_savings,
            "annual_fuel_savings": annual_fuel_savings,
            "net_annual_savings_per_truck": net_annual_savings,
            "fleet_capex": total_fleet_cost,
            "fleet_annual_savings": total_annual_savings,
            "payback_years": round(total_fleet_cost / total_annual_savings, 1)
        }
    
    def operational_model(self) -> Dict:
        return {
            "hub_to_hub": {
                "description": "Autonomous on highway, human in city",
                "miles_autonomous": 0.90,
                "complexity": "Medium",
                "timeline": "2024-2026"
            },
            "long_haul": {
                "description": "Full autonomous highway",
                "miles_autonomous": 0.95,
                "complexity": "Lower",
                "timeline": "2023-2025"
            },
            "last_mile": {
                "description": "Complex urban environment",
                "miles_autonomous": 0.50,
                "complexity": "Very High",
                "timeline": "2028+"
            }
        }
    
    def key_players(self) -> Dict:
        return {
            "aurora": {"funding": 2e9, "partners": ["PACCAR", "Volvo"], "approach": "Highway"},
            "waymo_via": {"funding": "Via Waymo", "partners": ["J.B. Hunt"], "approach": "Hub-to-hub"},
            "tu_simple": {"status": "Winding down", "lessons": "Commercial challenges"},
            "embark": {"status": "Acquired", "price": 85e6, "buyer": "Applied Intuition"},
            "kodiak": {"funding": 165e6, "partners": ["Pitney Bowes"], "approach": "Defense + Commercial"},
            "gatik": {"funding": 120e6, "focus": "Middle mile", "partners": ["Walmart", "Loblaw"]}
        }
    
    def total_addressable_market(self) -> Dict:
        # US trucking market
        us_freight_spending = 800e9  # $800B annually
        long_haul_percentage = 0.40
        
        addressable = us_freight_spending * long_haul_percentage
        
        return {
            "us_freight_billions": us_freight_spending / 1e9,
            "long_haul_addressable_billions": addressable / 1e9,
            "autonomy_capture_2030": 0.10,  # 10% of long haul
            "autonomy_revenue_2030_billions": (addressable * 0.10) / 1e9,
            "key_metric": "$0.70/mile driver cost eliminated"
        }
