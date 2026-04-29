"""Sustainable Aviation Fuel Production Economics"""
from typing import Dict

class SAFProduction:
    """Analyze SAF production facility investments"""
    
    def __init__(self, pathway: str = "HEFA", capacity_kt_per_year: float = 100):
        self.pathway = pathway  # HEFA, AtJ, FT, PtL
        self.capacity = capacity_kt_per_year  # Kilotons per year
    
    def capex_analysis(self) -> Dict:
        costs_per_kt = {
            "HEFA": 1500,  # $/ton capacity
            "AtJ": 2500,
            "FT": 4000,
            "PtL": 8000
        }
        cost_per_kt = costs_per_kt.get(self.pathway, 2000)
        total = self.capacity * 1000 * cost_per_kt
        
        return {
            "total_capex": round(total, 0),
            "cost_per_kt_capacity": cost_per_kt,
            "pathway_maturity": "Commercial" if self.pathway == "HEFA" else "Emerging",
            "blending_limit_pct": 50 if self.pathway == "HEFA" else 100
        }
    
    def production_cost(self, feedstock_cost_per_ton: float) -> Dict:
        conversion_rates = {
            "HEFA": 0.95,
            "AtJ": 0.90,
            "FT": 0.70,
            "PtL": 0.45
        }
        yield_rate = conversion_rates.get(self.pathway, 0.80)
        
        energy_cost = 50  # $/MWh
        energy_per_ton = 2  # MWh per ton SAF
        utility_cost = energy_cost * energy_per_ton
        
        catalyst_chemicals = 30
        labor_maintenance = 40
        
        feedstock_needed = 1 / yield_rate
        feedstock_cost = feedstock_needed * feedstock_cost_per_ton
        
        total_cost = feedstock_cost + utility_cost + catalyst_chemicals + labor_maintenance
        
        return {
            "production_cost_per_ton": round(total_cost, 0),
            "feedstock_cost_share": round(feedstock_cost / total_cost * 100, 1),
            "yield_rate": round(yield_rate * 100, 1),
            "feedstock_tons_per_saf_ton": round(feedstock_needed, 2)
        }
    
    def vs_jet_fuel_economics(self, jet_fuel_price_per_ton: float, carbon_credit: float = 100) -> Dict:
        # SAF typically costs 2-5x conventional jet fuel
        prod_cost = self.production_cost(800)["production_cost_per_ton"]
        
        premium = prod_cost - jet_fuel_price_per_ton
        premium_pct = (premium / jet_fuel_price_per_ton) * 100 if jet_fuel_price_per_ton > 0 else 0
        
        # Carbon savings (SAF reduces lifecycle emissions 50-80%)
        carbon_intensity_jet = 3.15  # tCO2 per ton jet fuel
        carbon_intensity_saf = {
            "HEFA": 0.8,
            "AtJ": 1.2,
            "FT": 0.5,
            "PtL": 0.1
        }.get(self.pathway, 1.0)
        
        carbon_saved = carbon_intensity_jet - carbon_intensity_saf
        carbon_revenue = carbon_saved * carbon_credit
        
        net_cost = prod_cost - carbon_revenue
        effective_premium = net_cost - jet_fuel_price_per_ton
        
        return {
            "conventional_jet_cost": jet_fuel_price_per_ton,
            "saf_production_cost": prod_cost,
            "premium_per_ton": round(premium, 0),
            "premium_percentage": round(premium_pct, 1),
            "carbon_saved_per_ton": round(carbon_saved, 2),
            "carbon_revenue_per_ton": round(carbon_revenue, 0),
            "effective_cost_after_carbon": round(net_cost, 0),
            "green_premium_required": round(effective_premium, 0)
        }
