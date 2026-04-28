"""Route Economics"""
from typing import Dict

class RouteEconomics:
    """Analyze route profitability"""
    
    def route_profit(self, distance_nm: float, passengers: int, 
                    yield_per_mile: float = 0.12) -> Dict:
        """Calculate route profitability"""
        revenue = distance_nm * passengers * yield_per_mile
        fuel_cost = distance_nm * 3.5  # gallons * $5
        operating_cost = fuel_cost + (passengers * 50) + 50000  # fixed
        
        return {
            "revenue": revenue,
            "operating_cost": operating_cost,
            "profit": revenue - operating_cost,
            "profit_per_passenger": (revenue - operating_cost) / passengers if passengers > 0 else 0
        }
    
    def load_factor_breakeven(self, fixed_costs: float, 
                             variable_cost_per_pax: float,
                             avg_ticket: float,
                             seats: int) -> Dict:
        """Calculate breakeven load factor"""
        breakeven_pax = fixed_costs / (avg_ticket - variable_cost_per_pax)
        load_factor = breakeven_pax / seats
        return {"breakeven_passengers": breakeven_pax, "load_factor": load_factor}
