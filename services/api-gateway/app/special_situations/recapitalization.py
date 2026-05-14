"""Recapitalization"""
from typing import Dict

class Recapitalization:
    def lbo_recap(self, ev: float, debt: float, target_ratio: float, ebitda: float) -> Dict:
        target_debt = ebitda * target_ratio
        dividend = target_debt - debt
        return {
            "post_debt": target_debt,
            "special_dividend": dividend,
            "post_equity": ev - target_debt
        }
    
    def debt_equity_swap(self, debt_face: float, recovery: float) -> Dict:
        return {"equity_issued": debt_face * recovery, "debt_reduction": debt_face}
