"""
Pattern Recognition for Technical Analysis
Detects chart patterns like double tops, head and shoulders, triangles
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

class PatternType(Enum):
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    TRIANGLE_ASCENDING = "triangle_ascending"
    TRIANGLE_DESCENDING = "triangle_descending"
    FLAG_BULLISH = "flag_bullish"
    FLAG_BEARISH = "flag_bearish"

@dataclass
class Pattern:
    type: PatternType
    symbol: str
    confidence: float
    start_idx: int
    end_idx: int
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None

class PatternRecognition:
    """
    Detect technical chart patterns in price data
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.patterns: List[Pattern] = []
    
    def find_local_extrema(self, prices: List[float], window: int = 5) -> Tuple[List[int], List[int]]:
        """Find local maxima and minima"""
        maxima = []
        minima = []
        
        for i in range(window, len(prices) - window):
            # Local maximum
            if all(prices[i] > prices[i-j] for j in range(1, window+1)) and \
               all(prices[i] > prices[i+j] for j in range(1, window+1)):
                maxima.append(i)
            
            # Local minimum
            if all(prices[i] < prices[i-j] for j in range(1, window+1)) and \
               all(prices[i] < prices[i+j] for j in range(1, window+1)):
                minima.append(i)
        
        return maxima, minima
    
    def detect_double_top(self, prices: List[float], maxima: List[int]) -> Optional[Pattern]:
        """Detect double top pattern"""
        if len(maxima) < 2:
            return None
        
        for i in range(len(maxima) - 1):
            first_peak = prices[maxima[i]]
            second_peak = prices[maxima[i+1]]
            
            # Check if peaks are similar height (within 3%)
            height_diff = abs(first_peak - second_peak) / first_peak
            
            if height_diff < 0.03:
                # Check for valley between peaks (at least 5% drop)
                valley_idx = minima[i] if i < len(minima) else (maxima[i] + maxima[i+1]) // 2
                if valley_idx > maxima[i] and valley_idx < maxima[i+1]:
                    valley_price = prices[valley_idx]
                    drop_pct = (first_peak - valley_price) / first_peak
                    
                    if drop_pct > 0.05:
                        # Pattern confirmed
                        target_price = valley_price - (first_peak - valley_price) * 0.5
                        stop_loss = max(first_peak, second_peak) * 1.02
                        
                        return Pattern(
                            type=PatternType.DOUBLE_TOP,
                            symbol="",  # Set by caller
                            confidence=round(1 - height_diff, 2),
                            start_idx=maxima[i],
                            end_idx=maxima[i+1],
                            price_target=round(target_price, 2),
                            stop_loss=round(stop_loss, 2)
                        )
        
        return None
    
    def detect_double_bottom(self, prices: List[float], minima: List[int]) -> Optional[Pattern]:
        """Detect double bottom pattern"""
        if len(minima) < 2:
            return None
        
        for i in range(len(minima) - 1):
            first_bottom = prices[minima[i]]
            second_bottom = prices[minima[i+1]]
            
            # Check if bottoms are similar depth (within 3%)
            depth_diff = abs(first_bottom - second_bottom) / first_bottom
            
            if depth_diff < 0.03:
                # Check for peak between bottoms (at least 5% rise)
                peak_idx = maxima[i] if i < len(maxima) else (minima[i] + minima[i+1]) // 2
                if peak_idx > minima[i] and peak_idx < minima[i+1]:
                    peak_price = prices[peak_idx]
                    rise_pct = (peak_price - first_bottom) / first_bottom
                    
                    if rise_pct > 0.05:
                        # Pattern confirmed
                        target_price = peak_price + (peak_price - first_bottom) * 0.5
                        stop_loss = min(first_bottom, second_bottom) * 0.98
                        
                        return Pattern(
                            type=PatternType.DOUBLE_BOTTOM,
                            symbol="",
                            confidence=round(1 - depth_diff, 2),
                            start_idx=minima[i],
                            end_idx=minima[i+1],
                            price_target=round(target_price, 2),
                            stop_loss=round(stop_loss, 2)
                        )
        
        return None
    
    def detect_head_and_shoulders(self, prices: List[float], maxima: List[int], minima: List[int]) -> Optional[Pattern]:
        """Detect head and shoulders pattern"""
        if len(maxima) < 3:
            return None
        
        for i in range(len(maxima) - 2):
            left_shoulder = prices[maxima[i]]
            head = prices[maxima[i+1]]
            right_shoulder = prices[maxima[i+2]]
            
            # Head must be higher than shoulders
            if head > left_shoulder and head > right_shoulder:
                # Shoulders should be similar height
                shoulder_diff = abs(left_shoulder - right_shoulder) / left_shoulder
                
                if shoulder_diff < 0.05:
                    head_height = (head - left_shoulder) / left_shoulder
                    
                    if head_height > 0.03:  # Head significantly higher
                        # Find neckline
                        neckline_idx = minima[i+1] if i+1 < len(minima) else (maxima[i+1] + maxima[i+2]) // 2
                        neckline_price = prices[neckline_idx]
                        
                        target_price = neckline_price - (head - neckline_price)
                        stop_loss = head * 1.01
                        
                        return Pattern(
                            type=PatternType.HEAD_AND_SHOULDERS,
                            symbol="",
                            confidence=round(1 - shoulder_diff, 2),
                            start_idx=maxima[i],
                            end_idx=maxima[i+2],
                            price_target=round(target_price, 2),
                            stop_loss=round(stop_loss, 2)
                        )
        
        return None
    
    def detect_triangles(self, prices: List[float], maxima: List[int], minima: List[int]) -> List[Pattern]:
        """Detect triangle patterns (ascending/descending)"""
        patterns = []
        
        if len(maxima) < 2 or len(minima) < 2:
            return patterns
        
        # Check last 4-6 extrema for triangle formation
        recent_maxima = maxima[-4:] if len(maxima) >= 4 else maxima
        recent_minima = minima[-4:] if len(minima) >= 4 else minima
        
        if len(recent_maxima) >= 2 and len(recent_minima) >= 2:
            # Ascending triangle: flat top, rising bottom
            max_prices = [prices[i] for i in recent_maxima]
            min_prices = [prices[i] for i in recent_minima]
            
            top_flat = np.std(max_prices) / np.mean(max_prices) < 0.02
            bottom_rising = min_prices[-1] > min_prices[0]
            
            if top_flat and bottom_rising:
                patterns.append(Pattern(
                    type=PatternType.TRIANGLE_ASCENDING,
                    symbol="",
                    confidence=0.75,
                    start_idx=recent_minima[0],
                    end_idx=recent_maxima[-1]
                ))
            
            # Descending triangle: flat bottom, falling top
            bottom_flat = np.std(min_prices) / np.mean(min_prices) < 0.02
            top_falling = max_prices[-1] < max_prices[0]
            
            if bottom_flat and top_falling:
                patterns.append(Pattern(
                    type=PatternType.TRIANGLE_DESCENDING,
                    symbol="",
                    confidence=0.75,
                    start_idx=recent_maxima[0],
                    end_idx=recent_minima[-1]
                ))
        
        return patterns
    
    def analyze(self, symbol: str, prices: List[float]) -> List[Pattern]:
        """Analyze price data for all patterns"""
        if len(prices) < 30:
            return []
        
        maxima, minima = self.find_local_extrema(prices)
        patterns = []
        
        # Detect individual patterns
        double_top = self.detect_double_top(prices, maxima)
        if double_top:
            double_top.symbol = symbol
            if double_top.confidence >= self.confidence_threshold:
                patterns.append(double_top)
        
        double_bottom = self.detect_double_bottom(prices, minima)
        if double_bottom:
            double_bottom.symbol = symbol
            if double_bottom.confidence >= self.confidence_threshold:
                patterns.append(double_bottom)
        
        hns = self.detect_head_and_shoulders(prices, maxima, minima)
        if hns:
            hns.symbol = symbol
            if hns.confidence >= self.confidence_threshold:
                patterns.append(hns)
        
        triangles = self.detect_triangles(prices, maxima, minima)
        for tri in triangles:
            tri.symbol = symbol
            patterns.append(tri)
        
        self.patterns = patterns
        return patterns
    
    def get_pattern_summary(self) -> Dict:
        """Get summary of detected patterns"""
        by_type = {}
        for p in self.patterns:
            pattern_name = p.type.value
            if pattern_name not in by_type:
                by_type[pattern_name] = []
            by_type[pattern_name].append({
                'symbol': p.symbol,
                'confidence': p.confidence,
                'price_target': p.price_target,
                'stop_loss': p.stop_loss
            })
        
        return {
            'total_patterns': len(self.patterns),
            'by_type': by_type
        }
