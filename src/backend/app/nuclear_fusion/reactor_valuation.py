"""Fusion Reactor Company Valuation"""
from typing import Dict

class ReactorValuation:
    """Value fusion reactor companies and projects"""
    
    def __init__(self, company_stage: str = "series_c"):
        self.stage = company_stage  # seed, series_a, series_c, pre_ipo
    
    def company_valuation(self, revenue: float = 0) -> Dict:
        # Fusion companies are pre-revenue, valued on milestones
        milestone_values = {
            "seed": {"valuation": 50e6, "milestone": "Concept validation"},
            "series_a": {"valuation": 200e6, "milestone": "Proof of concept"},
            "series_b": {"valuation": 500e6, "milestone": "Plasma achievement"},
            "series_c": {"valuation": 1e9, "milestone": "Net energy gain"},
            "pre_ipo": {"valuation": 5e9, "milestone": "Pilot plant commitment"}
        }
        
        data = milestone_values.get(self.stage, milestone_values["seed"])
        
        return {
            "valuation_millions": data["valuation"] / 1e6,
            "key_milestone": data["milestone"],
            "stage": self.stage,
            "valuation_method": "Milestone-based (DCF not applicable)",
            "comparable_transactions": "Commonwealth $1.8B, Helion $500M"
        }
    
    def power_plant_npv(self, size_mw: float = 1000, construction_years: int = 7) -> Dict:
        # Conservative NPV for a fusion plant
        capex = 5e9  # $5/W
        fixed_om = 150e6  # Annual
        fuel = 20e6  # Tritium
        
        # Revenue
        capacity_factor = 0.85
        annual_mwh = size_mw * 8760 * capacity_factor
        price_mwh = 80  # Premium for clean baseload
        annual_revenue = annual_mwh * price_mwh
        
        annual_cost = fixed_om + fuel
        
        # NPV over 40 years
        discount = 0.08
        npv = -capex
        for year in range(1, 41):
            if year <= construction_years:
                cash_flow = -capex / construction_years  # Construction spend
            else:
                cash_flow = annual_revenue - annual_cost
            npv += cash_flow / ((1 + discount) ** year)
        
        return {
            "npv_billions": round(npv / 1e9, 1),
            "lcoe_usd_mwh": round((annual_cost + (capex * discount)) / annual_mwh * 1000, 0),
            "payback_years": round(capex / (annual_revenue - annual_cost), 1),
            "note": "Pre-commercial technology - high uncertainty"
        }
    
    def component_suppliers(self) -> Dict:
        return {
            "superconducting_magnets": {
                "market_size_billions": 10,
                "key_suppliers": ["Tokamak Energy", "Commonwealth", "MIT"],
                "technology": "REBCO high-temperature superconductor"
            },
            "vacuum_vessels": {
                "market_size_billions": 5,
                "key_suppliers": ["Westinghouse", "General Atomics"],
                "technology": "Stainless steel + shielding"
            },
            "tritium_breeding": {
                "market_size_billions": 2,
                "key_suppliers": ["ITER partners"],
                "technology": "Lithium blanket"
            },
            "control_systems": {
                "market_size_billions": 3,
                "key_suppliers": ["Siemens", "General Electric"],
                "technology": "Real-time plasma control"
            }
        }
    
    def risk_analysis(self) -> Dict:
        return {
            "technical_risks": {
                "plasma_instability": "Medium - Q>1 achieved, Q>10 needed",
                "materials_degradation": "High - neutron damage uncertain",
                "tritium_supply": "Medium - breeding blanket unproven"
            },
            "commercial_risks": {
                "cost_overruns": "Very High - FOAK plants always over",
                "competition": "Medium - fission, renewables improving",
                "regulatory": "Medium - new framework needed"
            },
            "timeline_risks": {
                "2030_promise": "Low probability",
                "2040_grid": "Medium probability",
                "2050_widespread": "Higher probability"
            },
            "investment_thesis": "Asymmetric payoff - small probability of massive returns"
        }
