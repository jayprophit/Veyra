"""Sustainable Aviation Fuel Economics"""
from typing import Dict

class SAFEconomics:
    """SAF production and market"""
    
    def pathway_comparison(self) -> Dict:
        return {
            "heft_spk": {
                "feedstock": "Used cooking oil, tallow",
                "blend_limit_pct": 50,
                "cost_per_liter": 2.0,
                "maturity": "Commercial",
                "capacity_growth": 0.30
            },
            "ft_spk": {
                "feedstock": "Municipal waste, biomass",
                "blend_limit_pct": 50,
                "cost_per_liter": 3.0,
                "maturity": "Limited commercial"
            },
            "atj": {
                "feedstock": "Ethanol",
                "blend_limit_pct": 50,
                "cost_per_liter": 2.5,
                "maturity": "Early commercial"
            },
            "ptl_power_to_liquid": {
                "feedstock": "CO2 + H2 + renewable energy",
                "blend_limit_pct": 100,
                "cost_per_liter": 5.0,
                "maturity": "R&D/pilot",
                "long_term_potential": "Highest"
            }
        }
    
    def market_mandates(self) -> Dict:
        return {
            "eu_refuel_eu": {"target_2030_pct": 6, "target_2050_pct": 70},
            "uk_mandate": {"start_2025_pct": 2, "escalation": "Annual"},
            "us_incentive": {"credit_per_gallon": 1.75, "mechanism": "Blenders tax credit"},
            "singapore": {"target_2026_pct": 1, "hub_strategy": True}
        }
    
    def airline_economics(self, fuel_volume_gallons: int = 1000000) -> Dict:
        conventional_cost = fuel_volume_gallons * 2.50
        saf_cost = fuel_volume_gallons * 5.00
        subsidy = fuel_volume_gallons * 1.75
        
        return {
            "conventional_cost": conventional_cost,
            "saf_cost": saf_cost,
            "saf_premium": saf_cost - conventional_cost,
            "subsidy_value": subsidy,
            "net_saf_cost": saf_cost - subsidy,
            "net_premium_pct": round((saf_cost - subsidy - conventional_cost) / conventional_cost * 100, 1)
        }
    
    def production_capacity(self) -> Dict:
        return {
            "current_global_million_liters": 500,
            "demand_2030_million_liters": 5000,
            "gap_multiple": 10,
            "investment_needed_b": 100,
            "production_scale_up": "Critical bottleneck"
        }
