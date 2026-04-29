"""Commercialization - Nanotech product launch"""
from typing import Dict

class Commercialization:
    """Nanotech commercialization analysis"""
    
    def time_to_revenue(self, tech_readiness: int,  # 1-9
                       regulatory_path: str,
                       market_complexity: str) -> Dict:
        """Estimate time to commercial revenue"""
        base_time = (9 - tech_readiness) * 12  # months per TRL level
        
        reg_add = {"none": 0, "simple": 12, "complex": 36, "pharma": 60}
        market_add = {"simple": 6, "moderate": 12, "complex": 24}
        
        total_months = base_time + reg_add.get(regulatory_path, 12) + market_add.get(market_complexity, 12)
        
        return {
            "current_trl": tech_readiness,
            "base_development": base_time,
            "regulatory_time": reg_add.get(regulatory_path, 12),
            "market_time": market_add.get(market_complexity, 12),
            "total_months": total_months,
            "years_to_revenue": round(total_months / 12, 1)
        }
    
    def adoption_curve_estimate(self, price_premium: float,
                               performance_gain: float,
                               incumbent_moat: str) -> Dict:
        """Estimate technology adoption curve"""
        value_ratio = performance_gain / price_premium if price_premium > 0 else 0
        
        moat_delay = {"strong": 5, "moderate": 3, "weak": 1}
        years_to_inflection = moat_delay.get(incumbent_moat, 3) / max(value_ratio, 0.5)
        
        return {
            "value_ratio": round(value_ratio, 2),
            "years_to_inflection": round(years_to_inflection, 1),
            "adoption_speed": "fast" if years_to_inflection < 3 else "medium" if years_to_inflection < 7 else "slow"
        }
