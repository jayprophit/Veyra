"""Bike Sharing Economics"""
from typing import Dict

class BikeSharing:
    """Bike share system economics"""
    
    def system_costs(self, bike_count: int = 1000) -> Dict:
        bike_cost = 1200
        station_cost = 50000
        station_count = bike_count / 10
        
        total = (bike_cost * bike_count) + (station_cost * station_count)
        
        return {
            "total_capex": total,
            "per_bike_cost": bike_cost,
            "station_count": station_count
        }
