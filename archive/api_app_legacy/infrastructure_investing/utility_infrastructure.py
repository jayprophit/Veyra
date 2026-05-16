"""Utility Infrastructure"""
from typing import Dict

class UtilityInfrastructure:
    def regulated_utility(self, rate_base: float, allowed_roe: float) -> Dict:
        allowed_earnings = rate_base * allowed_roe
        return {"rate_base": rate_base, "allowed_roe": allowed_roe, "allowed_earnings": allowed_earnings}
    
    def infrastructure_yield(self, investment: float, cash_yield: float) -> Dict:
        return {"cash_yield": cash_yield, "yield_pct": cash_yield / investment * 100 if investment > 0 else 0}
