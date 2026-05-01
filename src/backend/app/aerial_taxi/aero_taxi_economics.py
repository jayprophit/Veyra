"""Aero Taxi Service Economics"""
from typing import Dict

class AeroTaxiEconomics:
    """Air taxi business model"""
    
    def market_size(self) -> Dict:
        return {
            "tam_2040": 1e12,  # $1T total addressable
            "us_market_2040": 300e9,
            "early_adopter_trips_annual": 100e6,
            "pricing_per_mile": 4.0  # $4/mile vs $2.50 Uber
        }
    
    def vertiport_economics(self) -> Dict:
        return {
            "capex": 5e6,  # $5M per vertiport
            "operating_annual": 500000,
            "slots_per_hour": 60,
            "revenue_per_landing": 50,
            "breakeven_flights_daily": 300
        }
    
    def fleet_requirements(self, daily_trips: int = 10000) -> Dict:
        trips_per_aircraft_daily = 20
        utilization = 0.60
        
        aircraft_needed = daily_trips / (trips_per_aircraft_daily * utilization)
        
        return {
            "aircraft_count": int(aircraft_needed),
            "aircraft_cost_each": 3e6,
            "total_fleet_capex": aircraft_needed * 3e6,
            "vertiports_needed": max(10, int(aircraft_needed / 20))
        }
