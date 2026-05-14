"""Municipal Waste to Energy Economics"""
from typing import Dict

class MunicipalWasteEnergy:
    """Analyze waste-to-energy plant investments"""
    
    def __init__(self, capacity_tons_per_day: float = 1000, technology: str = "incineration"):
        self.capacity = capacity_tons_per_day
        self.tech = technology  # incineration, gasification, pyrolysis
    
    def plant_capex(self) -> Dict:
        costs_per_ton = {
            "incineration": 250000,  # $/ton/day
            "gasification": 300000,
            "pyrolysis": 350000
        }
        
        cost_per_ton = costs_per_ton.get(self.tech, 250000)
        plant_cost = self.capacity * cost_per_ton
        
        # Additional systems
        emission_control = plant_cost * 0.20
        grid_connection = plant_cost * 0.05
        civil_works = plant_cost * 0.10
        
        total = plant_cost + emission_control + grid_connection + civil_works
        
        return {
            "total_capex_millions": round(total / 1e6, 1),
            "per_ton_day_capacity": cost_per_ton,
            "plant_equipment_millions": round(plant_cost / 1e6, 1),
            "emission_control_millions": round(emission_control / 1e6, 1),
            "annual_waste_processed_tons": self.capacity * 365
        }
    
    def revenue_streams(self, electricity_price_mwh: float = 80) -> Dict:
        # Electricity generation (incineration: 600 kWh/ton)
        kwh_per_ton = 600
        daily_mwh = (self.capacity * kwh_per_ton) / 1000
        annual_mwh = daily_mwh * 365
        
        electricity_revenue = annual_mwh * electricity_price_mwh
        
        # Tipping fee (waste disposal fee)
        tipping_fee_per_ton = 70
        annual_tipping = self.capacity * 365 * tipping_fee_per_ton
        
        # Metal recovery
        metal_recovery_per_ton = 5
        annual_metal = self.capacity * 365 * metal_recovery_per_ton
        
        total = electricity_revenue + annual_tipping + annual_metal
        
        return {
            "electricity_revenue_millions": round(electricity_revenue / 1e6, 1),
            "tipping_fee_revenue_millions": round(annual_tipping / 1e6, 1),
            "metal_recovery_millions": round(annual_metal / 1e6, 1),
            "total_revenue_millions": round(total / 1e6, 1),
            "annual_mwh": annual_mwh,
            "revenue_sources": ["Electricity", "Tipping fees", "Metal recovery"]
        }
    
    def operating_costs(self) -> Dict:
        # Fixed costs
        labor = 30  # $/ton
        maintenance = 25
        chemicals = 8
        insurance = 5
        ash_disposal = 12
        
        total_per_ton = labor + maintenance + chemicals + insurance + ash_disposal
        annual_opex = total_per_ton * self.capacity * 365
        
        return {
            "cost_per_ton": total_per_ton,
            "annual_opex_millions": round(annual_opex / 1e6, 1),
            "cost_breakdown": {
                "labor": labor,
                "maintenance": maintenance,
                "chemicals": chemicals,
                "insurance": insurance,
                "ash_disposal": ash_disposal
            }
        }
    
    def project_economics(self, electricity_price: float = 80) -> Dict:
        capex = self.plant_capex()["total_capex_millions"] * 1e6
        revenue = self.revenue_streams(electricity_price)["total_revenue_millions"] * 1e6
        opex = self.operating_costs()["annual_opex_millions"] * 1e6
        
        ebitda = revenue - opex
        
        # Simple metrics
        payback = capex / ebitda if ebitda > 0 else float('inf')
        roi = ebitda / capex * 100
        
        return {
            "capex_millions": capex / 1e6,
            "annual_revenue_millions": revenue / 1e6,
            "annual_opex_millions": opex / 1e6,
            "ebitda_millions": round(ebitda / 1e6, 1),
            "payback_years": round(payback, 1),
            "roi_pct": round(roi, 1),
            "profit_margin_pct": round((revenue - opex) / revenue * 100, 1)
        }
    
    def environmental_benefits(self) -> Dict:
        # Avoided landfill emissions
        tons_annual = self.capacity * 365
        methane_avoided = tons_annual * 0.5  # 0.5 ton CO2eq/ton waste
        
        # Renewable energy
        kwh_per_ton = 600
        renewable_mwh = (tons_annual * kwh_per_ton) / 1000
        
        # Carbon credits potential
        carbon_price = 50  # $/ton
        credit_value = methane_avoided * carbon_price
        
        return {
            "waste_diverted_from_landfill_tons": tons_annual,
            "co2eq_avoided_tons": methane_avoided,
            "renewable_energy_mwh": renewable_mwh,
            "carbon_credit_value_millions": round(credit_value / 1e6, 1),
            "landfill_space_saved_m3": tons_annual * 1.5
        }
