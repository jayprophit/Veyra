"""Biofoundry Economics"""
from typing import Dict

class BiofoundryEconomics:
    """Analyze automated bioengineering facility investments"""
    
    def __init__(self, throughput: str = "high"):
        self.throughput = throughput  # low, medium, high
    
    def facility_capex(self) -> Dict:
        configs = {
            "low": {"base": 5e6, "automation": 2e6, "annual_runs": 1000},
            "medium": {"base": 15e6, "automation": 8e6, "annual_runs": 5000},
            "high": {"base": 50e6, "automation": 30e6, "annual_runs": 20000}
        }
        
        c = configs.get(self.throughput, configs["medium"])
        total = c["base"] + c["automation"]
        
        return {
            "total_capex": round(total, 0),
            "infrastructure": c["base"],
            "automation_systems": c["automation"],
            "annual_design_build_test_runs": c["annual_runs"],
            "cost_per_run": round(total / c["annual_runs"], 0)
        }
    
    def revenue_model(self, success_rate: float = 0.15) -> Dict:
        # Revenue from successful strain development
        projects_per_year = self.facility_capex()["annual_design_build_test_runs"] / 100  # 100 runs per project
        successful_projects = projects_per_year * success_rate
        
        # Revenue models
        milestone_payments = successful_projects * 2e6  # $2M per milestone
        royalty_stream = successful_projects * 5e6  # $5M NPV of royalties
        
        total_revenue = milestone_payments + royalty_stream
        
        return {
            "projects_per_year": projects_per_year,
            "successful_projects": round(successful_projects, 1),
            "milestone_revenue": round(milestone_payments, 0),
            "royalty_revenue": round(royalty_stream, 0),
            "total_annual_revenue": round(total_revenue, 0)
        }
    
    def partner_economics(self, partner_type: str = "pharma") -> Dict:
        structures = {
            "pharma": {"upfront": 10e6, "milestones": 50e6, "royalty": 0.05},
            "biotech": {"upfront": 5e6, "milestones": 25e6, "royalty": 0.03},
            "startup": {"upfront": 1e6, "milestones": 10e6, "royalty": 0.02}
        }
        
        deal = structures.get(partner_type, structures["pharma"])
        
        return {
            "partner_type": partner_type,
            "upfront_payment": deal["upfront"],
            "total_milestones": deal["milestones"],
            "royalty_rate": deal["royalty"],
            "total_potential": deal["upfront"] + deal["milestones"]
        }
    
    def vs_traditional_rnd(self) -> Dict:
        # Traditional strain development
        traditional_time = 36  # months
        traditional_cost = 5e6
        
        # Biofoundry approach
        foundry_time = 12  # months
        foundry_cost = self.facility_capex()["cost_per_run"] * 50  # 50 runs
        
        return {
            "traditional_time_months": traditional_time,
            "traditional_cost": traditional_cost,
            "biofoundry_time_months": foundry_time,
            "biofoundry_cost": foundry_cost,
            "time_savings_months": traditional_time - foundry_time,
            "cost_savings_pct": round((traditional_cost - foundry_cost) / traditional_cost * 100, 1),
            "advantage": "3x faster, lower cost per strain"
        }
