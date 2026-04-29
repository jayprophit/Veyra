"""Regulatory Arbitrage - Cannabis state/federal arbitrage"""
from typing import Dict

class RegulatoryArbitrage:
    """Analyze cannabis regulatory arbitrage"""
    
    def state_premium(self, state_tax_rate: float,
                     neighbor_tax_rate: float,
                     cross_border_demand: float,
                     enforcement_risk: float) -> Dict:
        """Calculate cross-border arbitrage potential"""
        tax_differential = neighbor_tax_rate - state_tax_rate
        arbitrage_value = cross_border_demand * tax_differential / 100
        
        # Risk adjustment
        risk_adjusted_value = arbitrage_value * (1 - enforcement_risk)
        
        return {
            "tax_differential_pct": round(tax_differential, 1),
            "gross_arbitrage": round(arbitrage_value, 0),
            "risk_adjusted_value": round(risk_adjusted_value, 0),
            "viable": risk_adjusted_value > 0 and tax_differential > 5
        }
    
    def federal_legalization_npv(self, current_state_revenue: float,
                                federal_rate_estimate: float,
                                interstate_enabled: bool) -> Dict:
        """Value impact of federal legalization"""
        federal_tax_impact = current_state_revenue * (federal_rate_estimate / 100)
        
        # Interstate commerce benefit
        interstate_benefit = current_state_revenue * 0.3 if interstate_enabled else 0
        
        net_impact = interstate_benefit - federal_tax_impact
        
        return {
            "current_revenue": current_state_revenue,
            "federal_tax_cost": round(federal_tax_impact, 0),
            "interstate_benefit": round(interstate_benefit, 0),
            "net_annual_impact": round(net_impact, 0),
            "legalization_positive": net_impact > 0
        }
