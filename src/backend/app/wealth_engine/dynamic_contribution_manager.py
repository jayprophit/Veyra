"""Dynamic Contribution Manager - Handles changing contribution schedules"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class ContributionFrequency(Enum):
    WEEKLY = 'weekly'
    BIWEEKLY = 'biweekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    LUMP_SUM = 'lump_sum'
    VARIABLE = 'variable'

@dataclass
class ContributionSchedule:
    base_amount: float
    frequency: ContributionFrequency
    escalation_rate: float = 0.0  # % increase per period
    max_amount: Optional[float] = None
    min_amount: float = 0
    start_date: datetime = None
    
    def __post_init__(self):
        if self.start_date is None:
            self.start_date = datetime.now()

class DynamicContributionManager:
    """
    Manages changing contribution amounts over time.
    Escalates contributions as income grows.
    """
    
    def __init__(self):
        self.schedules = {}
        self.contribution_history = []
        self.income_tracker = {}
    
    def create_schedule(self, user_id: str, base: float, freq: ContributionFrequency,
                       escalate: float = 0.0, max_amt: Optional[float] = None) -> ContributionSchedule:
        """Create escalating contribution schedule"""
        schedule = ContributionSchedule(
            base_amount=base,
            frequency=freq,
            escalation_rate=escalate,
            max_amount=max_amt
        )
        self.schedules[user_id] = schedule
        return schedule
    
    def get_next_contribution(self, user_id: str) -> Dict:
        """Calculate next contribution amount with escalation"""
        schedule = self.schedules.get(user_id)
        if not schedule:
            return {'amount': 0, 'date': None}
        
        # Calculate escalation
        periods_elapsed = self._get_periods_elapsed(schedule)
        escalated_amount = schedule.base_amount * ((1 + schedule.escalation_rate) ** periods_elapsed)
        
        # Apply caps
        if schedule.max_amount:
            escalated_amount = min(escalated_amount, schedule.max_amount)
        escalated_amount = max(escalated_amount, schedule.min_amount)
        
        # Next date
        next_date = self._get_next_date(schedule, periods_elapsed)
        
        return {
            'amount': round(escalated_amount, 2),
            'date': next_date,
            'periods_elapsed': periods_elapsed,
            'original_base': schedule.base_amount,
            'escalation_applied': periods_elapsed > 0
        }
    
    def record_contribution(self, user_id: str, amount: float, source: str = 'regular'):
        """Record actual contribution"""
        self.contribution_history.append({
            'user_id': user_id,
            'amount': amount,
            'source': source,
            'timestamp': datetime.now()
        })
    
    def adjust_for_income_change(self, user_id: str, old_income: float, new_income: float,
                                  strategy: str = 'proportional') -> Dict:
        """Adjust contributions when income changes"""
        schedule = self.schedules.get(user_id)
        if not schedule:
            return {'error': 'No schedule found'}
        
        income_change_pct = (new_income - old_income) / old_income if old_income > 0 else 0
        
        if strategy == 'proportional':
            # Keep contribution as % of income
            new_base = schedule.base_amount * (1 + income_change_pct)
        elif strategy == 'aggressive':
            # Increase more if income went up
            new_base = schedule.base_amount * (1 + income_change_pct * 1.2)
        elif strategy == 'conservative':
            # Keep same amount, pocket raise
            new_base = schedule.base_amount
        else:  # minimum
            new_base = min(schedule.base_amount, new_income * 0.1)  # Cap at 10%
        
        old_base = schedule.base_amount
        schedule.base_amount = round(new_base, 2)
        
        return {
            'old_amount': old_base,
            'new_amount': schedule.base_amount,
            'income_change': f"{income_change_pct*100:+.0f}%",
            'strategy': strategy
        }
    
    def get_yearly_projection(self, user_id: str, years: int = 1) -> Dict:
        """Project contributions over time"""
        schedule = self.schedules.get(user_id)
        if not schedule:
            return {'error': 'No schedule found'}
        
        projections = []
        total = 0
        
        periods_per_year = {
            ContributionFrequency.WEEKLY: 52,
            ContributionFrequency.BIWEEKLY: 26,
            ContributionFrequency.MONTHLY: 12,
            ContributionFrequency.QUARTERLY: 4
        }.get(schedule.frequency, 12)
        
        for period in range(years * periods_per_year):
            amount = schedule.base_amount * ((1 + schedule.escalation_rate) ** period)
            if schedule.max_amount:
                amount = min(amount, schedule.max_amount)
            
            projections.append({
                'period': period + 1,
                'amount': round(amount, 2)
            })
            total += amount
        
        return {
            'frequency': schedule.frequency.value,
            'periods': len(projections),
            'total_projected': round(total, 2),
            'avg_per_period': round(total / len(projections), 2) if projections else 0,
            'yearly_totals': self._calculate_yearly_totals(projections, periods_per_year)
        }
    
    def _get_periods_elapsed(self, schedule: ContributionSchedule) -> int:
        """Calculate how many periods have passed"""
        elapsed = datetime.now() - schedule.start_date
        
        days_per_period = {
            ContributionFrequency.WEEKLY: 7,
            ContributionFrequency.BIWEEKLY: 14,
            ContributionFrequency.MONTHLY: 30,
            ContributionFrequency.QUARTERLY: 90
        }.get(schedule.frequency, 30)
        
        return max(0, elapsed.days // days_per_period)
    
    def _get_next_date(self, schedule: ContributionSchedule, periods: int) -> datetime:
        """Calculate next contribution date"""
        days_per_period = {
            ContributionFrequency.WEEKLY: 7,
            ContributionFrequency.BIWEEKLY: 14,
            ContributionFrequency.MONTHLY: 30,
            ContributionFrequency.QUARTERLY: 90
        }.get(schedule.frequency, 30)
        
        return schedule.start_date + timedelta(days=days_per_period * (periods + 1))
    
    def _calculate_yearly_totals(self, projections: List[Dict], periods_per_year: int) -> List[float]:
        """Sum projections by year"""
        yearly = []
        for year in range(0, len(projections), periods_per_year):
            year_total = sum(p['amount'] for p in projections[year:year+periods_per_year])
            yearly.append(round(year_total, 2))
        return yearly

# Example usage
if __name__ == "__main__":
    mgr = DynamicContributionManager()
    
    # Start at £20/week, escalate 10% per quarter, max £100/week
    mgr.create_schedule('user_001', 20, ContributionFrequency.WEEKLY, 0.10, 100)
    
    # Get projection
    proj = mgr.get_yearly_projection('user_001', years=2)
    print(f"2-year projection: £{proj['total_projected']:,.2f}")
    print(f"Yearly totals: {proj['yearly_totals']}")
    
    # Simulate income increase
    result = mgr.adjust_for_income_change('user_001', 1000, 1500, 'proportional')
    print(f"\nIncome increased 50%")
    print(f"Contribution: £{result['old_amount']} → £{result['new_amount']}")
