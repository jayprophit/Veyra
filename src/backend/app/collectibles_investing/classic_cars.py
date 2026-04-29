"""Classic Cars - Vintage automobile investing"""
from typing import Dict

class ClassicCars:
    """Analyze classic car investments"""
    
    def valuation(self, year: int, make: str, model: str, condition: int, mileage: int) -> Dict:
        base_values = {"Ferrari": 500000, "Porsche": 200000, "Jaguar": 150000, "Aston Martin": 300000}
        base = base_values.get(make, 100000)
        
        condition_mult = {1: 0.3, 2: 0.6, 3: 1.0, 4: 1.5, 5: 2.5}.get(condition, 1.0)
        age = 2024 - year
        vintage_premium = min(age * 5000, 200000) if age > 25 else 0
        
        value = base * condition_mult + vintage_premium
        return {"estimated_value": round(value, 0), "base": base, "condition_adj": condition_mult}
    
    def investment_return(self, purchase_price: float, current_value: float, years_held: float, storage_cost_annual: float) -> Dict:
        storage_total = storage_cost_annual * years_held
        insurance_total = purchase_price * 0.015 * years_held
        total_costs = purchase_price + storage_total + insurance_total
        profit = current_value - total_costs
        cagr = ((current_value / total_costs) ** (1/years_held) - 1) * 100 if years_held > 0 else 0
        return {"cagr": round(cagr, 1), "profit": round(profit, 0), "total_costs": round(total_costs, 0)}
