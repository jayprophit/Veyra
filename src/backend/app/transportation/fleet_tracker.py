"""
Transportation & Fleet Management Tracker
==========================================
Track delivery fleet, trucking, logistics operations
Revenue per mile, fuel costs, vehicle maintenance
"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date


@dataclass
class FleetTrip:
    trip_id: str
    vehicle_id: str
    miles: float
    revenue: float
    fuel_cost: float
    driver_wages: float
    maintenance: float
    date: date


class FleetTracker:
    """Track transportation fleet operations"""
    
    def __init__(self, fleet_name: str = "Fleet"):
        self.fleet_name = fleet_name
        self.trips: List[FleetTrip] = []
    
    def add_trip(self, trip: FleetTrip):
        self.trips.append(trip)
    
    def get_fleet_metrics(self) -> Dict:
        if not self.trips:
            return {'status': 'NO_DATA'}
        
        revenue = sum(t.revenue for t in self.trips)
        miles = sum(t.miles for t in self.trips)
        fuel = sum(t.fuel_cost for t in self.trips)
        wages = sum(t.driver_wages for t in self.trips)
        maint = sum(t.maintenance for t in self.trips)
        
        costs = fuel + wages + maint
        profit = revenue - costs
        
        return {
            'fleet': self.fleet_name,
            'total_trips': len(self.trips),
            'total_miles': round(miles, 0),
            'revenue': round(revenue, 2),
            'fuel_cost': round(fuel, 2),
            'wages': round(wages, 2),
            'maintenance': round(maint, 2),
            'total_costs': round(costs, 2),
            'profit': round(profit, 2),
            'margin_pct': round(profit / revenue * 100, 1) if revenue else 0,
            'revenue_per_mile': round(revenue / miles, 2) if miles else 0,
            'cost_per_mile': round(costs / miles, 2) if miles else 0
        }


# Usage
def analyze_fleet(trips: List[Dict]) -> Dict:
    tracker = FleetTracker()
    for t in trips:
        tracker.add_trip(FleetTrip(
            trip_id=t['id'],
            vehicle_id=t.get('vehicle', 'V1'),
            miles=t['miles'],
            revenue=t['revenue'],
            fuel_cost=t.get('fuel', t['miles'] * 0.50),
            driver_wages=t.get('wages', t['miles'] * 0.60),
            maintenance=t.get('maint', 0),
            date=t.get('date', date.today())
        ))
    return tracker.get_fleet_metrics()
