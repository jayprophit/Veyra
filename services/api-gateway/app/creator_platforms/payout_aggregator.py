"""Payout Aggregator - Multi-platform revenue tracking"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PayoutRecord:
    platform: str
    amount: float
    currency: str
    date: datetime
    status: str
    fees: float

class PayoutAggregator:
    """Aggregate payouts across all creator platforms"""
    
    def __init__(self):
        self.records: List[PayoutRecord] = []
        self.platforms: List[str] = []
    
    def add_payout(self, record: PayoutRecord):
        self.records.append(record)
        if record.platform not in self.platforms:
            self.platforms.append(record.platform)
    
    def total_earnings(self, platform: str = None) -> float:
        records = self.records if not platform else [r for r in self.records if r.platform == platform]
        return sum(r.amount for r in records)
    
    def earnings_by_platform(self) -> Dict[str, float]:
        result = {}
        for r in self.records:
            result[r.platform] = result.get(r.platform, 0) + r.amount
        return result
    
    def monthly_summary(self, year: int, month: int) -> Dict:
        month_records = [r for r in self.records 
                        if r.date.year == year and r.date.month == month]
        return {
            "total": sum(r.amount for r in month_records),
            "by_platform": {p: sum(r.amount for r in month_records if r.platform == p) 
                          for p in set(r.platform for r in month_records)},
            "total_fees": sum(r.fees for r in month_records)
        }
    
    def get_pending_payouts(self) -> List[PayoutRecord]:
        return [r for r in self.records if r.status == "pending"]
