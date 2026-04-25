"""Insurance & Protection Tracker"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class Policy:
    type: str  # income_protection, life, business, home
    provider: str
    premium: float
    coverage: float
    start_date: date
    renewal_date: date
    active: bool = True

class ProtectionTracker:
    """Track all insurance policies"""
    
    def __init__(self):
        self.policies: List[Policy] = []
        self.emergency_fund_target = 6  # months
        
    def add_policy(self, policy: Policy):
        self.policies.append(policy)
    
    def get_coverage(self) -> Dict:
        """Get total coverage summary"""
        total_premium = sum(p.premium for p in self.policies if p.active)
        total_coverage = sum(p.coverage for p in self.policies if p.active)
        
        by_type = {}
        for p in self.policies:
            if p.active:
                by_type[p.type] = by_type.get(p.type, 0) + p.coverage
        
        return {
            "total_premium": total_premium,
            "total_coverage": total_coverage,
            "by_type": by_type,
            "num_policies": len([p for p in self.policies if p.active])
        }
    
    def check_gaps(self, monthly_income: float, has_mortgage: bool) -> List[str]:
        """Check missing insurance"""
        gaps = []
        types = [p.type for p in self.policies if p.active]
        
        if "income_protection" not in types:
            gaps.append("CRITICAL: Income protection missing")
        if "life" not in types and has_mortgage:
            gaps.append("Life insurance recommended (mortgage)")
        if "business" not in types:
            gaps.append("Business liability insurance")
        
        return gaps
    
    def emergency_fund_calc(self, monthly_expenses: float) -> Dict:
        """Calculate emergency fund targets"""
        return {
            "starter_target": monthly_expenses * 1,
            "3_months": monthly_expenses * 3,
            "6_months": monthly_expenses * 6,
            "12_months": monthly_expenses * 12,
            "recommended": monthly_expenses * 6
        }
