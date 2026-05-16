"""Maritime Shipping Economics"""
from typing import Dict

class MaritimeEconomics:
    """Container shipping economics"""
    
    def shipping_costs(self, route: str = "asia_europe") -> Dict:
        costs = {
            "asia_europe": {
                "fuel_per_teu": 400,
                "charter_per_teu": 300,
                "port_fees": 150,
                "crew_per_teu": 100,
                "total": 950
            },
            "transpacific": {
                "fuel_per_teu": 500,
                "charter_per_teu": 350,
                "port_fees": 200,
                "crew_per_teu": 120,
                "total": 1170
            }
        }
        return costs.get(route, costs["asia_europe"])
    
    def fleet_autonomy_roi(self, fleet_size: int = 10) -> Dict:
        retrofit_per_vessel = 1.5e6
        annual_savings_per_vessel = 1.5e6
        
        total_capex = retrofit_per_vessel * fleet_size
        total_annual_savings = annual_savings_per_vessel * fleet_size
        
        return {
            "total_capex": total_capex,
            "annual_savings": total_annual_savings,
            "payback_years": round(total_capex / total_annual_savings, 1),
            "ten_year_npv": (total_annual_savings * 10) - total_capex
        }
    
    def market_size(self) -> Dict:
        return {
            "global_shipping_revenue": 200e9,
            "container_share": 0.60,
            "autonomous_addressable": 50e9,
            "technology_spend": 5e9
        }
