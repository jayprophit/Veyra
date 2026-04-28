"""Country Risk Scorer - Score countries on political, economic, and social risk"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CountryMetrics:
    country_code: str
    country_name: str
    # Political
    political_stability: float  # 0-10
    government_effectiveness: float  # 0-10
    rule_of_law: float  # 0-10
    
    # Economic
    gdp_growth: float  # %
    inflation_rate: float  # %
    debt_to_gdp: float  # %
    fx_reserves_months: float  # months of imports
    
    # Social
    gini_coefficient: float  # 0-1
    unemployment_rate: float  # %
    social_stability_index: float  # 0-10

class CountryRiskScorer:
    """Score countries on comprehensive risk metrics"""
    
    def __init__(self):
        self.risk_weights = {
            "political": 0.30,
            "economic": 0.40,
            "social": 0.30
        }
    
    def calculate_risk_score(self, metrics: CountryMetrics) -> Dict:
        """Calculate comprehensive country risk score"""
        
        # Political Risk (0-100, lower = better)
        political_score = 100 - (
            metrics.political_stability * 5 +
            metrics.government_effectiveness * 3 +
            metrics.rule_of_law * 2
        )
        
        # Economic Risk
        economic_score = 50  # Base
        
        # GDP growth impact
        if metrics.gdp_growth < -2:
            economic_score += 20
        elif metrics.gdp_growth < 0:
            economic_score += 10
        elif metrics.gdp_growth > 5:
            economic_score -= 10
        
        # Inflation impact
        if metrics.inflation_rate > 20:
            economic_score += 20
        elif metrics.inflation_rate > 10:
            economic_score += 10
        elif metrics.inflation_rate > 5:
            economic_score += 5
        
        # Debt impact
        if metrics.debt_to_gdp > 100:
            economic_score += 15
        elif metrics.debt_to_gdp > 80:
            economic_score += 8
        
        # FX reserves impact
        if metrics.fx_reserves_months < 3:
            economic_score += 15
        elif metrics.fx_reserves_months < 6:
            economic_score += 5
        
        # Social Risk
        social_score = 50  # Base
        
        # Inequality impact
        if metrics.gini_coefficient > 0.45:
            social_score += 15
        elif metrics.gini_coefficient > 0.40:
            social_score += 8
        
        # Unemployment impact
        if metrics.unemployment_rate > 15:
            social_score += 15
        elif metrics.unemployment_rate > 10:
            social_score += 8
        elif metrics.unemployment_rate > 7:
            social_score += 3
        
        # Social stability
        social_score += (10 - metrics.social_stability_index) * 3
        
        # Calculate weighted composite
        composite_score = (
            political_score * self.risk_weights["political"] +
            economic_score * self.risk_weights["economic"] +
            social_score * self.risk_weights["social"]
        )
        
        # Risk classification
        if composite_score < 30:
            risk_level = "LOW"
            sovereign_rating = "A/AA"
        elif composite_score < 50:
            risk_level = "MODERATE"
            sovereign_rating = "BBB"
        elif composite_score < 70:
            risk_level = "HIGH"
            sovereign_rating = "BB/B"
        else:
            risk_level = "VERY_HIGH"
            sovereign_rating = "CCC/D"
        
        return {
            "country": metrics.country_name,
            "country_code": metrics.country_code,
            "composite_risk_score": round(composite_score, 1),
            "risk_level": risk_level,
            "implied_sovereign_rating": sovereign_rating,
            "component_scores": {
                "political": round(political_score, 1),
                "economic": round(economic_score, 1),
                "social": round(social_score, 1)
            },
            "key_risk_factors": self._identify_risk_factors(metrics),
            "investment_recommendation": self._get_recommendation(risk_level)
        }
    
    def _identify_risk_factors(self, metrics: CountryMetrics) -> List[str]:
        """Identify key risk factors for country"""
        factors = []
        
        if metrics.political_stability < 5:
            factors.append("Political instability")
        
        if metrics.debt_to_gdp > 80:
            factors.append(f"High debt burden ({metrics.debt_to_gdp:.0f}% of GDP)")
        
        if metrics.inflation_rate > 10:
            factors.append(f"High inflation ({metrics.inflation_rate:.1f}%)")
        
        if metrics.fx_reserves_months < 6:
            factors.append("Low FX reserves")
        
        if metrics.gini_coefficient > 0.40:
            factors.append("High inequality")
        
        if metrics.unemployment_rate > 10:
            factors.append(f"High unemployment ({metrics.unemployment_rate:.1f}%)")
        
        return factors
    
    def _get_recommendation(self, risk_level: str) -> str:
        """Get investment recommendation based on risk level"""
        recommendations = {
            "LOW": "SUITABLE_FOR_INVESTMENT - Normal allocations appropriate",
            "MODERATE": "CAUTION - Reduce exposure, monitor closely",
            "HIGH": "AVOID_NEW_INVESTMENT - Consider reducing existing positions",
            "VERY_HIGH": "EXIT - Liquidate positions when possible"
        }
        return recommendations.get(risk_level, "NEUTRAL")
    
    def compare_countries(self, countries: List[CountryMetrics]) -> List[Dict]:
        """Compare multiple countries"""
        results = []
        
        for country in countries:
            score = self.calculate_risk_score(country)
            results.append(score)
        
        # Sort by risk score (ascending = lower risk first)
        results.sort(key=lambda x: x["composite_risk_score"])
        
        return results
    
    def calculate_premium_spread(self, risk_score1: float, risk_score2: float) -> Dict:
        """Calculate expected sovereign spread between two countries"""
        score_diff = risk_score1 - risk_score2
        
        # Rough mapping: 10 risk points ≈ 50 bps spread
        estimated_spread_bps = abs(score_diff) * 5
        
        return {
            "score_difference": round(score_diff, 1),
            "estimated_spread_bps": round(estimated_spread_bps, 0),
            "higher_risk_country": "Country 1" if risk_score1 > risk_score2 else "Country 2",
            "spread_direction": "Risk premium for higher risk country"
        }
    
    def get_regional_summary(self, countries: List[CountryMetrics]) -> Dict:
        """Get regional risk summary"""
        scores = [self.calculate_risk_score(c) for c in countries]
        
        avg_score = sum(s["composite_risk_score"] for s in scores) / len(scores)
        
        # Count by risk level
        risk_distribution = {}
        for s in scores:
            level = s["risk_level"]
            risk_distribution[level] = risk_distribution.get(level, 0) + 1
        
        # Best and worst
        best = min(scores, key=lambda x: x["composite_risk_score"])
        worst = max(scores, key=lambda x: x["composite_risk_score"])
        
        return {
            "num_countries": len(countries),
            "average_risk_score": round(avg_score, 1),
            "risk_distribution": risk_distribution,
            "lowest_risk": {
                "country": best["country"],
                "score": best["composite_risk_score"]
            },
            "highest_risk": {
                "country": worst["country"],
                "score": worst["composite_risk_score"]
            },
            "regional_rating": "STABLE" if avg_score < 40 else "CAUTION" if avg_score < 60 else "RISKY"
        }
