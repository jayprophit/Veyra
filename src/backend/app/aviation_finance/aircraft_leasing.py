"""Aircraft Leasing"""
from typing import Dict

class AircraftLeasing:
    """Model aircraft lease economics"""
    
    RATES = {"narrowbody": 350000, "widebody": 850000, "regional": 120000}
    
    def lease_npv(self, aircraft_type: str, years: int, 
                 discount_rate: float = 0.06) -> Dict:
        """Calculate lessor NPV"""
        monthly = self.RATES.get(aircraft_type, 300000)
        annual = monthly * 12
        npv = sum(annual / ((1 + discount_rate) ** y) for y in range(1, years + 1))
        return {"monthly_lease": monthly, "npv": npv, "term": years}
    
    def operating_vs_finance(self, asset_value: float, lease_rate: float) -> Dict:
        """Compare lease vs buy"""
        annual_lease = lease_rate * 12
        implied_rate = annual_lease / asset_value
        return {"operating_cost": annual_lease, "implied_yield": implied_rate}
