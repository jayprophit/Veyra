"""Shariah Screening"""
from typing import Dict

class ShariahScreening:
    def equity_screening(self, debt_ratio: float, cash_ratio: float, revenue_source: str) -> Dict:
        """Screen stock for Shariah compliance"""
        debt_compliant = debt_ratio < 0.33
        cash_compliant = cash_ratio < 0.33
        
        prohibited_sources = ["alcohol", "gambling", "pork", "conventional_banking", "arms"]
        revenue_compliant = revenue_source.lower() not in prohibited_sources
        
        overall = debt_compliant and cash_compliant and revenue_compliant
        
        return {
            "compliant": overall,
            "debt_pass": debt_compliant,
            "cash_pass": cash_compliant,
            "revenue_pass": revenue_compliant,
            "purification_ratio": 0.05 if not overall else 0  # % to donate if non-compliant income
        }
    
    def business_activity_check(self, revenue_breakdown: Dict[str, float]) -> Dict:
        """Check revenue sources for compliance"""
        prohibited = ["alcohol", "gambling", "interest", "pork", "adult"]
        non_compliant_revenue = sum(v for k, v in revenue_breakdown.items() if k.lower() in prohibited)
        total = sum(revenue_breakdown.values())
        
        compliant_pct = 1 - (non_compliant_revenue / total if total > 0 else 0)
        
        return {
            "compliant_revenue_pct": round(compliant_pct * 100, 1),
            "passes": compliant_pct >= 0.95,
            "purification_amount": non_compliant_revenue * 0.10 if non_compliant_revenue > 0 else 0
        }
    
    def purification_calculation(self, dividends: float, non_compliant_pct: float) -> Dict:
        """Calculate amount to purify from dividends"""
        amount_to_purify = dividends * non_compliant_pct
        return {
            "total_dividends": dividends,
            "purification_amount": amount_to_purify,
            "purified_dividends": dividends - amount_to_purify,
            "charity_destination": "Recommended: Education or poverty alleviation"
        }
