"""Point Source Capture Economics"""
from typing import Dict

class PointSourceCapture:
    """Industrial CO2 capture"""
    
    def capture_technologies(self) -> Dict:
        return {
            "amine_scrubbing": {
                "maturity": "Commercial",
                "cost_per_ton": 60,
                "energy_penalty_pct": 20,
                "applications": ["Natural gas processing", "Power plants"]
            },
            "solid_sorbents": {
                "maturity": "Demonstration",
                "cost_per_ton": 50,
                "energy_penalty_pct": 15,
                "advantage": "Lower regeneration energy"
            },
            "calcium_looping": {
                "maturity": "Pilot",
                "cost_per_ton": 40,
                "advantage": "Waste sorbent utilization"
            }
        }
    
    def project_economics(self, scale_tons_yearly: int = 1000000) -> Dict:
        capex = scale_tons_yearly * 200
        opex = scale_tons_yearly * 30
        transport_storage = scale_tons_yearly * 20
        
        return {
            "capex_m": capex / 1e6,
            "annual_opex_m": opex / 1e6,
            "transport_storage_m": transport_storage / 1e6,
            "total_cost_per_ton": 200 + 30 + 20,
            "45q_credit_per_ton": 85,
            "net_cost_per_ton": 165,
            "needed_credit_for_profit": 165
        }
    
    def major_projects(self) -> Dict:
        return {
            "petra_nova": {"location": "Texas", "scale_tons": 1.6e6, "status": "Operational", "cost": 1e9},
            "boundary_dam": {"location": "Canada", "scale_tons": 1e6, "status": "Operational"},
            "orc_project": {"location": "California", "scale_tons": 1.5e6, "status": "Construction"}
        }
