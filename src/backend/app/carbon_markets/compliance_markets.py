"""Compliance Markets"""
from typing import Dict

class ComplianceMarkets:
    def ets_analysis(self, allowance_price: float, emissions: float) -> Dict:
        cost = allowance_price * emissions
        return {"total_cost": cost, "cost_per_tonne_co2": allowance_price}
