"""
Economic Calendar Tracker
=========================
Track and analyze economic events, earnings, IPOs
Market impact prediction, volatility forecasting
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import calendar


class EventImpact(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EventType(Enum):
    ECONOMIC = "economic"
    EARNINGS = "earnings"
    IPO = "ipo"
    DIVIDEND = "dividend"
    FED = "fed"
    OPEX = "opex"


@dataclass
class EconomicEvent:
    """Economic event data"""
    date: datetime
    time: str
    event_type: str
    name: str
    country: str
    impact: str
    forecast: Optional[str] = None
    previous: Optional[str] = None
    actual: Optional[str] = None


@dataclass
class EarningsEvent:
    """Earnings event data"""
    ticker: str
    company: str
    date: datetime
    time: str  # BMO = Before Market Open, AMC = After Market Close
    eps_estimate: float
    revenue_estimate: float
    eps_actual: Optional[float] = None
    revenue_actual: Optional[float] = None
    surprise_pct: Optional[float] = None


class EconomicCalendar:
    """
    Track and analyze economic events
    
    Features:
    - Economic data releases (NFP, CPI, GDP, etc.)
    - Earnings calendar
    - IPO schedule
    - Fed meetings
    - Options expiration
    """
    
    def __init__(self):
        self.economic_events: List[EconomicEvent] = []
        self.earnings_events: List[EarningsEvent] = []
        self.ipos: List[Dict] = []
    
    def add_economic_event(self, event: EconomicEvent):
        """Add economic event"""
        self.economic_events.append(event)
    
    def add_earnings(self, earnings: EarningsEvent):
        """Add earnings event"""
        self.earnings_events.append(earnings)
    
    def get_upcoming_events(self, days: int = 7) -> Dict[str, List]:
        """Get events for next N days"""
        cutoff = datetime.now() + timedelta(days=days)
        
        upcoming_economic = [
            e for e in self.economic_events
            if e.date > datetime.now() and e.date <= cutoff
        ]
        
        upcoming_earnings = [
            e for e in self.earnings_events
            if e.date > datetime.now() and e.date <= cutoff
        ]
        
        return {
            'economic': upcoming_economic,
            'earnings': upcoming_earnings,
            'count': len(upcoming_economic) + len(upcoming_earnings)
        }
    
    def get_high_impact_events(self, days: int = 30) -> List[EconomicEvent]:
        """Get high impact events"""
        cutoff = datetime.now() + timedelta(days=days)
        
        high_impact = [
            e for e in self.economic_events
            if e.impact == EventImpact.HIGH.value
            and e.date > datetime.now()
            and e.date <= cutoff
        ]
        
        return sorted(high_impact, key=lambda x: x.date)
    
    def get_earnings_by_date(self, date: datetime) -> List[EarningsEvent]:
        """Get all earnings for specific date"""
        return [
            e for e in self.earnings_events
            if e.date.date() == date.date()
        ]
    
    def get_opex_dates(self, year: int = None) -> List[datetime]:
        """Get monthly options expiration dates (3rd Friday)"""
        if year is None:
            year = datetime.now().year
        
        opex_dates = []
        
        for month in range(1, 13):
            # Get the 3rd Friday
            cal = calendar.monthcalendar(year, month)
            fridays = [week[calendar.FRIDAY] for week in cal if week[calendar.FRIDAY] != 0]
            
            if len(fridays) >= 3:
                opex_dates.append(datetime(year, month, fridays[2]))
        
        # Also include quarterly (Mar, Jun, Sep, Dec) - these are major OPEX
        return opex_dates
    
    def get_quarterly_opex(self, year: int = None) -> List[datetime]:
        """Get quarterly options expiration (major)"""
        opex = self.get_opex_dates(year)
        
        # Filter for March, June, September, December
        quarterly = [
            d for d in opex
            if d.month in [3, 6, 9, 12]
        ]
        
        return quarterly
    
    def estimate_volatility(self, days_ahead: int = 5) -> Dict:
        """Estimate expected volatility from calendar"""
        upcoming = self.get_upcoming_events(days_ahead)
        
        high_count = len([
            e for e in upcoming['economic']
            if e.impact == EventImpact.HIGH.value
        ])
        
        earnings_count = len(upcoming['earnings'])
        
        # Simple volatility scoring
        vol_score = high_count * 2 + earnings_count * 0.5
        
        if vol_score >= 5:
            vol_forecast = 'HIGH'
            vix_estimate = '>25'
        elif vol_score >= 3:
            vol_forecast = 'ELEVATED'
            vix_estimate = '20-25'
        elif vol_score >= 1:
            vol_forecast = 'NORMAL'
            vix_estimate = '15-20'
        else:
            vol_forecast = 'LOW'
            vix_estimate = '<15'
        
        return {
            'volatility_forecast': vol_forecast,
            'estimated_vix_range': vix_estimate,
            'high_impact_events': high_count,
            'earnings_count': earnings_count,
            'score': vol_score,
            'trading_recommendation': 'Reduce size' if vol_score >= 5 else 'Normal' if vol_score < 3 else 'Caution'
        }
    
    def get_earnings_season_schedule(self) -> Dict:
        """Get earnings season dates"""
        now = datetime.now()
        
        # Determine current quarter
        quarter = (now.month - 1) // 3 + 1
        
        # Earnings season typically starts 2-3 weeks after quarter end
        season_starts = {
            1: datetime(now.year, 4, 15),   # Q1 earnings in April
            2: datetime(now.year, 7, 15),   # Q2 earnings in July
            3: datetime(now.year, 10, 15),  # Q3 earnings in October
            4: datetime(now.year + 1, 1, 15)  # Q4 earnings in January
        }
        
        season_start = season_starts[quarter]
        season_end = season_start + timedelta(days=45)
        
        return {
            'current_quarter': f'Q{quarter}',
            'season_start': season_start.strftime('%Y-%m-%d'),
            'season_end': season_end.strftime('%Y-%m-%d'),
            'status': 'IN_PROGRESS' if now >= season_start and now <= season_end else 'UPCOMING' if now < season_start else 'COMPLETED',
            'peak_weeks': [
                (season_start + timedelta(days=7)).strftime('%Y-%m-%d'),
                (season_start + timedelta(days=14)).strftime('%Y-%m-%d')
            ]
        }
    
    def get_fed_meeting_schedule(self, year: int = None) -> List[Dict]:
        """Get Federal Reserve meeting schedule"""
        if year is None:
            year = datetime.now().year
        
        # Fed typically meets 8 times per year
        # Schedule varies but usually follows pattern
        typical_dates = [
            datetime(year, 1, 28),   # Jan/Feb
            datetime(year, 3, 18),   # Mar
            datetime(year, 4, 29),   # Apr/May
            datetime(year, 6, 10),   # Jun
            datetime(year, 7, 29),  # Jul
            datetime(year, 9, 16),   # Sep
            datetime(year, 11, 5),   # Nov
            datetime(year, 12, 16)   # Dec
        ]
        
        meetings = []
        for date in typical_dates:
            has_press_conf = date.month in [3, 6, 9, 12]  # Quarterly
            
            meetings.append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'FOMC',
                'has_press_conference': has_press_conf,
                'importance': 'HIGH' if has_press_conf else 'MEDIUM',
                'rate_decision_expected': True
            })
        
        return meetings
    
    def get_calendar_summary(self) -> Dict:
        """Get comprehensive calendar summary"""
        return {
            'today': datetime.now().strftime('%Y-%m-%d'),
            'this_week_events': self.get_upcoming_events(7),
            'high_impact_upcoming': len(self.get_high_impact_events(30)),
            'earnings_season': self.get_earnings_season_schedule(),
            'volatility_forecast': self.estimate_volatility(),
            'opex_this_month': self.get_opex_dates()[-1].strftime('%Y-%m-%d') if self.get_opex_dates() else None,
            'next_fed_meeting': self.get_fed_meeting_schedule()[0] if self.get_fed_meeting_schedule() else None,
            'timestamp': datetime.now().isoformat()
        }


# Usage
def get_economic_summary() -> Dict:
    """Quick economic calendar summary"""
    calendar = EconomicCalendar()
    return calendar.get_calendar_summary()


def get_next_opex() -> str:
    """Get next options expiration date"""
    calendar = EconomicCalendar()
    dates = calendar.get_opex_dates()
    
    now = datetime.now()
    
    for date in dates:
        if date > now:
            return date.strftime('%Y-%m-%d')
    
    return 'Unknown'


def check_earnings_week(tickers: List[str]) -> Dict[str, bool]:
    """Check which tickers have earnings this week"""
    calendar = EconomicCalendar()
    week_events = calendar.get_upcoming_events(7)
    
    earnings_tickers = {e.ticker for e in week_events['earnings']}
    
    return {
        ticker: ticker in earnings_tickers
        for ticker in tickers
    }
