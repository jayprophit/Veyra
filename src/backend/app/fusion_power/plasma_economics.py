"""Plasma Physics Economics"""
from typing import Dict

class PlasmaEconomics:
    """Fusion plasma performance metrics"""
    
    def performance_metrics(self) -> Dict:
        return {
            "triple_product": {
                "description": "n * T * tau - fusion figure of merit",
                "iter_target": 3e21,
                "net_energy_threshold": 1e21,
                "current_record": 1.5e21  # JET
            },
            "q_factor": {
                "description": "Fusion energy out / energy in",
                "iter_target": 10,
                "current_best": 1.53,  # JET 1997
                "net_electricity": "Q > 30 required"
            }
        }
    
    def reactor_economics(self, capacity_mw: int = 1000) -> Dict:
        overnight_cost = 5e9  # $5B per GW
        fixed_om = 100e6  # $100M/year
        fuel_cost = 0.02  # $0.02/kWh (tritium)
        capacity_factor = 0.85
        
        annual_output_mwh = capacity_mw * 8760 * capacity_factor
        revenue_at_50_mwh = annual_output_mwh * 50
        
        return {
            "capex": overnight_cost,
            "annual_om": fixed_om,
            "annual_fuel_cost": annual_output_mwh * fuel_cost,
            "annual_revenue_50_mwh": revenue_at_50_mwh,
            "payback_years": round(overnight_cost / (revenue_at_50_mwh - fixed_om), 1)
        }
