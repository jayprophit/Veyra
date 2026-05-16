"""Lawsuit Funding"""
from typing import Dict

class LawsuitFunding:
    """Structure lawsuit funding deals"""
    
    def funding_structure(self, case_ev: float, funding_needed: float,
                         multiple: float = 3.0) -> Dict:
        """Structure non-recourse funding"""
        return_amount = funding_needed * multiple
        success_return = (return_amount / funding_needed - 1) * 100 if funding_needed > 0 else 0
        
        return {
            "funding_amount": funding_needed,
            "return_if_successful": return_amount,
            "return_multiple": multiple,
            "return_pct": success_return
        }
    
    def portfolio_return(self, cases: int, avg_multiple: float,
                        win_rate: float) -> Dict:
        """Expected portfolio return"""
        expected_return = avg_multiple * win_rate
        return {"expected_multiple": expected_return, "irr_approx": (expected_return ** (1/3) - 1) * 100}
