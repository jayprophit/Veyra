"""eVTOL Aircraft Economics"""
from typing import Dict

class EVTOLLEconomics:
    """Analyze electric vertical takeoff and landing investments"""
    
    def __init__(self, aircraft_type: str = "multicopter", passenger_capacity: int = 4):
        self.type = aircraft_type  # multicopter, lift+cruise, vectored thrust
        self.capacity = passenger_capacity
    
    def aircraft_cost(self) -> Dict:
        costs = {
            "multicopter": 1.5e6,      # $1.5M
            "lift_cruise": 2.5e6,      # $2.5M
            "vectored_thrust": 3.0e6   # $3.0M
        }
        
        base_cost = costs.get(self.type, 2.0e6)
        
        return {
            "purchase_price": round(base_cost, 0),
            "per_passenger_cost": round(base_cost / self.capacity, 0),
            "certification_timeline": "2025-2026" if self.type == "multicopter" else "2026-2028",
            "battery_cycles_lifetime": 2000
        }
    
    def operating_economics(self, trip_distance_nm: float = 20) -> Dict:
        # Operating costs per flight hour
        energy_cost = 0.15  # $/kWh
        power_consumption = 300  # kW average
        flight_time_hours = trip_distance_nm / 100  # Assuming 100 knots
        
        energy_per_trip = power_consumption * flight_time_hours * energy_cost
        pilot_cost = 50  # Autonomous will reduce this
        maintenance = 100
        insurance = 50
        
        total_cost = energy_per_trip + pilot_cost + maintenance + insurance
        
        # Revenue
        ticket_price_per_pax = 100  # Premium over ground transport
        revenue = ticket_price_per_pax * self.capacity
        
        return {
            "cost_per_trip": round(total_cost, 0),
            "revenue_per_trip": revenue,
            "margin_per_trip": round(revenue - total_cost, 0),
            "energy_cost_pct": round(energy_per_trip / total_cost * 100, 1),
            "break_even_load_factor": round(total_cost / revenue * 100, 1)
        }
    
    def market_opportunity(self, daily_trips_per_aircraft: int = 20) -> Dict:
        # Urban air mobility market
        us_cities_viable = 50
        aircraft_per_city = 100
        total_addressable_aircraft = us_cities_viable * aircraft_per_city
        
        aircraft_cost = self.aircraft_cost()["purchase_price"]
        total_tam_value = total_addressable_aircraft * aircraft_cost
        
        ops = self.operating_economics()
        annual_trips = daily_trips_per_aircraft * 300  # Operating days
        annual_revenue_per_aircraft = annual_trips * ops["revenue_per_trip"]
        
        return {
            "us_market_aircraft": total_addressable_aircraft,
            "aircraft_tam_billions": round(total_tam_value / 1e9, 1),
            "annual_revenue_per_aircraft": round(annual_revenue_per_aircraft, 0),
            "serviceable_market_2030": round(total_addressable_aircraft * 0.3),  # 30% penetration
            "payback_years": round(aircraft_cost / (annual_revenue_per_aircraft * 0.3), 1)
        }
    
    def vs_ground_transport(self, ground_cost_per_mile: float = 2) -> Dict:
        trip_distance = 20  # miles
        ground_total = trip_distance * ground_cost_per_mile * self.capacity
        
        air_ops = self.operating_economics()
        air_revenue = air_ops["revenue_per_trip"]
        
        time_savings_minutes = 30  # Urban traffic
        value_of_time = 50  # $/hour per passenger
        time_value = value_of_time * (time_savings_minutes / 60) * self.capacity
        
        return {
            "ground_transport_cost": ground_total,
            "air_taxi_revenue": air_revenue,
            "premium_over_ground": round((air_revenue / ground_total - 1) * 100, 0),
            "time_savings_value": round(time_value, 0),
            "justified_premium_pct": round((time_value / ground_total) * 100, 0)
        }
