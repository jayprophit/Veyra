"""P2P Lending Tracker - Zopa, Ratesetter, Funding Circle"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class P2PLoan:
    platform: str
    borrower_rating: str
    amount: Decimal
    interest_rate: Decimal
    term_months: int
    start_date: date
    repaid: Decimal = Decimal("0")
    status: str = "active"

class P2PTracker:
    """Track P2P lending across platforms"""
    
    PLATFORMS = {
        "zopa": {"rates": "4-6%", "min": 1000},
        "ratesetter": {"rates": "3-5%", "min": 10},
        "funding_circle": {"rates": "6-8%", "min": 100},
        "assetz_capital": {"rates": "5-7%", "min": 50}
    }
    
    def __init__(self):
        self.loans: List[P2PLoan] = []
    
    def add_loan(self, loan: P2PLoan):
        self.loans.append(loan)
    
    def get_summary(self) -> Dict:
        total_lent = sum(l.amount for l in self.loans)
        total_repaid = sum(l.repaid for l in self.loans)
        
        by_platform = {}
        for l in self.loans:
            by_platform[l.platform] = by_platform.get(l.platform, Decimal("0")) + l.amount
        
        return {
            "total_lent": float(total_lent),
            "total_repaid": float(total_repaid),
            "outstanding": float(total_lent - total_repaid),
            "num_loans": len(self.loans),
            "by_platform": {k: float(v) for k, v in by_platform.items()}
        }
