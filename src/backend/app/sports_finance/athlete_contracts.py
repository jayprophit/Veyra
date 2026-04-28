"""Athlete Contracts - Contract valuation"""
from typing import Dict

class AthleteContracts:
    """Analyze athlete contracts"""
    
    def contract_npv(self, annual_salary: float, years: int, 
                   discount_rate: float = 0.08) -> Dict:
        """Calculate NPV of guaranteed contract"""
        npv = sum(annual_salary / ((1 + discount_rate) ** y) for y in range(1, years + 1))
        total = annual_salary * years
        
        return {
            "total_value": total,
            "npv": round(npv, 0),
            "discount": round(total - npv, 0),
            "avg_annual": annual_salary
        }
    
    def endorsement_value(self, social_followers: int, 
                         engagement_rate: float) -> Dict:
        """Estimate endorsement earning potential"""
        # $0.01 per follower per year is rough benchmark
        base_value = social_followers * 0.01
        engagement_multiplier = 1 + (engagement_rate * 10)
        
        return {
            "estimated_annual": base_value * engagement_multiplier,
            "per_follower_value": 0.01 * engagement_multiplier
        }
