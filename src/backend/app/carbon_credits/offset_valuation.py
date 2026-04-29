"""Carbon Offset Valuation"""
from typing import Dict

class OffsetValuation:
    """Value carbon offset projects and credits"""
    
    def __init__(self, project_type: str = "forestry"):
        self.project_type = project_type  # forestry, renewable, cookstoves, etc
    
    def project_costs(self, annual_credits_tonnes: int = 100000) -> Dict:
        costs = {
            "forestry": {"development": 5, "verification": 2, "monitoring": 1},
            "renewable": {"development": 2, "verification": 1, "monitoring": 0.5},
            "cookstoves": {"development": 8, "verification": 3, "monitoring": 2},
            "direct_air_capture": {"development": 50, "verification": 5, "monitoring": 3}
        }
        
        c = costs.get(self.project_type, costs["forestry"])
        
        # Per tonne costs
        dev_per_tonne = c["development"]
        verify_per_tonne = c["verification"]
        monitor_per_tonne = c["monitoring"]
        
        total_cost = dev_per_tonne + verify_per_tonne + monitor_per_tonne
        
        return {
            "development_cost_per_tonne": dev_per_tonne,
            "verification_cost_per_tonne": verify_per_tonne,
            "monitoring_cost_per_tonne": monitor_per_tonne,
            "total_cost_per_tonne": total_cost,
            "annual_project_cost": total_cost * annual_credits_tonnes
        }
    
    def credit_pricing(self, vintage: int = 2024, certification: str = "vcs") -> Dict:
        base_prices = {
            "vcs": 8,
            "gold_standard": 12,
            "car": 4,
            "climate_action_reserve": 15
        }
        
        base = base_prices.get(certification, 8)
        
        # Vintage premium/discount
        current_year = 2024
        vintage_adjustment = (vintage - current_year) * 0.50  # $0.50 per year older
        
        # Quality adjustments
        quality_multiplier = 1.0
        if self.project_type == "direct_air_capture":
            quality_multiplier = 8.0  # $400-600/tonne
        elif self.project_type == "forestry":
            quality_multiplier = 1.2
        
        price = (base + vintage_adjustment) * quality_multiplier
        
        return {
            "base_price_per_tonne": round(price, 2),
            "vintage_premium": vintage_adjustment,
            "quality_multiplier": quality_multiplier,
            "certification": certification,
            "vintage": vintage
        }
    
    def project_returns(self, annual_credits: int = 100000, project_life_years: int = 20) -> Dict:
        costs = self.project_costs(annual_credits)
        pricing = self.credit_pricing()
        
        annual_revenue = annual_credits * pricing["base_price_per_tonne"]
        annual_cost = costs["annual_project_cost"]
        annual_profit = annual_revenue - annual_cost
        
        # Initial development cost
        initial_capex = costs["development_cost_per_tonne"] * annual_credits * 3  # 3 years to ramp
        
        # Simple NPV calculation (conservative)
        npv = -initial_capex
        for year in range(1, project_life_years + 1):
            cash_flow = annual_profit / ((1.10) ** year)  # 10% discount
            npv += cash_flow
        
        irr_approx = (annual_profit / initial_capex) * 100 if initial_capex > 0 else 0
        
        return {
            "annual_revenue": round(annual_revenue, 0),
            "annual_cost": round(annual_cost, 0),
            "annual_profit": round(annual_profit, 0),
            "initial_capex": round(initial_capex, 0),
            "project_npv": round(npv, 0),
            "irr_approximate_pct": round(irr_approx, 1),
            "payback_years": round(initial_capex / annual_profit, 1) if annual_profit > 0 else float('inf')
        }
    
    def additionality_assessment(self) -> Dict:
        scores = {
            "forestry": 0.7,
            "renewable": 0.5,
            "cookstoves": 0.8,
            "direct_air_capture": 0.95
        }
        
        score = scores.get(self.project_type, 0.6)
        
        return {
            "additionality_score": score,
            "rating": "High" if score > 0.8 else "Medium" if score > 0.6 else "Low",
            "risk_factors": ["Baseline determination", "Leakage", "Permanence"],
            "recommendation": "Strong" if score > 0.8 else "Moderate" if score > 0.6 else "Weak"
        }
