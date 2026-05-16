"""Pattern Recognition"""
import numpy as np
import pandas as pd
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum

class PatternType(Enum):
    HNS = "head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIANGLE = "triangle"

@dataclass
class Pattern:
    type: PatternType
    symbol: str
    confidence: float
    price_target: float
    stop: float

class PatternRecognizer:
    """Technical pattern recognition"""
    
    def detect(self, symbol: str, data: pd.DataFrame) -> List[Pattern]:
        """Detect chart patterns"""
        patterns = []
        highs = data['high'].values
        lows = data['low'].values
        
        # Double top detection
        if len(highs) > 20:
            recent_highs = highs[-20:]
            peaks = self._find_peaks(recent_highs)
            if len(peaks) >= 2:
                if abs(recent_highs[peaks[0]] - recent_highs[peaks[1]]) / recent_highs[peaks[0]] < 0.02:
                    patterns.append(Pattern(
                        PatternType.DOUBLE_TOP,
                        symbol,
                        0.75,
                        recent_highs[peaks[0]] * 0.95,
                        recent_highs[peaks[0]] * 1.02
                    ))
        
        return patterns
    
    def _find_peaks(self, arr: np.ndarray, order: int = 3) -> List[int]:
        """Find local maxima"""
        from scipy.signal import argrelextrema
        return argrelextrema(arr, np.greater, order=order)[0].tolist()
