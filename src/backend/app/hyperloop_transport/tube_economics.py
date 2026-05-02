"""Hyperloop Tube Economics"""
from typing import Dict

class TubeEconomics:
    """Vacuum tube transportation costs"""
    
    def capex_analysis(self) -> Dict:
        return {
            "tube_construction": {
                "cost_per_km": 50e6,
                "diameter_m": 3.3,
                "materials": ["Steel", "Concrete pylons"],
                "earthworks": "Major cost driver"
            },
            "levitation_system": {
                "maglev_per_km": 10e6,
                "maintenance_annual": 1e6,
                "efficiency": 0.95
            },
            "vacuum_system": {
                "pumps_per_km": 20,
                "energy_consumption_mw": 5,
                "operating_cost_annual": 2e6
            }
        }
    
    def operating_model(self, distance_km: int = 500) -> Dict:
        capacity = 28  # passengers per pod
        pods_per_hour = 30
        ticket_price = 100
        
        daily_revenue = capacity * pods_per_hour * 16 * ticket_price
        annual_revenue = daily_revenue * 300
        
        capex = distance_km * 60e6
        annual_om = distance_km * 5e6
        
        return {
            "passenger_capacity_daily": capacity * pods_per_hour * 16,
            "annual_revenue": annual_revenue,
            "capex": capex,
            "annual_om": annual_om,
            "simple_payback_years": round(capex / (annual_revenue - annual_om), 1)
        }
    
    def route_economics(self) -> Dict:
        return {
            "la_to_sf": {"distance_km": 600, "capex_b": 36, "trip_time_min": 35, "viability": "Challenged"},
            "dubai_to_abu_dhabi": {"distance_km": 140, "capex_b": 8, "trip_time_min": 12, "advantage": "Short test route"},
            "european_corridor": {"distance_km": 1000, "regulatory": "Complex", "timeline": "Uncertain"}
        }
