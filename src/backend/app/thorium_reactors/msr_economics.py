"""Molten Salt Reactor Economics"""
from typing import Dict

class MSREconomics:
    """Molten salt reactor costs and benefits"""
    
    def reactor_types(self) -> Dict:
        return {
            "thermal_spectrum": {
                "fuel": "UF4 in FLiBe",
                "moderator": "Graphite",
                " Outlet_temp_c": 700,
                "efficiency_pct": 45,
                "status": "Development"
            },
            "fast_spectrum": {
                "fuel": "Chloride salts",
                "breeding": "U-233 from Th-232",
                "outlet_temp_c": 850,
                "efficiency_pct": 50,
                "status": "Concept"
            }
        }
    
    def advantages(self) -> Dict:
        return {
            "safety": {"meltdown": "Impossible - fuel already molten", "pressure": "Low (near atmospheric)"},
            "efficiency": {"thermal_to_electric": 0.50, "waste_heat": "Can be used for process"},
            "fuel_utilization": {"burnup_pct": 99, "waste_volume": "Fraction of LWR"},
            "online_refueling": {"continuous_operation": "No shutdowns", "capacity_factor": 0.95}
        }
    
    def cost_estimates(self, capacity_mw: int = 100) -> Dict:
        return {
            "overnight_cost_per_kw": 4000,  # Similar to advanced reactors
            "total_capital_m": capacity_mw * 4000,
            "development_cost_first_of_kind_b": 2,
            "nth_of_a_kind_reduction": 0.30,
            "fuel_cost_per_mwh": 5,
            "om_per_mwh": 15
        }
    
    def development_timeline(self) -> Dict:
        return {
            "kairos_power": {"design": "Hermes demo", "timeline": "2027", "funding": "Private + DOE"},
            "terrestrial_energy": {"design": "IMSR", "location": "Canada", "licensing": "Pre-application"},
            "copenhagen_atomics": {"design": "Waste burner", "approach": "Open source", "timeline": "2030"}
        }
