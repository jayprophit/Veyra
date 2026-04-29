"""Patent Valuation - IP and patent portfolio analysis"""
from typing import Dict, List

class PatentValuation:
    """Value patent portfolios and intellectual property"""
    
    def patent_dcf(self, annual_revenue: float,
                   growth_rate: float,
                   patent_life: int,
                   discount_rate: float = 0.15) -> Dict:
        """DCF valuation for patent-protected revenue"""
        # Calculate NPV of patent-protected cash flows
        npv = 0
        for year in range(1, patent_life + 1):
            revenue = annual_revenue * ((1 + growth_rate) ** year)
            cash_flow = revenue * 0.3  # 30% margin assumption
            npv += cash_flow / ((1 + discount_rate) ** year)
        
        return {
            "annual_revenue": annual_revenue,
            "patent_life_years": patent_life,
            "npv": round(npv, 0),
            "royalty_rate": "5-10% typical",
            "value_per_patent": round(npv / 10, 0)  # Assume 10 patents
        }
    
    def patent_quality_score(self, citations: int,
                            claims: int,
                            family_size: int,
                            litigation_history: bool) -> Dict:
        """Score patent quality for investment decisions"""
        score = 0
        score += min(citations * 2, 40)  # Citations indicate importance
        score += min(claims, 20)  # More claims = broader protection
        score += family_size * 5  # International coverage
        score -= 15 if litigation_history else 0  # Litigation risk
        
        return {
            "quality_score": score,
            "grade": "A" if score > 80 else "B" if score > 60 else "C" if score > 40 else "D",
            "investment_quality": "strong" if score > 70 else "moderate" if score > 50 else "weak",
            "factors": {
                "citation_impact": citations,
                "claim_breadth": claims,
                "geographic_coverage": family_size,
                "litigation_risk": litigation_history
            }
        }
    
    def portfolio_valuation(self, patents: List[Dict],
                         market_segment: str) -> Dict:
        """Value entire patent portfolio"""
        total_value = 0
        high_value = 0
        
        for patent in patents:
            quality = self.patent_quality_score(
                patent.get("citations", 0),
                patent.get("claims", 0),
                patent.get("family_size", 0),
                patent.get("litigation", False)
            )
            value = quality["quality_score"] * 10000  # $10K per point
            total_value += value
            if quality["grade"] == "A":
                high_value += value
        
        # Market segment premium
        premiums = {"software": 1.2, "biotech": 1.5, "hardware": 1.0, "pharma": 1.8}
        premium = premiums.get(market_segment, 1.0)
        
        return {
            "patent_count": len(patents),
            "total_value": round(total_value * premium, 0),
            "tier_a_value": round(high_value * premium, 0),
            "avg_value_per_patent": round(total_value * premium / len(patents), 0) if patents else 0,
            "market_segment": market_segment
        }
