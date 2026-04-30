"""Robot Leasing Economics"""
from typing import Dict

class RobotLeasing:
    """Lease vs buy analysis for industrial robots"""
    
    def lease_terms(self, robot_value: float = 100000) -> Dict:
        lease_rate_factor = 0.03  # 3% per month
        lease_term_months = 36
        
        monthly_payment = robot_value * lease_rate_factor
        total_lease_cost = monthly_payment * lease_term_months
        
        return {
            "monthly_payment": monthly_payment,
            "total_lease_cost": total_lease_cost,
            "buyout_option": robot_value * 0.10,
            "vs_purchase_premium_pct": round((total_lease_cost - robot_value) / robot_value * 100, 1)
        }
    
    def comparison_analysis(self) -> Dict:
        return {
            "lease_advantages": ["Conserves cash", "Tax deductible", "Easy upgrades", "Maintenance included"],
            "buy_advantages": ["Lower total cost", "Asset ownership", "Depreciation benefits", "Unlimited use"],
            "breakeven_months": 48,
            "recommendation": "Lease if rapid obsolescence expected"
        }
