"""Veterinary Valuation - Vet clinic and hospital analytics"""
from typing import Dict

class VeterinaryValuation:
    """Value veterinary practices"""
    
    def practice_dcf(self, annual_revenue: float,
                    ebitda_margin: float,
                    growth_rate: float,
                    discount_rate: float = 0.10) -> Dict:
        """DCF valuation for veterinary practice"""
        ebitda = annual_revenue * (ebitda_margin / 100)
        
        # Project 10 years
        cash_flows = []
        for year in range(1, 11):
            revenue = annual_revenue * ((1 + growth_rate) ** year)
            cf = revenue * (ebitda_margin / 100)
            cash_flows.append(cf)
        
        # Terminal value
        terminal_value = cash_flows[-1] * 8  # 8x EBITDA multiple
        
        # NPV
        npv = sum(cf / ((1 + discount_rate) ** (i+1)) for i, cf in enumerate(cash_flows))
        npv += terminal_value / ((1 + discount_rate) ** 10)
        
        return {
            "annual_revenue": annual_revenue,
            "ebitda_margin": ebitda_margin,
            "enterprise_value": round(npv, 0),
            "revenue_multiple": round(npv / annual_revenue, 1),
            "ebitda_multiple": round(npv / ebitda, 1) if ebitda > 0 else 0
        }
    
    def client_lifetime_value(self, annual_spend: float,
                             years_as_client: float,
                             acquisition_cost: float) -> Dict:
        """Calculate veterinary client LTV"""
        ltv = annual_spend * years_as_client
        net_ltv = ltv - acquisition_cost
        
        return {
            "annual_spend": annual_spend,
            "years_as_client": years_as_client,
            "lifetime_value": round(ltv, 0),
            "acquisition_cost": acquisition_cost,
            "net_ltv": round(net_ltv, 0),
            "ltv_cac_ratio": round(ltv / acquisition_cost, 1) if acquisition_cost > 0 else 0
        }
