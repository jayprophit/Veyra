"""Storage Costs"""
from typing import Dict

class StorageCosts:
    """Calculate commodity storage"""
    
    RATES = {"oil_terminal": 0.5, "grain_silo": 0.3, "lng_tank": 0.8}
    
    def storage_cost(self, commodity: str, volume: float,
                    months: int) -> Dict:
        """Calculate storage cost"""
        monthly_rate = self.RATES.get(commodity, 0.5)
        total = volume * monthly_rate * months
        
        return {"total_cost": total, "monthly_rate": monthly_rate, "cost_per_unit": monthly_rate}
    
    def carrying_cost(self, commodity_value: float, 
                     interest_rate: float = 0.05,
                     months: int = 6) -> Dict:
        """Total carrying cost"""
        interest = commodity_value * interest_rate * (months / 12)
        return {"interest_cost": interest, "annualized_rate": interest_rate}
