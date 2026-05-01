"""Geothermal Drilling Economics"""
from typing import Dict

class GeothermalDrilling:
    """Drilling costs and technology"""
    
    def drilling_costs(self) -> Dict:
        return {
            "conventional_geothermal": {
                "cost_per_meter": 2000,
                "typical_depth_m": 3000,
                "total_well_cost": 6e6
            },
            "egs_deep_drilling": {
                "cost_per_meter": 5000,
                "target_depth_m": 7000,
                "total_well_cost": 35e6
            },
            "advanced_drilling_tech": {
                "plasma_drilling": {"status": "R&D", "potential_reduction": 0.50},
                "millimeter_wave": {"status": "Pilot", "target_depth": 20000}
            }
        }
    
    def project_economics(self) -> Dict:
        return {
            "capex_breakdown": {
                "drilling": 0.50,
                "surface_plant": 0.30,
                "exploration": 0.10,
                "contingency": 0.10
            },
            "lcoe_factors": {
                "resource_temperature": "Primary driver",
                "flow_rate": "Second most important",
                "drilling_success_rate": 0.70
            }
        }
    
    def risk_mitigation(self) -> Dict:
        return {
            "exploration_risk": {"dry_hole_rate": 0.20, "insurance_available": True},
            "resource_decline": {"annual_rate": 0.05, "mitigation": "Reinjection"},
            "induced_seismicity": {"management": "Traffic light protocol", "public_concern": "Medium"}
        }
