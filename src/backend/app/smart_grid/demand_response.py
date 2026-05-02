"""Demand Response Economics"""
from typing import Dict

class DemandResponse:
    """Load flexibility programs"""
    
    def program_types(self) -> Dict:
        return {
            "price_based": {
                "mechanism": "Time-varying rates",
                "customer_incentive": "Save money",
                "administrative_cost": "Low",
                "effectiveness": "Moderate"
            },
            "incentive_based": {
                "mechanism": "Direct load control/curtailment",
                "customer_incentive": "Monthly credit",
                "administrative_cost": "Medium",
                "effectiveness": "High"
            },
            "market_based": {
                "mechanism": "Bid into wholesale market",
                "customer_incentive": "Revenue share",
                "administrative_cost": "High",
                "effectiveness": "Highest"
            }
        }
    
    def resource_potential(self) -> Dict:
        return {
            "us_dr_capacity_gw": 60,
            "projected_2030_gw": 150,
            "sectors": {
                "residential": {"potential_pct": 0.10, "flexibility_hours": 2},
                "commercial": {"potential_pct": 0.15, "flexibility_hours": 4},
                "industrial": {"potential_pct": 0.20, "flexibility_hours": 8}
            },
            "ev_charging": {"future_potential_gw": 100, "control_method": "Smart scheduling"}
        }
    
    def economics(self, dr_capacity_mw: int = 100) -> Dict:
        return {
            "program_setup_cost_m": 5,
            "annual_administration_m": 2,
            "capacity_payment_per_kw_year": 50,
            "energy_payment_per_mwh": 100,
            "customer_incentives_annual_m": dr_capacity_mw * 0.05,
            "avoided_generation_cost_m": dr_capacity_mw * 0.10,
            "net_benefit_m": dr_capacity_mw * 0.03
        }
    
    def technology_enablers(self) -> Dict:
        return {
            "smart_thermostats": {"market_penetration_pct": 40, "dr_participation_pct": 60},
            "battery_storage": {"participation": "Bidirectional", "value_stack": 5},
            "ev_charging": {"v2g_potential": "High", "aggregation_needed": True},
            "building_automation": {"commercial_participation": "Key", "integration": "BACnet"}
        }
