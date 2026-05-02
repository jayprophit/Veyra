"""
Seasonality Analyzer
====================
Analyze seasonal patterns: Month-of-year, day-of-week, holiday effects
Best/worst performing periods, cyclic patterns
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import calendar


class SeasonalityAnalyzer:
    """
    Analyze seasonal patterns in stock returns
    
    Patterns analyzed:
    - Month-of-year (January effect, etc.)
    - Day-of-week (Weekend effect)
    - Pre/post holiday returns
    - Quarterly patterns
    """
    
    def __init__(self, returns_df: pd.DataFrame = None):
        self.returns = returns_df
    
    def load_data(self, prices: pd.Series):
        """Load price data and calculate returns"""
        self.returns = prices.pct_change().dropna()
    
    def analyze_monthly_seasonality(self) -> Dict[str, Dict]:
        """Analyze returns by calendar month"""
        if self.returns is None:
            return {}
        
        self.returns.index = pd.to_datetime(self.returns.index)
        
        monthly_stats = {}
        
        for month in range(1, 13):
            month_returns = self.returns[self.returns.index.month == month]
            
            if len(month_returns) > 0:
                monthly_stats[calendar.month_name[month]] = {
                    'avg_return': round(month_returns.mean() * 100, 2),
                    'win_rate': round((month_returns > 0).mean() * 100, 1),
                    'volatility': round(month_returns.std() * 100, 2),
                    'best_return': round(month_returns.max() * 100, 2),
                    'worst_return': round(month_returns.min() * 100, 2),
                    'years_analyzed': len(month_returns)
                }
        
        return monthly_stats
    
    def analyze_day_of_week(self) -> Dict[str, Dict]:
        """Analyze returns by day of week"""
        if self.returns is None:
            return {}
        
        self.returns.index = pd.to_datetime(self.returns.index)
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        dow_stats = {}
        
        for i, day in enumerate(days):
            day_returns = self.returns[self.returns.index.dayofweek == i]
            
            if len(day_returns) > 0:
                dow_stats[day] = {
                    'avg_return': round(day_returns.mean() * 100, 3),
                    'win_rate': round((day_returns > 0).mean() * 100, 1),
                    'sharpe': round(day_returns.mean() / day_returns.std(), 2) if day_returns.std() > 0 else 0
                }
        
        return dow_stats
    
    def analyze_quarterly_pattern(self) -> Dict[str, Dict]:
        """Analyze quarterly returns"""
        if self.returns is None:
            return {}
        
        self.returns.index = pd.to_datetime(self.returns.index)
        
        quarters = {
            'Q1': [1, 2, 3],
            'Q2': [4, 5, 6],
            'Q3': [7, 8, 9],
            'Q4': [10, 11, 12]
        }
        
        quarterly_stats = {}
        
        for q_name, months in quarters.items():
            q_returns = self.returns[self.returns.index.month.isin(months)]
            
            if len(q_returns) > 0:
                quarterly_stats[q_name] = {
                    'avg_return': round(q_returns.mean() * 100, 2),
                    'win_rate': round((q_returns > 0).mean() * 100, 1),
                    'volatility': round(q_returns.std() * 100, 2)
                }
        
        return quarterly_stats
    
    def detect_january_effect(self) -> Dict:
        """Test for January effect (higher returns in January)"""
        if self.returns is None:
            return {}
        
        self.returns.index = pd.to_datetime(self.returns.index)
        
        january_returns = self.returns[self.returns.index.month == 1]
        other_months = self.returns[self.returns.index.month != 1]
        
        jan_avg = january_returns.mean() if len(january_returns) > 0 else 0
        other_avg = other_months.mean() if len(other_months) > 0 else 0
        
        return {
            'january_avg_return': round(jan_avg * 100, 2),
            'other_months_avg': round(other_avg * 100, 2),
            'difference': round((jan_avg - other_avg) * 100, 2),
            'effect_present': jan_avg > other_avg * 1.5,
            'sample_years': len(january_returns)
        }
    
    def analyze_turn_of_month(self, days: int = 5) -> Dict:
        """Analyze turn-of-month effect"""
        if self.returns is None:
            return {}
        
        self.returns.index = pd.to_datetime(self.returns.index)
        
        # Get last N days of each month
        tom_returns = []
        
        for date in self.returns.index:
            # Last day of month
            last_day = calendar.monthrange(date.year, date.month)[1]
            
            if date.day > last_day - days:
                tom_returns.append(self.returns[date])
        
        other_returns = self.returns[~self.returns.index.isin(
            [r for r in self.returns.index if r.day > calendar.monthrange(r.year, r.month)[1] - days]
        )]
        
        tom_series = pd.Series(tom_returns)
        
        return {
            'turn_of_month_avg': round(tom_series.mean() * 100, 3) if len(tom_series) > 0 else 0,
            'rest_of_month_avg': round(other_returns.mean() * 100, 3) if len(other_returns) > 0 else 0,
            'effect': 'Present' if len(tom_series) > 0 and tom_series.mean() > other_returns.mean() else 'Absent'
        }
    
    def get_best_worst_months(self) -> Dict:
        """Identify best and worst performing months"""
        monthly = self.analyze_monthly_seasonality()
        
        if not monthly:
            return {}
        
        # Sort by average return
        sorted_months = sorted(
            monthly.items(),
            key=lambda x: x[1]['avg_return'],
            reverse=True
        )
        
        return {
            'best_month': sorted_months[0][0],
            'best_return': sorted_months[0][1]['avg_return'],
            'worst_month': sorted_months[-1][0],
            'worst_return': sorted_months[-1][1]['avg_return'],
            'top_3': [m[0] for m in sorted_months[:3]],
            'bottom_3': [m[0] for m in sorted_months[-3:]]
        }
    
    def generate_seasonal_report(self) -> Dict:
        """Generate comprehensive seasonality report"""
        return {
            'monthly_seasonality': self.analyze_monthly_seasonality(),
            'day_of_week': self.analyze_day_of_week(),
            'quarterly_pattern': self.analyze_quarterly_pattern(),
            'january_effect': self.detect_january_effect(),
            'turn_of_month': self.analyze_turn_of_month(),
            'best_worst_months': self.get_best_worst_months(),
            'timestamp': datetime.now().isoformat()
        }


# Usage
def quick_seasonal_analysis(prices: pd.Series) -> Dict:
    """Quick seasonality analysis"""
    analyzer = SeasonalityAnalyzer()
    analyzer.load_data(prices)
    
    return {
        'monthly': analyzer.analyze_monthly_seasonality(),
        'best_worst': analyzer.get_best_worst_months(),
        'january_effect': analyzer.detect_january_effect()
    }


def get_trading_calendar_insights() -> Dict:
    """Get general trading calendar insights"""
    return {
        'known_effects': {
            'january_effect': 'Small caps outperform in January',
            'turn_of_month': 'Strong returns last/first days of month',
            'holiday_effect': 'Pre-holiday returns often positive',
            'weekend_effect': 'Monday returns often negative',
            'october_effect': 'October historically volatile',
            'sell_in_may': 'May-Oct underperformance vs Nov-Apr'
        },
        'best_practices': [
            'Consider seasonal patterns as supplementary signal',
            'Combine with technical/fundamental analysis',
            'Avoid over-reliance on seasonal effects',
            'Each year/market is different'
        ]
    }
