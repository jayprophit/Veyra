"""
Technical Analysis Pattern Recognition
======================================
Detect chart patterns: Head & Shoulders, Double Top/Bottom, Triangles, Flags
Candlestick patterns: Doji, Hammer, Engulfing, Morning Star
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PatternType(Enum):
    HEAD_SHOULDERS = "head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIANGLE_ASCENDING = "ascending_triangle"
    TRIANGLE_DESCENDING = "descending_triangle"
    TRIANGLE_SYMMETRICAL = "symmetrical_triangle"
    FLAG_BULL = "bull_flag"
    FLAG_BEAR = "bear_flag"
    CUP_HANDLE = "cup_and_handle"
    WEDGE_RISING = "rising_wedge"
    WEDGE_FALLING = "falling_wedge"


class CandlePattern(Enum):
    DOJI = "doji"
    HAMMER = "hammer"
    SHOOTING_STAR = "shooting_star"
    ENGULFING_BULL = "bullish_engulfing"
    ENGULFING_BEAR = "bearish_engulfing"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    THREE_WHITE_SOLDIERS = "three_white_soldiers"
    THREE_BLACK_CROWS = "three_black_crows"


@dataclass
class PatternSignal:
    """Pattern detection result"""
    pattern: str
    direction: str  # 'bullish', 'bearish', 'neutral'
    confidence: float
    start_idx: int
    end_idx: int
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None


class PatternRecognition:
    """
    Chart pattern recognition engine
    
    Detects classic technical patterns in price data
    """
    
    def __init__(self):
        self.patterns_found: List[PatternSignal] = []
    
    def find_local_extrema(self, prices: np.ndarray, 
                          order: int = 5) -> Tuple[List[int], List[int]]:
        """
        Find local maxima and minima in price series
        
        Args:
            prices: Price series
            order: Number of points on each side to consider
        """
        from scipy.signal import argrelextrema
        
        maxima = argrelextrema(prices, np.greater, order=order)[0].tolist()
        minima = argrelextrema(prices, np.less, order=order)[0].tolist()
        
        return maxima, minima
    
    def detect_head_shoulders(self, highs: np.ndarray, 
                              tolerance: float = 0.02) -> Optional[PatternSignal]:
        """
        Detect Head and Shoulders pattern
        
        Pattern: Left Shoulder -> Head -> Right Shoulder
        All peaks should be at similar level except head (highest)
        """
        maxima, _ = self.find_local_extrema(highs)
        
        if len(maxima) < 3:
            return None
        
        # Look for H&S in last 3 peaks
        for i in range(len(maxima) - 2):
            left_shoulder = highs[maxima[i]]
            head = highs[maxima[i+1]]
            right_shoulder = highs[maxima[i+2]]
            
            # Check conditions
            shoulders_similar = abs(left_shoulder - right_shoulder) / head < tolerance
            head_highest = head > max(left_shoulder, right_shoulder) * 1.02
            
            if shoulders_similar and head_highest:
                # Calculate price target (neckline projection)
                neckline = min(highs[maxima[i]:maxima[i+2]])
                head_height = head - neckline
                target = neckline - head_height
                
                return PatternSignal(
                    pattern=PatternType.HEAD_SHOULDERS.value,
                    direction='bearish',
                    confidence=0.75,
                    start_idx=maxima[i],
                    end_idx=maxima[i+2],
                    price_target=round(target, 2),
                    stop_loss=round(head * 1.01, 2)
                )
        
        return None
    
    def detect_double_top(self, highs: np.ndarray,
                         tolerance: float = 0.02) -> Optional[PatternSignal]:
        """Detect Double Top pattern"""
        maxima, _ = self.find_local_extrema(highs)
        
        if len(maxima) < 2:
            return None
        
        for i in range(len(maxima) - 1):
            peak1 = highs[maxima[i]]
            peak2 = highs[maxima[i+1]]
            
            # Peaks should be similar height
            if abs(peak1 - peak2) / peak1 < tolerance:
                # Find valley between
                valley_idx = np.argmin(highs[maxima[i]:maxima[i+1]]) + maxima[i]
                valley = highs[valley_idx]
                
                target = valley - (peak1 - valley)
                
                return PatternSignal(
                    pattern=PatternType.DOUBLE_TOP.value,
                    direction='bearish',
                    confidence=0.70,
                    start_idx=maxima[i],
                    end_idx=maxima[i+1],
                    price_target=round(target, 2),
                    stop_loss=round(max(peak1, peak2) * 1.01, 2)
                )
        
        return None
    
    def detect_double_bottom(self, lows: np.ndarray,
                           tolerance: float = 0.02) -> Optional[PatternSignal]:
        """Detect Double Bottom pattern"""
        _, minima = self.find_local_extrema(lows)
        
        if len(minima) < 2:
            return None
        
        for i in range(len(minima) - 1):
            bottom1 = lows[minima[i]]
            bottom2 = lows[minima[i+1]]
            
            if abs(bottom1 - bottom2) / bottom1 < tolerance:
                peak_idx = np.argmax(lows[minima[i]:minima[i+1]]) + minima[i]
                peak = lows[peak_idx]
                
                target = peak + (peak - bottom1)
                
                return PatternSignal(
                    pattern=PatternType.DOUBLE_BOTTOM.value,
                    direction='bullish',
                    confidence=0.70,
                    start_idx=minima[i],
                    end_idx=minima[i+1],
                    price_target=round(target, 2),
                    stop_loss=round(min(bottom1, bottom2) * 0.99, 2)
                )
        
        return None
    
    def detect_triangles(self, highs: np.ndarray, 
                        lows: np.ndarray) -> Optional[PatternSignal]:
        """Detect triangle patterns"""
        n = len(highs)
        
        if n < 20:
            return None
        
        # Get recent price action
        recent_highs = highs[-20:]
        recent_lows = lows[-20:]
        
        # Fit trendlines
        x = np.arange(20)
        high_slope = np.polyfit(x, recent_highs, 1)[0]
        low_slope = np.polyfit(x, recent_lows, 1)[0]
        
        # Ascending triangle: flat top, rising bottom
        if abs(high_slope) < 0.001 and low_slope > 0.001:
            return PatternSignal(
                pattern=PatternType.TRIANGLE_ASCENDING.value,
                direction='bullish',
                confidence=0.65,
                start_idx=n-20,
                end_idx=n-1,
                price_target=round(highs[-1] + (highs[-1] - lows[-5]), 2)
            )
        
        # Descending triangle: flat bottom, falling top
        if abs(low_slope) < 0.001 and high_slope < -0.001:
            return PatternSignal(
                pattern=PatternType.TRIANGLE_DESCENDING.value,
                direction='bearish',
                confidence=0.65,
                start_idx=n-20,
                end_idx=n-1,
                price_target=round(lows[-1] - (highs[-5] - lows[-1]), 2)
            )
        
        # Symmetrical triangle: converging
        if high_slope < -0.001 and low_slope > 0.001:
            return PatternSignal(
                pattern=PatternType.TRIANGLE_SYMMETRICAL.value,
                direction='neutral',
                confidence=0.60,
                start_idx=n-20,
                end_idx=n-1
            )
        
        return None
    
    def analyze_candlestick_patterns(self, opens: np.ndarray,
                                     highs: np.ndarray,
                                     lows: np.ndarray,
                                     closes: np.ndarray) -> List[Dict]:
        """Analyze candlestick patterns"""
        patterns = []
        n = len(opens)
        
        for i in range(2, n):
            o, h, l, c = opens[i], highs[i], lows[i], closes[i]
            body = abs(c - o)
            upper_shadow = h - max(o, c)
            lower_shadow = min(o, c) - l
            total_range = h - l
            
            # Doji (small body)
            if body < total_range * 0.1:
                patterns.append({
                    'pattern': CandlePattern.DOJI.value,
                    'direction': 'neutral',
                    'idx': i,
                    'confidence': 0.60
                })
            
            # Hammer (small body at top, long lower shadow)
            elif lower_shadow > body * 2 and upper_shadow < body * 0.5 and c > o:
                patterns.append({
                    'pattern': CandlePattern.HAMMER.value,
                    'direction': 'bullish',
                    'idx': i,
                    'confidence': 0.65
                })
            
            # Shooting star (small body at bottom, long upper shadow)
            elif upper_shadow > body * 2 and lower_shadow < body * 0.5 and c < o:
                patterns.append({
                    'pattern': CandlePattern.SHOOTING_STAR.value,
                    'direction': 'bearish',
                    'idx': i,
                    'confidence': 0.65
                })
            
            # Bullish Engulfing
            if i > 0:
                prev_o, prev_c = opens[i-1], closes[i-1]
                if prev_c < prev_o and c > o and o < prev_c and c > prev_o:
                    patterns.append({
                        'pattern': CandlePattern.ENGULFING_BULL.value,
                        'direction': 'bullish',
                        'idx': i,
                        'confidence': 0.70
                    })
                
                # Bearish Engulfing
                if prev_c > prev_o and c < o and o > prev_c and c < prev_o:
                    patterns.append({
                        'pattern': CandlePattern.ENGULFING_BEAR.value,
                        'direction': 'bearish',
                        'idx': i,
                        'confidence': 0.70
                    })
        
        return patterns[-5:]  # Return last 5 patterns
    
    def scan_all_patterns(self, df: pd.DataFrame) -> Dict:
        """Scan for all chart patterns"""
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        opens = df['open'].values
        
        patterns = {
            'chart_patterns': [],
            'candlestick_patterns': [],
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Chart patterns
        hs = self.detect_head_shoulders(highs)
        if hs:
            patterns['chart_patterns'].append(hs)
        
        dt = self.detect_double_top(highs)
        if dt:
            patterns['chart_patterns'].append(dt)
        
        db = self.detect_double_bottom(lows)
        if db:
            patterns['chart_patterns'].append(db)
        
        tri = self.detect_triangles(highs, lows)
        if tri:
            patterns['chart_patterns'].append(tri)
        
        # Candlestick patterns
        patterns['candlestick_patterns'] = self.analyze_candlestick_patterns(
            opens, highs, lows, closes
        )
        
        return patterns


# Usage
def quick_pattern_scan(prices: List[float]) -> Dict:
    """Quick pattern detection"""
    df = pd.DataFrame({
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices
    })
    
    recognizer = PatternRecognition()
    return recognizer.scan_all_patterns(df)


def detect_support_resistance(prices: np.ndarray, 
                              window: int = 10) -> Dict[str, List[float]]:
    """Detect support and resistance levels"""
    from scipy.signal import find_peaks
    
    # Find peaks (resistance)
    peaks, _ = find_peaks(prices, distance=window)
    resistance_levels = prices[peaks].tolist()
    
    # Find troughs (support)
    troughs, _ = find_peaks(-prices, distance=window)
    support_levels = prices[troughs].tolist()
    
    return {
        'support': sorted(support_levels[-5:]),
        'resistance': sorted(resistance_levels[-5:])
    }
