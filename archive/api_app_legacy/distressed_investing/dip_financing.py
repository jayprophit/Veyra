"""DIP Financing - Debtor-in-possession financing"""
from typing import Dict

class DIPFinancing:
    """Analyze DIP financing structures"""
    
    def structure_dip(self, financing_need: float, collateral_value: float,
                       exit_timeline_months: int) -> Dict:
        """Structure DIP financing"""
        # DIP typically 70-80% of collateral
        max_dip = collateral_value * 0.75
        
        # Roll-up of pre-petition debt (common)
        roll_up_pct = 0.20
        roll_up_amount = financing_need * roll_up_pct
        
        # Interest rate (premium for risk)
        base_rate = 0.08
        dip_premium = 0.04
        
        return {
            "max_dip_available": max_dip,
            "requested": financing_need,
            "feasible": financing_need <= max_dip,
            "roll_up": roll_up_amount,
            "new_money": financing_need - roll_up_amount,
            "interest_rate": base_rate + dip_premium,
            "superpriority": True,
            "exit_timeline_months": exit_timeline_months
        }
    
    def exit_financing(self, post_reorg_ebitda: float, target_leverage: float) -> Dict:
        """Plan exit financing"""
        total_debt_capacity = post_reorg_ebitda * target_leverage
        
        return {
            "debt_capacity": total_debt_capacity,
            "recommended_structure": {
                "senior_secured": total_debt_capacity * 0.6,
                "senior_unsecured": total_debt_capacity * 0.3,
                "convertible": total_debt_capacity * 0.1
            },
            "interest_coverage": round(post_reorg_ebitda / (total_debt_capacity * 0.06), 1)
        }
