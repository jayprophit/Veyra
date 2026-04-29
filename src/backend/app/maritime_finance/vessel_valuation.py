"""Vessel Valuation - Ship valuations and economics"""
from typing import Dict

class VesselValuation:
    """Value commercial vessels"""
    
    def secondhand_value(self, newbuild_price: float,
                        age_years: int,
                        vessel_type: str) -> Dict:
        """Calculate secondhand vessel value"""
        # Depreciation curves by type
        depreciation = {
            "bulk_carrier": 0.04, "tanker": 0.05, "container": 0.06,
            "lng": 0.03, "lpg": 0.04
        }
        
        rate = depreciation.get(vessel_type, 0.05)
        remaining_value = newbuild_price * ((1 - rate) ** age_years)
        scrap_floor = newbuild_price * 0.15  # Scrap value floor
        
        value = max(remaining_value, scrap_floor)
        
        return {
            "newbuild_price": newbuild_price,
            "age": age_years,
            "depreciation_rate": rate,
            "current_value": round(value, 0),
            "value_loss": round(newbuild_price - value, 0),
            "scrap_value": round(scrap_floor, 0)
        }
    
    def charter_rate_yield(self, daily_rate: float,
                        operating_cost: float,
                        vessel_value: float) -> Dict:
        """Calculate vessel charter yield"""
        daily_profit = daily_rate - operating_cost
        annual_profit = daily_profit * 330  # 330 operating days
        yield_pct = (annual_profit / vessel_value) * 100 if vessel_value > 0 else 0
        
        return {
            "daily_rate": daily_rate,
            "daily_operating_cost": operating_cost,
            "daily_profit": daily_profit,
            "annual_profit": round(annual_profit, 0),
            "asset_yield": round(yield_pct, 2),
            "investment_grade": "A" if yield_pct > 15 else "B" if yield_pct > 10 else "C"
        }
