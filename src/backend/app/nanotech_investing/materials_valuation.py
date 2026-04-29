"""Materials Valuation - Nanomaterials and applications"""
from typing import Dict

class MaterialsValuation:
    """Value nanotechnology materials and applications"""
    
    def graphene_applications(self, target_market: str,
                           performance_improvement: float,
                           cost_premium: float,
                           market_size_billions: float) -> Dict:
        """Value graphene applications by market"""
        # Adoption curve based on cost-benefit
        cost_benefit = performance_improvement / cost_premium if cost_premium > 0 else 0
        
        if cost_benefit > 2:
            adoption_rate = 0.15  # 15% market share potential
        elif cost_benefit > 1:
            adoption_rate = 0.08
        else:
            adoption_rate = 0.02
        
        addressable_market = market_size_billions * 1e9 * adoption_rate
        value_captured = addressable_market * 0.1  # 10% margin
        
        return {
            "target_market": target_market,
            "cost_benefit_ratio": round(cost_benefit, 2),
            "adoption_rate": round(adoption_rate * 100, 1),
            "addressable_market": round(addressable_market, 0),
            "value_captured": round(value_captured, 0),
            "viability": "high" if cost_benefit > 1.5 else "medium" if cost_benefit > 1 else "low"
        }
    
    def nanomedicine_valuation(self, drug_candidates: int,
                              phase_distribution: Dict[str, int],
                              avg_peak_sales: float) -> Dict:
        """Value nanomedicine pipeline"""
        # POS by phase
        pos_rates = {"preclinical": 0.06, "phase1": 0.52, "phase2": 0.28, "phase3": 0.58}
        
        risk_adjusted_value = 0
        for phase, count in phase_distribution.items():
            pos = pos_rates.get(phase, 0.1)
            value = count * avg_peak_sales * pos * 3  # 3x multiple
            risk_adjusted_value += value
        
        return {
            "total_candidates": drug_candidates,
            "risk_adjusted_value": round(risk_adjusted_value, 0),
            "per_candidate_value": round(risk_adjusted_value / max(drug_candidates, 1), 0),
            "portfolio_grade": "A" if risk_adjusted_value > 1e9 else "B" if risk_adjusted_value > 500e6 else "C"
        }
