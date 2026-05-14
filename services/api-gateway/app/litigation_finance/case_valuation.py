"""Case Valuation"""
from typing import Dict

class CaseValuation:
    """Value legal cases"""
    
    def expected_value(self, damages: float, win_prob: float, 
                     duration_years: int) -> Dict:
        """Calculate expected case value"""
        expected = damages * win_prob
        # Discount for duration
        discount = 0.08
        pv = expected / ((1 + discount) ** duration_years)
        
        return {
            "expected_damages": expected,
            "present_value": pv,
            "win_probability": win_prob,
            "duration": duration_years
        }
    
    def portfolio_analysis(self, cases: list) -> Dict:
        """Analyze portfolio of cases"""
        total_ev = sum(c["expected"] for c in cases)
        diversification = len(cases) * 0.05
        
        return {
            "total_expected_value": total_ev,
            "case_count": len(cases),
            "diversification_benefit": min(diversification, 0.3)
        }
