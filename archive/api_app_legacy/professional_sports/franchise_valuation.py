"""Franchise Valuation - Professional sports teams"""
from typing import Dict

class FranchiseValuation:
    """Value professional sports franchises"""
    
    def team_enterprise_value(self, revenue: float,
                            operating_income: float,
                            growth_rate: float,
                            market_size: int) -> Dict:
        """Calculate sports franchise value"""
        # Revenue multiple based on sport and market
        base_multiple = 6.0
        growth_premium = min(growth_rate * 20, 3)
        market_premium = min(market_size / 5e6, 2)
        
        multiple = base_multiple + growth_premium + market_premium
        enterprise_value = revenue * multiple
        
        return {
            "revenue": revenue,
            "operating_income": operating_income,
            "revenue_multiple": round(multiple, 1),
            "enterprise_value": round(enterprise_value, 0),
            "operating_margin": round(operating_income / revenue * 100, 1) if revenue > 0 else 0
        }
    
    def salary_cap_efficiency(self, payroll: float,
                             wins: int,
                             cap_amount: float,
                             playoff_revenue: float) -> Dict:
        """Analyze salary cap efficiency"""
        efficiency = wins / (payroll / cap_amount) if payroll > 0 else 0
        cost_per_win = payroll / wins if wins > 0 else 0
        
        return {
            "payroll": payroll,
            "salary_cap": cap_amount,
            "cap_utilization": round(payroll / cap_amount * 100, 1),
            "wins": wins,
            "cost_per_win": round(cost_per_win, 0),
            "efficiency_score": round(efficiency, 2),
            "playoff_revenue": playoff_revenue
        }
