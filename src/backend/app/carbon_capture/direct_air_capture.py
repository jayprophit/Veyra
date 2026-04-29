"""Direct Air Capture - DAC technology economics"""
from typing import Dict

class DirectAirCapture:
    """Analyze Direct Air Capture investments"""
    
    def __init__(self, capacity_tons_per_year: float, technology: str = "solid_sorbent"):
        self.capacity = capacity_tons_per_year
        self.tech = technology  # solid_sorbent, liquid_solvent, membrane
    
    def capex_analysis(self) -> Dict:
        costs = {
            "solid_sorbent": 600,  # $/ton/year
            "liquid_solvent": 800,
            "membrane": 1000
        }
        cost_per_ton = costs.get(self.tech, 700)
        total_capex = self.capacity * cost_per_ton
        
        return {
            "total_capex": round(total_capex, 0),
            "cost_per_ton_capacity": cost_per_ton,
            "equipment_share": 0.60,
            "installation_share": 0.25,
            "engineering_share": 0.15
        }
    
    def opex_per_ton(self) -> Dict:
        energy_cost = 2500  # MWh per ton CO2
        energy_price = 50  # $/MWh
        maintenance = 30
        labor = 20
        
        total_opex = (energy_cost * energy_price / 1000) + maintenance + labor
        
        return {
            "total_opex_per_ton": round(total_opex, 0),
            "energy_cost_share": round((energy_cost * energy_price / 1000) / total_opex * 100, 1),
            "maintenance": maintenance,
            "labor": labor
        }
    
    def project_economics(self, carbon_price: float, tax_credit_45q: float = 85) -> Dict:
        opex = self.opex_per_ton()["total_opex_per_ton"]
        revenue_per_ton = carbon_price + tax_credit_45q
        margin = revenue_per_ton - opex
        
        annual_revenue = self.capacity * revenue_per_ton
        annual_cost = self.capacity * opex
        annual_profit = self.capacity * margin
        
        capex = self.capex_analysis()["total_capex"]
        payback = capex / annual_profit if annual_profit > 0 else float('inf')
        
        return {
            "revenue_per_ton": revenue_per_ton,
            "opex_per_ton": opex,
            "margin_per_ton": margin,
            "annual_revenue": round(annual_revenue, 0),
            "annual_profit": round(annual_profit, 0),
            "simple_payback_years": round(payback, 1),
            "ltco2_per_ton": round(capex / self.capacity + opex * 20, 0)  # 20-year levelized
        }
