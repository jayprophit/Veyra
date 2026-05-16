"""
Earnings Calendar Models
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

class ReportTime(Enum):
    PRE_MARKET = "pre-market"
    POST_MARKET = "post-market"
    DURING = "during"

@dataclass
class EarningsEvent:
    ticker: str
    company_name: str
    report_date: date
    report_time: ReportTime
    eps_estimate: Optional[float] = None
    revenue_estimate: Optional[float] = None
    eps_actual: Optional[float] = None
    revenue_actual: Optional[float] = None
    surprise_percent: Optional[float] = None
    whisper_number: Optional[float] = None
    is_confirmed: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    @property
    def surprise_direction(self) -> str:
        if self.surprise_percent is None:
            return "unknown"
        return "beat" if self.surprise_percent > 0 else "miss"
    
    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "report_date": self.report_date.isoformat(),
            "report_time": self.report_time.value,
            "eps_estimate": self.eps_estimate,
            "revenue_estimate": self.revenue_estimate,
            "eps_actual": self.eps_actual,
            "revenue_actual": self.revenue_actual,
            "surprise_percent": self.surprise_percent,
            "surprise_direction": self.surprise_direction,
            "whisper_number": self.whisper_number,
            "is_confirmed": self.is_confirmed,
        }
