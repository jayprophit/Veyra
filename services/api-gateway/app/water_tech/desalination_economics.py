"""Desalination Economics"""
from typing import Dict

class DesalinationEconomics:
    """Analyze seawater and brackish water desalination projects"""
    
    def __init__(self, capacity_m3_per_day: float = 100000, technology: str = "ro"):
        self.capacity = capacity_m3_per_day
        self.tech = technology  # ro (reverse osmosis), thermal, ed
    
    def capex_analysis(self) -> Dict:
        costs_per_m3 = {
            "ro": 1200,  # $/m3/day capacity
            "thermal": 2000,
            "electrodialysis": 800
        }
        
        cost_per_m3 = costs_per_m3.get(self.tech, 1200)
        plant_cost = self.capacity * cost_per_m3
        
        # Intake/outfall
        intake = plant_cost * 0.15
        
        # Land, buildings, infrastructure
        infrastructure = plant_cost * 0.20
        
        total = plant_cost + intake + infrastructure
        
        return {
            "total_capex_millions": round(total / 1e6, 1),
            "per_m3_day_capacity": cost_per_m3,
            "plant_equipment": round(plant_cost / 1e6, 1),
            "intake_outfall": round(intake / 1e6, 1),
            "infrastructure": round(infrastructure / 1e6, 1),
            "technology": self.tech
        }
    
    def operating_cost(self, energy_cost_kwh: float = 0.08) -> Dict:
        # Energy consumption by technology
        energy_per_m3 = {
            "ro": 3.5,  # kWh/m3
            "thermal": 15.0,
            "electrodialysis": 2.0
        }
        
        kwh_per_m3 = energy_per_m3.get(self.tech, 3.5)
        energy_cost = kwh_per_m3 * energy_cost_kwh
        
        # Other costs
        chemicals = 0.10
        labor = 0.15
        maintenance = 0.20
        membrane_replacement = 0.10  # RO specific
        
        total_opex = energy_cost + chemicals + labor + maintenance + membrane_replacement
        
        return {
            "total_cost_per_m3": round(total_opex, 2),
            "energy_cost_per_m3": round(energy_cost, 2),
            "energy_intensity_kwh_m3": kwh_per_m3,
            "energy_pct_of_total": round(energy_cost / total_opex * 100, 1),
            "annual_opex_millions": round(total_opex * self.capacity * 365 / 1e6, 1)
        }
    
    def water_cost_comparison(self) -> Dict:
        sources = {
            "desalination": self.operating_cost()["total_cost_per_m3"],
            "surface_water": 0.50,
            "groundwater": 0.80,
            "water_reuse": 0.60,
            "imported_water": 2.00
        }
        
        desal_cost = sources["desalination"]
        
        return {
            "source_costs_usd_m3": sources,
            "desalination_premium": round(desal_cost / sources["surface_water"], 1),
            "competitive_vs_imported": desal_cost < sources["imported_water"],
            "typical_retail_price": 3.00,
            "margin_for_utility": round(3.00 - desal_cost, 2)
        }
    
    def project_finance(self, debt_pct: float = 0.70, project_life: int = 25) -> Dict:
        capex = self.capex_analysis()["total_capex_millions"] * 1e6
        annual_opex = self.operating_cost()["annual_opex_millions"] * 1e6
        
        debt = capex * debt_pct
        equity = capex * (1 - debt_pct)
        
        # Revenue
        water_price = 2.50  # $/m3
        annual_production = self.capacity * 365 * 0.90  # 90% availability
        annual_revenue = annual_production * water_price
        
        # Debt service
        interest_rate = 0.06
        debt_term = 20
        
        # Simple levelized calculation
        annual_debt_service = debt * (interest_rate / (1 - (1 + interest_rate) ** -debt_term))
        
        ebitda = annual_revenue - annual_opex
        debt_service_coverage = ebitda / annual_debt_service
        
        return {
            "capex_millions": capex / 1e6,
            "debt_millions": debt / 1e6,
            "equity_millions": equity / 1e6,
            "annual_revenue_millions": annual_revenue / 1e6,
            "annual_ebitda_millions": ebitda / 1e6,
            "dscr": round(debt_service_coverage, 2),
            "debt_pct": debt_pct * 100,
            "project_irr_pct": round((ebitda / capex) * 100, 1)
        }
