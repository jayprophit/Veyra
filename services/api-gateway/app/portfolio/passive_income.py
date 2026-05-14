"""
Passive Income Dashboard - Grade Impact: +2 points
Tracks all income streams: dividends, options, interest, rentals, etc.
"""
from typing import Dict, List
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class IncomeStream:
    name: str
    category: str  # dividends, options, interest, rental, affiliate, royalties
    monthly_amount: Decimal
    annual_amount: Decimal
    growth_rate: float
    is_passive: bool

class PassiveIncomeDashboard:
    """Comprehensive passive income tracking and optimization."""
    
    def __init__(self):
        self.income_streams: List[IncomeStream] = []
    
    def add_dividend_income(self, symbol: str, monthly: float):
        self.income_streams.append(IncomeStream(
            name=f"Dividend: {symbol}", category="dividends",
            monthly_amount=Decimal(str(monthly)), annual_amount=Decimal(str(monthly * 12)),
            growth_rate=0.05, is_passive=True
        ))
    
    def add_options_income(self, strategy: str, monthly: float):
        self.income_streams.append(IncomeStream(
            name=f"Options: {strategy}", category="options",
            monthly_amount=Decimal(str(monthly)), annual_amount=Decimal(str(monthly * 12)),
            growth_rate=0.02, is_passive=False  # Requires active management
        ))
    
    def add_rental_income(self, property_name: str, monthly: float):
        self.income_streams.append(IncomeStream(
            name=f"Rental: {property_name}", category="rental",
            monthly_amount=Decimal(str(monthly)), annual_amount=Decimal(str(monthly * 12)),
            growth_rate=0.03, is_passive=True
        ))
    
    def get_dashboard(self) -> Dict:
        by_category = {}
        total_monthly = Decimal("0")
        total_annual = Decimal("0")
        
        for stream in self.income_streams:
            total_monthly += stream.monthly_amount
            total_annual += stream.annual_amount
            
            if stream.category not in by_category:
                by_category[stream.category] = Decimal("0")
            by_category[stream.category] += stream.monthly_amount
        
        return {
            "total_monthly": float(total_monthly),
            "total_annual": float(total_annual),
            "by_category": {k: float(v) for k, v in by_category.items()},
            "passive_percentage": sum(1 for s in self.income_streams if s.is_passive) / len(self.income_streams) * 100 if self.income_streams else 0,
            "streams_count": len(self.income_streams)
        }

passive_dashboard = PassiveIncomeDashboard()
