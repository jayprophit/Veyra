"""
Market Breadth Analyzer
=======================
Track market internals: Advance/Decline, New highs/lows, Volume breadth
McClellan Oscillator, Arms Index (TRIN), Bullish Percent Index
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class BreadthReading:
    """Market breadth data point"""
    date: datetime
    advances: int
    declines: int
    unchanged: int
    adv_volume: float
    dec_volume: float
    new_highs: int
    new_lows: int


class MarketBreadthAnalyzer:
    """
    Analyze market breadth indicators
    
    Key metrics:
    - Advance/Decline Line
    - McClellan Oscillator
    - Arms Index (TRIN)
    - New Highs/New Lows
    - Bullish Percent Index
    """
    
    def __init__(self):
        self.breadth_history: List[BreadthReading] = []
    
    def add_reading(self, reading: BreadthReading):
        """Add daily breadth reading"""
        self.breadth_history.append(reading)
    
    def calculate_ad_line(self) -> pd.Series:
        """Calculate Advance-Decline Line"""
        if not self.breadth_history:
            return pd.Series()
        
        ad_line = []
        cumulative = 0
        
        for reading in self.breadth_history:
            net_advances = reading.advances - reading.declines
            cumulative += net_advances
            ad_line.append(cumulative)
        
        dates = [r.date for r in self.breadth_history]
        return pd.Series(ad_line, index=dates)
    
    def calculate_mcclellan_oscillator(self, 
                                      fast_period: int = 19,
                                      slow_period: int = 39) -> pd.Series:
        """
        Calculate McClellan Oscillator
        
        MACD of Advance-Decline Line
        """
        if len(self.breadth_history) < slow_period:
            return pd.Series()
        
        # Calculate daily net advances
        net_advances = [
            r.advances - r.declines for r in self.breadth_history
        ]
        
        dates = [r.date for r in self.breadth_history]
        
        # Calculate EMAs
        series = pd.Series(net_advances, index=dates)
        ema_fast = series.ewm(span=fast_period, adjust=False).mean()
        ema_slow = series.ewm(span=slow_period, adjust=False).mean()
        
        # McClellan Oscillator
        oscillator = ema_fast - ema_slow
        
        return oscillator
    
    def calculate_arms_index(self) -> List[Dict]:
        """
        Calculate Arms Index (TRIN)
        
        TRIN = (Advances/Declines) / (Adv Volume/Dec Volume)
        
        < 1: Bullish (more volume in advancing stocks)
        > 1: Bearish (more volume in declining stocks)
        """
        arms_data = []
        
        for reading in self.breadth_history:
            if reading.declines > 0 and reading.dec_volume > 0:
                ad_ratio = reading.advances / reading.declines
                volume_ratio = reading.adv_volume / reading.dec_volume
                trin = ad_ratio / volume_ratio
                
                interpretation = 'Bullish' if trin < 0.8 else 'Neutral' if trin < 1.2 else 'Bearish'
                
                arms_data.append({
                    'date': reading.date.strftime('%Y-%m-%d'),
                    'trin': round(trin, 3),
                    'interpretation': interpretation,
                    'advances': reading.advances,
                    'declines': reading.declines
                })
        
        return arms_data
    
    def calculate_bullish_percent(self, 
                                 bullish_stocks: int,
                                 total_stocks: int) -> Dict:
        """
        Calculate Bullish Percent Index
        
        % of stocks on Point & Figure buy signals
        """
        if total_stocks == 0:
            return {}
        
        bp = (bullish_stocks / total_stocks) * 100
        
        # Determine field position
        if bp > 70:
            field_position = 'Overbought - X-Column (Bull Confirmed)'
        elif bp > 50:
            field_position = 'Bull Alert - Rising'
        elif bp > 30:
            field_position = 'Bear Alert - Falling'
        else:
            field_position = 'Oversold - O-Column (Bear Confirmed)'
        
        return {
            'bullish_percent': round(bp, 2),
            'bullish_stocks': bullish_stocks,
            'total_stocks': total_stocks,
            'field_position': field_position,
            'signal': 'Bullish' if bp > 50 else 'Bearish' if bp < 50 else 'Neutral'
        }
    
    def analyze_new_highs_lows(self) -> Dict:
        """Analyze new highs vs new lows ratio"""
        if not self.breadth_history:
            return {}
        
        recent = self.breadth_history[-20:]  # Last 20 days
        
        total_new_highs = sum(r.new_highs for r in recent)
        total_new_lows = sum(r.new_lows for r in recent)
        
        if total_new_lows == 0:
            ratio = float('inf')
        else:
            ratio = total_new_highs / total_new_lows
        
        # Determine market condition
        if ratio > 2:
            condition = 'Strong Bullish (Leadership)'
        elif ratio > 1:
            condition = 'Bullish'
        elif ratio > 0.5:
            condition = 'Neutral'
        else:
            condition = 'Bearish (Weak Leadership)'
        
        return {
            'new_highs_20d': total_new_highs,
            'new_lows_20d': total_new_lows,
            'hl_ratio': round(ratio, 2) if ratio != float('inf') else 'Infinite',
            'market_condition': condition,
            'signal': 'Bullish' if ratio > 1 else 'Bearish' if ratio < 0.5 else 'Neutral'
        }
    
    def get_breadth_summary(self) -> Dict:
        """Get comprehensive breadth summary"""
        if not self.breadth_history:
            return {'error': 'No breadth data available'}
        
        latest = self.breadth_history[-1]
        
        return {
            'latest_date': latest.date.strftime('%Y-%m-%d'),
            'advances': latest.advances,
            'declines': latest.declines,
            'unchanged': latest.unchanged,
            'ad_ratio': round(latest.advances / latest.declines, 2) if latest.declines > 0 else 0,
            'volume_advance': latest.adv_volume,
            'volume_decline': latest.dec_volume,
            'new_highs': latest.new_highs,
            'new_lows': latest.new_lows,
            'mcclellan_oscillator': round(self.calculate_mcclellan_oscillator().iloc[-1], 2) if len(self.breadth_history) > 39 else None,
            'ad_line_trend': self._get_ad_line_trend(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_ad_line_trend(self) -> str:
        """Determine AD Line trend"""
        if len(self.breadth_history) < 10:
            return 'Insufficient data'
        
        ad_line = self.calculate_ad_line()
        
        if len(ad_line) < 10:
            return 'Insufficient data'
        
        recent = ad_line.iloc[-5:].mean()
        previous = ad_line.iloc[-10:-5].mean()
        
        if recent > previous * 1.02:
            return 'Rising (Bullish)'
        elif recent < previous * 0.98:
            return 'Falling (Bearish)'
        else:
            return 'Flat (Neutral)'


# Usage
def quick_breadth_analysis(advances: int, declines: int, 
                          adv_vol: float, dec_vol: float) -> Dict:
    """Quick market breadth check"""
    analyzer = MarketBreadthAnalyzer()
    
    reading = BreadthReading(
        date=datetime.now(),
        advances=advances,
        declines=declines,
        unchanged=0,
        adv_volume=adv_vol,
        dec_volume=dec_vol,
        new_highs=50,
        new_lows=20
    )
    
    analyzer.add_reading(reading)
    
    return analyzer.get_breadth_summary()


def calculate_trin(advances: int, declines: int,
                  adv_vol: float, dec_vol: float) -> float:
    """Quick TRIN calculation"""
    if declines == 0 or dec_vol == 0:
        return 0
    
    ad_ratio = advances / declines
    vol_ratio = adv_vol / dec_vol
    
    return round(ad_ratio / vol_ratio, 3)
