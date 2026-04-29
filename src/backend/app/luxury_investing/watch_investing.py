"""Watch Investing - Luxury timepiece analytics"""
from typing import Dict

class WatchInvesting:
    """Analyze luxury watch investments"""
    
    def investment_grade_score(self, brand: str,
                            model: str,
                            production_volume: int,
                            waitlist_months: int,
                            historical_appreciation: float) -> Dict:
        """Score watch as investment"""
        brand_scores = {
            "patek_philippe": 10, "rolex": 9, "audemars_piguet": 9,
            "vacheron_constantin": 8, "omega": 6, "tudor": 5
        }
        
        brand_score = brand_scores.get(brand.lower(), 5)
        scarcity_score = min(waitlist_months / 12, 5)  # Max 5 for 5+ years
        volume_score = max(0, 5 - production_volume / 1000)
        appreciation_score = min(historical_appreciation * 10, 10)
        
        total_score = brand_score + scarcity_score + volume_score + appreciation_score
        
        return {
            "brand": brand,
            "model": model,
            "investment_grade": "AAA" if total_score > 25 else "AA" if total_score > 20 else "A" if total_score > 15 else "B",
            "score": round(total_score, 1),
            "components": {
                "brand": brand_score,
                "scarcity": round(scarcity_score, 1),
                "volume": round(volume_score, 1),
                "appreciation": round(appreciation_score, 1)
            }
        }
    
    def flip_potential(self, retail_price: float,
                      secondary_price: float,
                      hold_period_months: int) -> Dict:
        """Calculate watch flipping potential"""
        profit = secondary_price - retail_price
        profit_pct = (profit / retail_price) * 100 if retail_price > 0 else 0
        annualized = profit_pct * (12 / hold_period_months) if hold_period_months > 0 else 0
        
        return {
            "retail_price": retail_price,
            "secondary_price": secondary_price,
            "gross_profit": round(profit, 0),
            "profit_percent": round(profit_pct, 1),
            "annualized_return": round(annualized, 1),
            "flip_recommendation": "strong" if annualized > 50 else "moderate" if annualized > 20 else "weak"
        }
    
    def vintage_premium(self, age_years: int,
                      condition_grade: str,
                      original_box_papers: bool,
                      service_history: bool) -> Dict:
        """Calculate vintage watch premiums"""
        age_premium = min(age_years * 0.02, 1.0)  # Max 100%
        
        condition_multipliers = {
            "mint": 2.0, "excellent": 1.5, "good": 1.2, "fair": 1.0, "poor": 0.7
        }
        condition_mult = condition_multipliers.get(condition_grade.lower(), 1.0)
        
        box_papers_bonus = 0.3 if original_box_papers else 0
        service_bonus = 0.1 if service_history else 0
        
        total_multiplier = 1 + age_premium + box_papers_bonus + service_bonus
        final_multiplier = total_multiplier * condition_mult
        
        return {
            "age_years": age_years,
            "condition": condition_grade,
            "vintage_multiplier": round(final_multiplier, 2),
            "age_premium": round(age_premium * 100, 1),
            "condition_adjustment": round((condition_mult - 1) * 100, 1),
            "documentation_bonus": round((box_papers_bonus + service_bonus) * 100, 1)
        }
