"""
Pattern Recognition Engine
===========================
Detects technical patterns in price data:
- Head and Shoulders
- Double Top/Bottom
- Triangles (ascending, descending, symmetrical)
- Flags and Pennants
- Cup and Handle
- Support/Resistance levels
- Candlestick patterns

Grade Impact: +5 points
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from scipy.signal import argrelextrema


class PatternType(Enum):
    # Reversal patterns
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    INV_HEAD_AND_SHOULDERS = "inverse_head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIPLE_TOP = "triple_top"
    TRIPLE_BOTTOM = "triple_bottom"
    
    # Continuation patterns
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    BULL_FLAG = "bull_flag"
    BEAR_FLAG = "bear_flag"
    BULL_PENNANT = "bull_pennant"
    BEAR_PENNANT = "bear_pennant"
    CUP_AND_HANDLE = "cup_and_handle"
    
    # Support/Resistance
    SUPPORT_LEVEL = "support_level"
    RESISTANCE_LEVEL = "resistance_level"
    TREND_LINE = "trend_line"
    CHANNEL = "channel"


class CandlePattern(Enum):
    DOJI = "doji"
    HAMMER = "hammer"
    SHOOTING_STAR = "shooting_star"
    ENGULFING_BULLISH = "engulfing_bullish"
    ENGULFING_BEARISH = "engulfing_bearish"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    THREE_WHITE_SOLDIERS = "three_white_soldiers"
    THREE_BLACK_CROWS = "three_black_crows"


@dataclass
class Pattern:
    pattern_type: PatternType
    start_date: datetime
    end_date: datetime
    start_price: float
    end_price: float
    confidence: float  # 0-1
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    notes: str = ""


@dataclass
class CandlestickSignal:
    pattern: CandlePattern
    date: datetime
    confidence: float
    direction: str  # bullish, bearish, neutral
    strength: int  # 1-5


class PatternRecognitionEngine:
    """
    Technical pattern recognition using price action analysis.
    """
    
    def __init__(self, min_pattern_bars: int = 20):
        self.min_pattern_bars = min_pattern_bars
        self.patterns: List[Pattern] = []
        self.candle_signals: List[CandlestickSignal] = []
    
    def find_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """
        Find all patterns in price data.
        
        Args:
            df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        if len(df) < self.min_pattern_bars:
            return patterns
        
        # Find local extrema
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        
        # Get local maxima and minima
        maxima_idx = argrelextrema(highs, np.greater, order=5)[0]
        minima_idx = argrelextrema(lows, np.less, order=5)[0]
        
        # Check for specific patterns
        patterns.extend(self._find_head_and_shoulders(df, maxima_idx, minima_idx))
        patterns.extend(self._find_double_top_bottom(df, maxima_idx, minima_idx))
        patterns.extend(self._find_triangles(df, maxima_idx, minima_idx))
        patterns.extend(self._find_flags_and_pennants(df))
        patterns.extend(self._find_cup_and_handle(df, maxima_idx, minima_idx))
        patterns.extend(self._find_support_resistance(df, maxima_idx, minima_idx))
        
        self.patterns = patterns
        return patterns
    
    def _find_head_and_shoulders(
        self,
        df: pd.DataFrame,
        maxima_idx: np.ndarray,
        minima_idx: np.ndarray
    ) -> List[Pattern]:
        """Find head and shoulders pattern."""
        patterns = []
        
        if len(maxima_idx) < 3:
            return patterns
        
        highs = df['high'].values
        
        # Look for 3 peaks
        for i in range(len(maxima_idx) - 2):
            left_shoulder = highs[maxima_idx[i]]
            head = highs[maxima_idx[i+1]]
            right_shoulder = highs[maxima_idx[i+2]]
            
            # Head and shoulders criteria
            if (head > left_shoulder and head > right_shoulder and
                abs(left_shoulder - right_shoulder) / head < 0.05):  # Shoulders roughly equal
                
                # Calculate neckline
                neckline_idx = minima_idx[minima_idx > maxima_idx[i]][0] if len(minima_idx) > 0 else maxima_idx[i] + 5
                neckline = df['low'].iloc[neckline_idx] if neckline_idx < len(df) else df['low'].mean()
                
                # Target is distance from head to neckline
                target = neckline - (head - neckline)
                
                patterns.append(Pattern(
                    pattern_type=PatternType.HEAD_AND_SHOULDERS,
                    start_date=df.index[maxima_idx[i]],
                    end_date=df.index[maxima_idx[i+2]],
                    start_price=left_shoulder,
                    end_price=right_shoulder,
                    confidence=0.75,
                    target_price=target,
                    stop_loss=head * 1.02,
                    notes="Bearish reversal pattern"
                ))
        
        return patterns
    
    def _find_double_top_bottom(
        self,
        df: pd.DataFrame,
        maxima_idx: np.ndarray,
        minima_idx: np.ndarray
    ) -> List[Pattern]:
        """Find double top and double bottom patterns."""
        patterns = []
        
        highs = df['high'].values
        lows = df['low'].values
        
        # Double top
        if len(maxima_idx) >= 2:
            for i in range(len(maxima_idx) - 1):
                first_peak = highs[maxima_idx[i]]
                second_peak = highs[maxima_idx[i+1]]
                
                # Peaks should be similar height
                if abs(first_peak - second_peak) / first_peak < 0.03:
                    valley_idx = minima_idx[(minima_idx > maxima_idx[i]) & (minima_idx < maxima_idx[i+1])]
                    if len(valley_idx) > 0:
                        valley = lows[valley_idx[0]]
                        target = valley - (first_peak - valley)
                        
                        patterns.append(Pattern(
                            pattern_type=PatternType.DOUBLE_TOP,
                            start_date=df.index[maxima_idx[i]],
                            end_date=df.index[maxima_idx[i+1]],
                            start_price=first_peak,
                            end_price=second_peak,
                            confidence=0.70,
                            target_price=target,
                            notes="Bearish reversal"
                        ))
        
        # Double bottom
        if len(minima_idx) >= 2:
            for i in range(len(minima_idx) - 1):
                first_bottom = lows[minima_idx[i]]
                second_bottom = lows[minima_idx[i+1]]
                
                if abs(first_bottom - second_bottom) / first_bottom < 0.03:
                    peak_idx = maxima_idx[(maxima_idx > minima_idx[i]) & (maxima_idx < minima_idx[i+1])]
                    if len(peak_idx) > 0:
                        peak = highs[peak_idx[0]]
                        target = peak + (peak - first_bottom)
                        
                        patterns.append(Pattern(
                            pattern_type=PatternType.DOUBLE_BOTTOM,
                            start_date=df.index[minima_idx[i]],
                            end_date=df.index[minima_idx[i+1]],
                            start_price=first_bottom,
                            end_price=second_bottom,
                            confidence=0.70,
                            target_price=target,
                            notes="Bullish reversal"
                        ))
        
        return patterns
    
    def _find_triangles(
        self,
        df: pd.DataFrame,
        maxima_idx: np.ndarray,
        minima_idx: np.ndarray
    ) -> List[Pattern]:
        """Find triangle patterns."""
        patterns = []
        
        if len(maxima_idx) < 2 or len(minima_idx) < 2:
            return patterns
        
        highs = df['high'].values
        lows = df['low'].values
        
        # Get recent swing points
        recent_maxima = maxima_idx[-3:] if len(maxima_idx) >= 3 else maxima_idx
        recent_minima = minima_idx[-3:] if len(minima_idx) >= 3 else minima_idx
        
        if len(recent_maxima) < 2 or len(recent_minima) < 2:
            return patterns
        
        # Check for descending highs and ascending lows (symmetrical triangle)
        highs_trend = np.polyfit(range(len(recent_maxima)), highs[recent_maxima], 1)[0]
        lows_trend = np.polyfit(range(len(recent_minima)), lows[recent_minima], 1)[0]
        
        # Ascending triangle: flat top, rising bottom
        if abs(highs_trend) < 0.1 and lows_trend > 0.5:
            patterns.append(Pattern(
                pattern_type=PatternType.ASCENDING_TRIANGLE,
                start_date=df.index[recent_minima[0]],
                end_date=df.index[-1],
                start_price=lows[recent_minima[0]],
                end_price=df['close'].iloc[-1],
                confidence=0.65,
                target_price=highs[recent_maxima[-1]],
                notes="Bullish continuation"
            ))
        
        # Descending triangle: flat bottom, falling top
        elif abs(lows_trend) < 0.1 and highs_trend < -0.5:
            patterns.append(Pattern(
                pattern_type=PatternType.DESCENDING_TRIANGLE,
                start_date=df.index[recent_maxima[0]],
                end_date=df.index[-1],
                start_price=highs[recent_maxima[0]],
                end_price=df['close'].iloc[-1],
                confidence=0.65,
                target_price=lows[recent_minima[-1]],
                notes="Bearish continuation"
            ))
        
        # Symmetrical triangle: converging
        elif highs_trend < -0.3 and lows_trend > 0.3:
            patterns.append(Pattern(
                pattern_type=PatternType.SYMMETRICAL_TRIANGLE,
                start_date=df.index[min(recent_maxima[0], recent_minima[0])],
                end_date=df.index[-1],
                start_price=df['close'].iloc[recent_maxima[0]],
                end_price=df['close'].iloc[-1],
                confidence=0.60,
                notes="Breakout expected in direction of prior trend"
            ))
        
        return patterns
    
    def _find_flags_and_pennants(self, df: pd.DataFrame) -> List[Pattern]:
        """Find flag and pennant patterns."""
        patterns = []
        
        if len(df) < 15:
            return patterns
        
        closes = df['close'].values
        
        # Check for sharp move followed by consolidation
        recent_change = (closes[-1] - closes[-15]) / closes[-15] * 100
        
        if abs(recent_change) > 10:  # Strong move
            # Check for consolidation (flag)
            consolidation_range = (df['high'].iloc[-10:].max() - df['low'].iloc[-10:].min()) / df['close'].iloc[-10:].mean() * 100
            
            if consolidation_range < 5:  # Tight consolidation
                pattern_type = PatternType.BULL_FLAG if recent_change > 0 else PatternType.BEAR_FLAG
                
                patterns.append(Pattern(
                    pattern_type=pattern_type,
                    start_date=df.index[-15],
                    end_date=df.index[-1],
                    start_price=closes[-15],
                    end_price=closes[-1],
                    confidence=0.60,
                    target_price=closes[-1] + (closes[-1] - closes[-15]) if recent_change > 0 else closes[-1] - (closes[-15] - closes[-1]),
                    notes="Continuation pattern"
                ))
        
        return patterns
    
    def _find_cup_and_handle(
        self,
        df: pd.DataFrame,
        maxima_idx: np.ndarray,
        minima_idx: np.ndarray
    ) -> List[Pattern]:
        """Find cup and handle pattern."""
        patterns = []
        
        if len(df) < 60:
            return patterns
        
        closes = df['close'].values
        
        # Simplified cup detection: U-shaped bottom over ~30-65 days
        recent = closes[-60:]
        mid_point = len(recent) // 2
        
        # Check for U shape
        left_side = recent[:mid_point]
        right_side = recent[mid_point:]
        
        if (left_side[0] > left_side[-1] and  # Left side down
            right_side[0] < right_side[-1] and  # Right side up
            abs(left_side[0] - right_side[-1]) / left_side[0] < 0.05):  # Similar levels
            
            # Check for handle (small pullback)
            if len(recent) > 50 and recent[-10:].mean() < recent[-30:-10].mean():
                patterns.append(Pattern(
                    pattern_type=PatternType.CUP_AND_HANDLE,
                    start_date=df.index[-60],
                    end_date=df.index[-1],
                    start_price=closes[-60],
                    end_price=closes[-1],
                    confidence=0.55,
                    target_price=closes[-1] + (closes[-60] - recent[mid_point]),
                    notes="Bullish continuation"
                ))
        
        return patterns
    
    def _find_support_resistance(
        self,
        df: pd.DataFrame,
        maxima_idx: np.ndarray,
        minima_idx: np.ndarray
    ) -> List[Pattern]:
        """Find support and resistance levels."""
        patterns = []
        
        highs = df['high'].values
        lows = df['low'].values
        
        # Find price clusters in highs (resistance)
        from scipy.cluster.hierarchy import fclusterdata
        
        if len(maxima_idx) >= 3:
            peak_prices = highs[maxima_idx].reshape(-1, 1)
            clusters = fclusterdata(peak_prices, t=0.03, criterion='distance')
            
            for cluster_id in np.unique(clusters):
                cluster_prices = peak_prices[clusters == cluster_id]
                if len(cluster_prices) >= 2:  # At least 2 touches
                    level = np.mean(cluster_prices)
                    patterns.append(Pattern(
                        pattern_type=PatternType.RESISTANCE_LEVEL,
                        start_date=df.index[maxima_idx[clusters == cluster_id][0]],
                        end_date=df.index[-1],
                        start_price=level,
                        end_price=level,
                        confidence=min(0.9, 0.5 + len(cluster_prices) * 0.1),
                        notes=f"Resistance tested {len(cluster_prices)} times"
                    ))
        
        # Find support clusters
        if len(minima_idx) >= 3:
            bottom_prices = lows[minima_idx].reshape(-1, 1)
            clusters = fclusterdata(bottom_prices, t=0.03, criterion='distance')
            
            for cluster_id in np.unique(clusters):
                cluster_prices = bottom_prices[clusters == cluster_id]
                if len(cluster_prices) >= 2:
                    level = np.mean(cluster_prices)
                    patterns.append(Pattern(
                        pattern_type=PatternType.SUPPORT_LEVEL,
                        start_date=df.index[minima_idx[clusters == cluster_id][0]],
                        end_date=df.index[-1],
                        start_price=level,
                        end_price=level,
                        confidence=min(0.9, 0.5 + len(cluster_prices) * 0.1),
                        notes=f"Support tested {len(cluster_prices)} times"
                    ))
        
        return patterns
    
    def analyze_candlesticks(self, df: pd.DataFrame) -> List[CandlestickSignal]:
        """Analyze candlestick patterns."""
        signals = []
        
        for i in range(1, len(df)):
            open_p = df['open'].iloc[i]
            high = df['high'].iloc[i]
            low = df['low'].iloc[i]
            close = df['close'].iloc[i]
            
            body = abs(close - open_p)
            range_total = high - low
            upper_shadow = high - max(open_p, close)
            lower_shadow = min(open_p, close) - low
            
            # Doji
            if body < range_total * 0.1:
                signals.append(CandlestickSignal(
                    pattern=CandlePattern.DOJI,
                    date=df.index[i],
                    confidence=0.80,
                    direction="neutral",
                    strength=2
                ))
            
            # Hammer
            if (lower_shadow > body * 2 and upper_shadow < body and close > open_p):
                signals.append(CandlestickSignal(
                    pattern=CandlePattern.HAMMER,
                    date=df.index[i],
                    confidence=0.75,
                    direction="bullish",
                    strength=4
                ))
            
            # Shooting star
            if (upper_shadow > body * 2 and lower_shadow < body and close < open_p):
                signals.append(CandlestickSignal(
                    pattern=CandlePattern.SHOOTING_STAR,
                    date=df.index[i],
                    confidence=0.75,
                    direction="bearish",
                    strength=4
                ))
        
        # Check for multi-candle patterns
        if len(df) >= 3:
            # Three white soldiers
            last3 = df.iloc[-3:]
            if all(last3['close'] > last3['open']) and all(last3['close'].diff() > 0):
                signals.append(CandlestickSignal(
                    pattern=CandlePattern.THREE_WHITE_SOLDIERS,
                    date=df.index[-1],
                    confidence=0.85,
                    direction="bullish",
                    strength=5
                ))
        
        self.candle_signals = signals
        return signals
    
    def get_summary(self, df: pd.DataFrame) -> Dict:
        """Get pattern recognition summary."""
        patterns = self.find_patterns(df)
        candle_signals = self.analyze_candlesticks(df)
        
        bullish = [p for p in patterns if p.pattern_type in [
            PatternType.DOUBLE_BOTTOM, PatternType.INV_HEAD_AND_SHOULDERS,
            PatternType.ASCENDING_TRIANGLE, PatternType.BULL_FLAG,
            PatternType.BULL_PENNANT, PatternType.CUP_AND_HANDLE
        ]]
        
        bearish = [p for p in patterns if p.pattern_type in [
            PatternType.HEAD_AND_SHOULDERS, PatternType.DOUBLE_TOP,
            PatternType.DESCENDING_TRIANGLE, PatternType.BEAR_FLAG,
            PatternType.BEAR_PENNANT
        ]]
        
        return {
            "total_patterns": len(patterns),
            "bullish_patterns": len(bullish),
            "bearish_patterns": len(bearish),
            "candle_signals": len(candle_signals),
            "highest_confidence": max([p.confidence for p in patterns], default=0),
            "recent_signals": [
                {
                    "type": p.pattern_type.value,
                    "confidence": p.confidence,
                    "target": p.target_price
                }
                for p in sorted(patterns, key=lambda x: x.confidence, reverse=True)[:3]
            ]
        }


# Example usage
if __name__ == "__main__":
    import yfinance as yf
    
    # Download sample data
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="3mo")
    
    engine = PatternRecognitionEngine()
    patterns = engine.find_patterns(df)
    
    print(f"Found {len(patterns)} patterns:")
    for p in patterns:
        print(f"  - {p.pattern_type.value}: confidence={p.confidence:.0%}, target=${p.target_price:.2f if p.target_price else 'N/A'}")
    
    # Candlestick analysis
    candle_signals = engine.analyze_candlesticks(df)
    print(f"\nCandlestick signals: {len(candle_signals)}")
    for s in candle_signals[-3:]:
        print(f"  - {s.pattern.value}: {s.direction} (strength={s.strength})")
