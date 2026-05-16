"""Green Methanol Economics"""
from typing import Dict

class GreenMethanol:
    """Renewable methanol for shipping"""
    
    def production_routes(self) -> Dict:
        return {
            "biomethanol": {
                "feedstock": "Agricultural waste, biogas",
                "co2_intensity": "Low",
                "cost_per_ton": 400,
                "maturity": "Commercial"
            },
            "e_methanol": {
                "feedstock": "CO2 + green H2",
                "co2_intensity": "Near zero",
                "cost_per_ton": 800,
                "maturity": "Pilot/demonstration"
            },
            "blue_methanol": {
                "feedstock": "Natural gas + CCS",
                "co2_intensity": "Reduced",
                "cost_per_ton": 350,
                "maturity": "Proposed"
            }
        }
    
    def shipping_applications(self) -> Dict:
        return {
            "maersk": {"order_dual_fuel_vessels": 25, "fuel_strategy": "E-methanol primary"},
            "euronav": {"trials": "Completed", "retrofit_consideration": True},
            "fuel_compatibility": {"engines": "Modified diesel", "storage": "New tanks needed"},
            "price_vs_hfo": {"green_methanol_premium": 3.0, "hfo_price_per_ton": 600}
        }
    
    def market_outlook(self) -> Dict:
        return {
            "demand_2030_million_tons": 10,
            "demand_2050_million_tons": 100,
            "production_2024_million_tons": 0.2,
            "investment_per_million_tons_capacity_m": 1500,
            "key_regions": ["Northern Europe", "Chile", "Saudi Arabia", "Australia"]
        }
    
    def project_economics(self) -> Dict:
        return {
            "capex_per_ton_yearly": 1000,
            "opex_breakdown": {"electricity": 0.60, "captured_co2": 0.15, "labor": 0.15, "other": 0.10},
            "breakeven_electricity_price": 0.03,
            "renewable_ppa_needed": "Long-term, low price"
        }
