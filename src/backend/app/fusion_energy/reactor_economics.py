"""Fusion Reactor Economics - Commercial fusion power analysis"""
from typing import Dict

class FusionReactorEconomics:
    """Analyze fusion reactor investments and LCOE"""
    
    def __init__(self, reactor_type: str = "tokamak", net_power_mw: float = 500):
        self.reactor_type = reactor_type  # tokamak, stellarator, ICF, MCF
        self.net_power = net_power_mw
    
    def development_cost(self, stage: str = "prototype") -> Dict:
        costs = {
            "concept": 100e6,
            "prototype": 2e9,
            "pilot": 5e9,
            "commercial": 10e9
        }
        
        return {
            "stage": stage,
            "total_cost": costs.get(stage, 2e9),
            "govt_funding_pct": 50 if stage in ["concept", "prototype"] else 20,
            "private_pct": 50 if stage in ["concept", "prototype"] else 80,
            "timeline_years": {"concept": 5, "prototype": 10, "pilot": 15, "commercial": 20}.get(stage, 10)
        }
    
    def projected_lcoe(self, year: int = 2050) -> Dict:
        # LCOE projections based on learning curves
        lcoe_projections = {
            2035: 200,   # $/MWh - first commercial
            2040: 120,
            2050: 80,
            2060: 50     # Mature technology
        }
        
        lcoe = lcoe_projections.get(year, 100)
        
        return {
            "lcoe_usd_per_mwh": lcoe,
            "year": year,
            "vs_nuclear": lcoe - 70,
            "vs_solar_wind": lcoe - 40,
            "competitive": lcoe < 100
        }
    
    def investment_opportunities(self) -> Dict:
        companies = [
            ("Commonwealth Fusion", 2e9, "tokamak"),
            ("TAE Technologies", 1.2e9, "field_reversed"),
            ("Helion Energy", 0.5e9, "pulsed_mcf"),
            ("Zap Energy", 0.2e9, "sheared_flow"),
        ]
        
        return {
            "total_private_funding": sum(c[1] for c in companies),
            "company_count": len(companies),
            "avg_valuation": sum(c[1] for c in companies) / len(companies),
            "leading_approach": "tokamak",
            "risk_profile": "High risk / High reward"
        }
    
    def grid_integration_value(self, baseload_capacity_mw: float) -> Dict:
        # Fusion provides baseload power with zero emissions
        capacity_factor = 0.85
        annual_mwh = baseload_capacity_mw * 8760 * capacity_factor
        
        # Value as baseload vs intermittent renewables
        grid_stability_value = 20  # $/MWh premium for baseload
        capacity_payment = 100000  # $/MW/year for capacity market
        
        return {
            "annual_generation_mwh": round(annual_mwh, 0),
            "capacity_factor": capacity_factor,
            "grid_stability_premium": grid_stability_value,
            "capacity_payment_annual": baseload_capacity_mw * capacity_payment,
            "firm_power_value": round(annual_mwh * grid_stability_value / 1e6, 2)  # Millions
        }
