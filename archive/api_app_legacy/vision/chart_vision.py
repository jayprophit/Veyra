"""
ChartVision - Computer Vision for Chart Pattern Recognition
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from scipy.signal import argrelextrema
import cv2


class PatternType(Enum):
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    BULL_FLAG = "bull_flag"
    BEAR_FLAG = "bear_flag"
    WEDGE_RISING = "wedge_rising"
    WEDGE_FALLING = "wedge_falling"
    CUP_AND_HANDLE = "cup_and_handle"
    DOJI = "doji"
    HAMMER = "hammer"
    ENGULFING_BULLISH = "engulfing_bullish"
    ENGULFING_BEARISH = "engulfing_bearish"


@dataclass
class ChartPattern:
    pattern_type: PatternType
    symbol: str
    confidence: float
    target_price: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class ChartVision:
    """Computer Vision engine for chart pattern detection"""
    
    def __init__(self):
        self.min_bars = 20
        
    def analyze_chart(self, symbol: str, df: pd.DataFrame) -> List[ChartPattern]:
        """Analyze OHLCV data and detect patterns"""
        patterns = []
        if len(df) < self.min_bars:
            return patterns
            
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        opens = df['open'].values
        
        # Find swing points
        swing_highs = argrelextrema(highs, np.greater, order=5)[0]
        swing_lows = argrelextrema(lows, np.less, order=5)[0]
        
        # Detect patterns
        patterns.extend(self._detect_head_and_shoulders(symbol, highs, lows, swing_highs))
        patterns.extend(self._detect_double_patterns(symbol, highs, lows, swing_highs, swing_lows))
        patterns.extend(self._detect_triangles(symbol, highs, lows, closes))
        patterns.extend(self._detect_candlesticks(symbol, opens, highs, lows, closes))
        
        return [p for p in patterns if p.confidence > 0.6]
    
    def _detect_head_and_shoulders(self, symbol, highs, lows, swing_highs):
        patterns = []
        for i in range(len(swing_highs) - 2):
            ls, head, rs = swing_highs[i], swing_highs[i+1], swing_highs[i+2]
            if highs[head] > highs[ls] and highs[head] > highs[rs]:
                if abs(highs[ls] - highs[rs]) / highs[ls] < 0.05:
                    patterns.append(ChartPattern(
                        pattern_type=PatternType.HEAD_AND_SHOULDERS,
                        symbol=symbol,
                        confidence=0.75
                    ))
        return patterns
    
    def _detect_double_patterns(self, symbol, highs, lows, swing_highs, swing_lows):
        patterns = []
        # Double Top
        for i in range(len(swing_highs) - 1):
            if abs(highs[swing_highs[i]] - highs[swing_highs[i+1]]) / highs[swing_highs[i]] < 0.03:
                patterns.append(ChartPattern(
                    pattern_type=PatternType.DOUBLE_TOP,
                    symbol=symbol,
                    confidence=0.72
                ))
        # Double Bottom
        for i in range(len(swing_lows) - 1):
            if abs(lows[swing_lows[i]] - lows[swing_lows[i+1]]) / lows[swing_lows[i]] < 0.03:
                patterns.append(ChartPattern(
                    pattern_type=PatternType.DOUBLE_BOTTOM,
                    symbol=symbol,
                    confidence=0.72
                ))
        return patterns
    
    def _detect_triangles(self, symbol, highs, lows, closes):
        patterns = []
        window = 30
        if len(highs) < window:
            return patterns
            
        x = np.arange(window)
        upper_slope, _ = np.polyfit(x, highs[-window:], 1)
        lower_slope, _ = np.polyfit(x, lows[-window:], 1)
        
        if abs(upper_slope) < 0.001 and lower_slope > 0.001:
            patterns.append(ChartPattern(PatternType.ASCENDING_TRIANGLE, symbol, 0.70))
        elif abs(lower_slope) < 0.001 and upper_slope < -0.001:
            patterns.append(ChartPattern(PatternType.DESCENDING_TRIANGLE, symbol, 0.70))
        elif upper_slope < -0.001 and lower_slope > 0.001:
            patterns.append(ChartPattern(PatternType.WEDGE_RISING, symbol, 0.65))
        
        return patterns
    
    def _detect_candlesticks(self, symbol, opens, highs, lows, closes):
        patterns = []
        for i in range(2, len(closes)):
            o, h, l, c = opens[i], highs[i], lows[i], closes[i]
            body = abs(c - o)
            
            # Doji
            if body < (h - l) * 0.1:
                patterns.append(ChartPattern(PatternType.DOJI, symbol, 0.75))
            
            # Hammer
            if (min(o, c) - l) > body * 2 and c > o:
                patterns.append(ChartPattern(PatternType.HAMMER, symbol, 0.72))
            
            # Bullish Engulfing
            if c > o and closes[i-1] < opens[i-1] and o < closes[i-1] and c > opens[i-1]:
                patterns.append(ChartPattern(PatternType.ENGULFING_BULLISH, symbol, 0.74))
            
            # Bearish Engulfing
            if c < o and closes[i-1] > opens[i-1] and o > closes[i-1] and c < opens[i-1]:
                patterns.append(ChartPattern(PatternType.ENGULFING_BEARISH, symbol, 0.74))
        
        return patterns
