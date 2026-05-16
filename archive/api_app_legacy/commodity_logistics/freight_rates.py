"""Freight Rates"""
from typing import Dict

class FreightRates:
    """Analyze freight markets"""
    
    BDI_RATES = {"capesize": 25000, "panamax": 15000, "supramax": 12000}
    
    def voyage_cost(self, vessel_type: str, distance_nm: float,
                   bunker_price: float = 600) -> Dict:
        """Calculate voyage cost"""
        daily_rate = self.BDI_RATES.get(vessel_type, 15000)
        days = distance_nm / 300  # 12 knots
        hire_cost = daily_rate * days
        fuel_cost = distance_nm * 30 * (bunker_price / 1000)  # tons per day
        
        return {
            "total_cost": hire_cost + fuel_cost,
            "hire_component": hire_cost,
            "fuel_component": fuel_cost,
            "days_at_sea": days
        }
    
    def time_charter_equiv(self, spot_rate: float, 
                          voyage_cost: float) -> Dict:
        """Calculate TCE"""
        tce = spot_rate - voyage_cost
        return {"tce_per_day": tce, "tce_annual": tce * 365}
