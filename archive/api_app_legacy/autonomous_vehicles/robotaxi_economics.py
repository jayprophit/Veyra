"""Robotaxi Economics"""
from typing import Dict

class RobotaxiEconomics:
    """Analyze robotaxi fleet economics"""
    
    def __init__(self, city_tier: str = "tier1"):
        self.city_tier = city_tier  # tier1, tier2, suburban
    
    def vehicle_economics(self, fleet_size: int = 100) -> Dict:
        # Waymo/Cruise vehicle costs
        sensor_suite = 150000  # LiDAR, cameras, radar
        vehicle_platform = 50000  # Base EV
        total_vehicle_cost = sensor_suite + vehicle_platform
        
        # Operating costs per mile
        maintenance = 0.20
        energy = 0.05
        insurance = 0.15
        teleops = 0.10  # Remote supervision
        
        cost_per_mile = maintenance + energy + insurance + teleops
        
        # Revenue
        miles_per_day = 200
        revenue_per_mile = 1.50
        daily_revenue = miles_per_day * revenue_per_mile
        daily_cost = miles_per_day * cost_per_mile
        
        annual_revenue_per_vehicle = daily_revenue * 365
        annual_cost_per_vehicle = daily_cost * 365
        
        total_fleet_capex = fleet_size * total_vehicle_cost
        annual_fleet_profit = (annual_revenue_per_vehicle - annual_cost_per_vehicle) * fleet_size
        
        return {
            "vehicle_cost": total_vehicle_cost,
            "cost_per_mile": cost_per_mile,
            "revenue_per_mile": revenue_per_mile,
            "annual_revenue_per_vehicle": annual_revenue_per_vehicle,
            "annual_profit_per_vehicle": annual_revenue_per_vehicle - annual_cost_per_vehicle,
            "fleet_capex": total_fleet_capex,
            "annual_fleet_profit": annual_fleet_profit,
            "payback_years": round(total_fleet_capex / annual_fleet_profit, 1) if annual_fleet_profit > 0 else float('inf')
        }
    
    def market_sizing(self, metro_population: int = 5_000_000) -> Dict:
        # Trips per day in metro area
        trips_per_capita = 3.0
        total_trips = metro_population * trips_per_capita
        
        # Robotaxi penetration
        robotaxi_share = 0.05  # 5% of trips
        robotaxi_trips = total_trips * robotaxi_share
        
        avg_fare = 15.00
        market_revenue = robotaxi_trips * avg_fare * 365
        
        return {
            "daily_trips_metro": total_trips,
            "robotaxi_trips_daily": robotaxi_trips,
            "annual_market_revenue_millions": market_revenue / 1e6,
            "market_share_target": 0.05
        }
    
    def competitive_landscape(self) -> Dict:
        return {
            "waymo": {"fleet": 700, "cities": ["SF", "Phoenix", "LA"], "valuation": 30e9},
            "cruise": {"fleet": 300, "cities": ["SF", "Austin"], "valuation": 30e9, "status": "Paused"},
            "zoox": {"fleet": 0, "cities": ["Testing"], "valuation": 1.2e9, "owner": "Amazon"},
            "motional": {"fleet": 100, "cities": ["Las Vegas", "LA"], "partners": ["Hyundai", "Aptiv"]},
            "tesla": {"approach": "Vision only", "timeline": "2024-2025", "fleet": "Consumer vehicles"}
        }
    
    def vs_uber(self, trip_distance_miles: float = 10) -> Dict:
        uber_cost = 2.00 * trip_distance_miles + 5.00  # $2/mile + base
        robotaxi_cost = 1.00 * trip_distance_miles  # $1/mile, no driver
        
        return {
            "uber_total": uber_cost,
            "robotaxi_total": robotaxi_cost,
            "savings": uber_cost - robotaxi_cost,
            "savings_pct": round((uber_cost - robotaxi_cost) / uber_cost * 100, 0),
            "consumer_benefit": "50% lower cost"
        }
