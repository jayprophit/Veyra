"""Aerospace Suppliers - Supply chain and tier analysis"""
from typing import Dict

class AerospaceSuppliers:
    """Analyze aerospace supplier economics"""
    
    def tier_analysis(self, tier_level: int,  # 1=direct to OEM, 2=sub, 3=component
                     revenue_concentration: float,
                     program_exposure: Dict[str, float]) -> Dict:
        """Analyze supplier tier positioning"""
        tier_multipliers = {1: 1.5, 2: 1.0, 3: 0.6}
        margin_potential = tier_multipliers.get(tier_level, 0.5)
        
        # Concentration risk
        risk_score = revenue_concentration * 100
        
        # Program diversity
        program_count = len(program_exposure)
        diversity_bonus = min(program_count * 5, 20)
        
        return {
            "tier_level": tier_level,
            "margin_potential": margin_potential,
            "concentration_risk": round(risk_score, 1),
            "program_diversity": program_count,
            "diversity_bonus": diversity_bonus,
            "composite_score": round(margin_potential * 10 + diversity_bonus - risk_score * 0.1, 1)
        }
    
    def aftermarket_value(self, original_contract: float,
                         spares_lifetime: float,
                         margin_pct: float) -> Dict:
        """Calculate aftermarket revenue potential"""
        aftermarket_multiple = spares_lifetime * 0.3  # 30% of OEM annually
        total_aftermarket = original_contract * aftermarket_multiple
        profit = total_aftermarket * (margin_pct / 100)
        
        return {
            "oem_contract": original_contract,
            "aftermarket_multiple": round(aftermarket_multiple, 1),
            "total_aftermarket": round(total_aftermarket, 0),
            "lifetime_profit": round(profit, 0),
            "aftermarket_strategic": aftermarket_multiple > 2
        }
