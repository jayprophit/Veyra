"""CRISPR Valuation - Gene editing investment analysis"""
from typing import Dict

class CRISPRValuation:
    """Value CRISPR and gene editing companies"""
    
    def platform_valuation(self, patent_count: int,
                          licensing_revenue: float,
                          pipeline_candidates: int,
                          stage: str) -> Dict:
        """Value gene editing platform"""
        patent_value = patent_count * 5e6  # $5M per patent
        stage_mult = {"discovery": 0.5, "preclinical": 1, "phase1": 2, "phase2": 4, "phase3": 8}
        pipeline_value = pipeline_candidates * stage_mult.get(stage, 1) * 50e6
        
        total_value = patent_value + licensing_revenue * 5 + pipeline_value
        
        return {
            "patent_value": round(patent_value, 0),
            "licensing_value": round(licensing_revenue * 5, 0),
            "pipeline_value": round(pipeline_value, 0),
            "total_platform_value": round(total_value, 0),
            "per_program_value": round(pipeline_value / max(pipeline_candidates, 1), 0)
        }
    
    def therapy_npv(self, addressable_patients: int,
                   therapy_price: float,
                   development_cost: float,
                   probability_success: float,
                   time_to_market: int) -> Dict:
        """Risk-adjusted NPV for gene therapy"""
        peak_sales = addressable_patients * therapy_price
        risk_adjusted_peak = peak_sales * probability_success
        
        # NPV over 10 years post-launch
        npv = -development_cost
        for year in range(1, 11):
            market_penetration = min(0.3, year * 0.03)
            year_revenue = risk_adjusted_peak * market_penetration
            npv += year_revenue / ((1.1) ** (year + time_to_market))
        
        return {
            "peak_sales_potential": peak_sales,
            "risk_adjusted_npv": round(npv, 0),
            "probability_of_success": probability_success,
            "roi_multiple": round(npv / development_cost, 1) if development_cost > 0 else 0,
            "investment_grade": "A" if npv > development_cost * 3 else "B" if npv > 0 else "C"
        }
