"""Satellite Terminal Economics"""
from typing import Dict

class TerminalEconomics:
    """User terminal cost analysis"""
    
    def terminal_costs(self) -> Dict:
        return {
            "starlink_v2": {"cost": 599, "cost_to_make": 300, "subsidy": 299},
            "flat_high_performance": {"cost": 2500, "target": "Enterprise"},
            "future_phased_array": {"target_cost": 199, "timeline": "2025-2026"}
        }
    
    def economics_by_use_case(self) -> Dict:
        return {
            "rural_consumer": {"monthly_arpu": 120, "ltv_months": 24, "acquisition_cost": 100},
            "rv_maritime": {"monthly_arpu": 150, "ltv_months": 12, "churn": 0.30},
            "enterprise": {"monthly_arpu": 500, "ltv_months": 36, "acquisition_cost": 500}
        }
