"""Dividend Engine - Automated dividend income tracking"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class DividendHolding:
    ticker: str
    shares: float
    annual_dividend_per_share: float
    dividend_frequency: int  # 1=annual, 2=semi, 4=quarterly, 12=monthly
    payout_dates: List[date]

class DividendEngine:
    def __init__(self):
        self.holdings: List[DividendHolding] = []
    
    def add(self, h: DividendHolding):
        self.holdings.append(h)
    
    def calculate_annual_income(self, h: DividendHolding) -> float:
        return h.shares * h.annual_dividend_per_share
    
    def get_summary(self) -> Dict:
        if not self.holdings:
            return {'status': 'NO_HOLDINGS'}
        
        total_annual = sum(self.calculate_annual_income(h) for h in self.holdings)
        monthly_avg = total_annual / 12
        
        return {
            'holdings': len(self.holdings),
            'total_shares': round(sum(h.shares for h in self.holdings), 2),
            'annual_dividend_income': round(total_annual, 2),
            'monthly_average': round(monthly_avg, 2),
            'yielding_positions': len(self.holdings)
        }
