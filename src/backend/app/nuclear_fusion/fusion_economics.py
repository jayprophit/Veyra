"""Fusion Energy Economics"""
from typing import Dict

class FusionEconomics:
    """Analyze fusion power plant economics and investments"""
    
    def __init__(self, reactor_type: str = "tokamak"):
        self.reactor_type = reactor_type  # tokamak, stellarator, ICF, Z-pinch
    
    def levelized_cost(self, plant_size_mw: float = 1000) -> Dict:
        # Learning curve from fission and renewables
        first_of_a_kind = {"capex": 8e9, "fixed_om": 200e6, "fuel": 10e6}
        nth_of_a_kind = {"capex": 4e9, "fixed_om": 100e6, "fuel": 10e6}
        
        # LCOE calculation
        capacity_factor = 0.90
        annual_mwh = plant_size_mw * 8760 * capacity_factor
        
        # FOAK
        annual_cost_foak = first_of_a_kind["fixed_om"] + first_of_a_kind["fuel"] + \
                         (first_of_a_kind["capex"] * 0.06)  # 6% capital charge
        lcoe_foak = annual_cost_foak / annual_mwh
        
        # NOAK
        annual_cost_noak = nth_of_a_kind["fixed_om"] + nth_of_a_kind["fuel"] + \
                         (nth_of_a_kind["capex"] * 0.06)
        lcoe_noak = annual_cost_noak / annual_mwh
        
        return {
            "lcoe_foak_usd_mwh": round(lcoe_foak * 1000, 0),
            "lcoe_noak_usd_mwh": round(lcoe_noak * 1000, 0),
            "capacity_factor": capacity_factor,
            "annual_mwh": annual_mwh,
            "target_competitive": 50,  # $50/MWh target
            "timeline_to_competitive": "2040-2050"
        }
    
    def development_costs(self) -> Dict:
        stages = {
            "proof_of_principle": {"cost": 500e6, "duration": 5, "status": "Complete"},
            "scientific_breakeven": {"cost": 2e9, "duration": 10, "status": "Achieved (NIF 2022)"},
            "engineering_breakeven": {"cost": 10e9, "duration": 15, "status": "In progress"},
            "pilot_plant": {"cost": 20e9, "duration": 20, "status": "Planning"},
            "commercial": {"cost": 50e9, "duration": 30, "status": "2040s"}
        }
        
        total_invested_to_date = sum([s["cost"] for s in stages.values() if s["status"] in ["Complete", "Achieved (NIF 2022)"]])
        
        return {
            "stages": stages,
            "total_invested_to_date_billions": total_invested_to_date / 1e9,
            "total_to_commercial_billions": sum([s["cost"] for s in stages.values()]) / 1e9,
            "funding_sources": ["Government (80%)", "Private (20%)"]
        }
    
    def market_opportunity(self) -> Dict:
        # Total electricity market
        global_generation_twh = 28000
        fusion_penetration_2050 = 0.10  # 10%
        
        addressable_twh = global_generation_twh * fusion_penetration_2050
        revenue_at_100_mwh = addressable_twh * 1e6 * 100  # $100/MWh
        
        # Value chain
        magnets = revenue_at_100_mwh * 0.20
        fuel = revenue_at_100_mwh * 0.05
        construction = revenue_at_100_mwh * 0.30
        operations = revenue_at_100_mwh * 0.45
        
        return {
            "addressable_twh_2050": addressable_twh,
            "addressable_revenue_billions": revenue_at_100_mwh / 1e9,
            "value_chain": {
                "superconducting_magnets": magnets / 1e9,
                "tritium_fuel": fuel / 1e9,
                "plant_construction": construction / 1e9,
                "plant_operations": operations / 1e9
            },
            "competitive_advantage": "Baseload carbon-free, no long-lived waste"
        }
    
    def investment_landscape(self) -> Dict:
        return {
            "public_companies": {
                "Commonwealth_Fusion": {"funding": 2e9, "approach": "SPARC tokamak", "timeline": "2030s"},
                "TAE_Technologies": {"funding": 1e9, "approach": "FRC aneutronic", "timeline": "2030s"},
                "Helion": {"funding": 0.5e9, "approach": "Magneto-inertial", "timeline": "2028"}
            },
            "government_projects": {
                "ITER": {"cost": 25e9, "partners": 35, "first_plasma": 2025},
                "DEMO": {"cost": "TBD", "partners": "ITER+", "operation": 2050},
                "UK_STEP": {"cost": 2e9, "timeline": 2040}
            },
            "risk_assessment": "High technical risk, enormous potential reward"
        }
