"""Celebrity Economics - Net worth and earning potential"""
from typing import Dict

class CelebrityEconomics:
    """Analyze celebrity earning potential and net worth"""
    
    def net_worth_estimate(self, annual_earnings: float, assets: float,
                          liabilities: float, career_stage: str) -> Dict:
        """Estimate celebrity net worth"""
        # Career stage multipliers for future earnings
        stage_mult = {
            "rising": 5, "peak": 3, "established": 2, 
            "mature": 1.5, "legacy": 1
        }
        
        multiplier = stage_mult.get(career_stage.lower(), 2)
        future_earnings_value = annual_earnings * multiplier
        
        net_worth = assets - liabilities + future_earnings_value * 0.3
        
        return {
            "estimated_net_worth": round(net_worth, 0),
            "tangible_assets": assets,
            "liabilities": liabilities,
            "future_earnings_value": round(future_earnings_value, 0),
            "career_stage": career_stage,
            "wealth_tier": self._wealth_tier(net_worth)
        }
    
    def _wealth_tier(self, net_worth: float) -> str:
        """Classify wealth tier"""
        if net_worth > 1e9:
            return "billionaire"
        elif net_worth > 100e6:
            return "centimillionaire"
        elif net_worth > 10e6:
            return "decamillionaire"
        elif net_worth > 1e6:
            return "millionaire"
        else:
            return "aspirational"
    
    def earning_potential(self, current_earnings: float, growth_rate: float,
                         diversification_score: float) -> Dict:
        """Project future earning potential"""
        # Diversification bonus
        div_bonus = diversification_score * 0.5
        
        # 5 year projection
        year_5 = current_earnings * ((1 + growth_rate + div_bonus) ** 5)
        
        return {
            "current_annual": current_earnings,
            "projected_year_5": round(year_5, 0),
            "cagr": round((growth_rate + div_bonus) * 100, 1),
            "diversification_premium": round(div_bonus * 100, 1),
            "recommendation": "diversify" if diversification_score < 0.5 else "maintain"
        }
    
    def revenue_streams_analysis(self, streams: Dict[str, float]) -> Dict:
        """Analyze multiple revenue streams"""
        total = sum(streams.values())
        
        # Calculate concentration
        max_share = max(streams.values()) / total if total > 0 else 0
        
        # Diversification score (Herfindahl index inverse)
        shares = [v/total for v in streams.values()]
        hhi = sum(s**2 for s in shares)
        diversification = 1 - hhi
        
        return {
            "total_annual_revenue": total,
            "stream_breakdown": {k: round(v/total*100, 1) for k, v in streams.items()},
            "concentration_risk": "high" if max_share > 0.6 else "medium" if max_share > 0.4 else "low",
            "diversification_score": round(diversification, 2),
            "stream_count": len(streams)
        }
