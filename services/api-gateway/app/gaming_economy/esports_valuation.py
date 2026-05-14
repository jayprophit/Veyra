"""Esports Valuation - Team and league valuations"""
from typing import Dict

class EsportsValuation:
    """Valuate esports teams and leagues"""
    
    def team_valuation(self, revenue: float,
                      growth_rate: float,
                      brand_strength: float) -> Dict:
        """Value esports team using revenue multiple"""
        base_multiple = 4
        growth_premium = growth_rate * 20
        brand_premium = brand_strength * 2
        total_multiple = base_multiple + growth_premium + brand_premium
        valuation = revenue * total_multiple
        return {"revenue": revenue, "multiple": total_multiple, "valuation": valuation}
    
    def player_contract_value(self, salary: float,
                             performance_metrics: Dict,
                             social_following: int) -> Dict:
        """Value player contract"""
        performance_bonus = performance_metrics.get("mvp_votes", 0) * 100000
        social_value = social_following * 0.05
        total_value = salary + performance_bonus + social_value
        return {"base_salary": salary, "performance_bonus": performance_bonus, "social_value": social_value, "total": total_value}
    
    def tournament_prize_pool(self, entrants: int,
                           entry_fee: float,
                           sponsor_contribution: float) -> Dict:
        """Calculate tournament economics"""
        entry_revenue = entrants * entry_fee
        total_prize = entry_revenue + sponsor_contribution
        return {"total_prize_pool": total_prize, "organizer_revenue": entry_revenue * 0.2, "sponsor_roi": sponsor_contribution / (entrants * 1000) if entrants > 0 else 0}
