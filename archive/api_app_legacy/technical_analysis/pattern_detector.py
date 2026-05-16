"""Chart Pattern Detector - Detect technical chart patterns"""
from typing import Dict, List, Tuple, Optional
import statistics

class ChartPatternDetector:
    """Detect common chart patterns in price data"""
    
    def __init__(self):
        self.patterns = [
            "head_and_shoulders",
            "inverse_head_and_shoulders",
            "double_top",
            "double_bottom",
            "ascending_triangle",
            "descending_triangle",
            "symmetrical_triangle",
            "bull_flag",
            "bear_flag",
            "cup_and_handle"
        ]
    
    def detect_head_and_shoulders(self, highs: List[float], 
                                   lows: List[float]) -> Optional[Dict]:
        """Detect Head and Shoulders pattern"""
        if len(highs) < 20:
            return None
        
        # Look for three peaks: left shoulder, head, right shoulder
        # Head should be highest, shoulders roughly equal
        
        recent_highs = highs[-20:]
        recent_lows = lows[-20:]
        
        # Find local maxima
        peaks = []
        for i in range(2, len(recent_highs) - 2):
            if (recent_highs[i] > recent_highs[i-1] and 
                recent_highs[i] > recent_highs[i-2] and
                recent_highs[i] > recent_highs[i+1] and
                recent_highs[i] > recent_highs[i+2]):
                peaks.append((i, recent_highs[i]))
        
        if len(peaks) < 3:
            return None
        
        # Check if middle peak is highest (head)
        for i in range(len(peaks) - 2):
            left_idx, left_shoulder = peaks[i]
            head_idx, head = peaks[i+1]
            right_idx, right_shoulder = peaks[i+2]
            
            # Head should be higher than both shoulders
            if head > left_shoulder and head > right_shoulder:
                # Shoulders should be roughly equal (within 5%)
                shoulder_diff = abs(left_shoulder - right_shoulder) / left_shoulder
                
                if shoulder_diff < 0.05:
                    # Find neckline
                    neckline = max(recent_lows[left_idx:right_idx])
                    
                    return {
                        "pattern": "HEAD_AND_SHOULDERS",
                        "confidence": round((1 - shoulder_diff) * 100, 1),
                        "neckline": neckline,
                        "target": head - (head - neckline),
                        "direction": "BEARISH",
                        "breakout_needed": True
                    }
        
        return None
    
    def detect_double_top(self, highs: List[float], 
                         lows: List[float]) -> Optional[Dict]:
        """Detect Double Top pattern"""
        if len(highs) < 15:
            return None
        
        recent_highs = highs[-15:]
        recent_lows = lows[-15:]
        
        # Find two peaks at similar level
        peaks = []
        for i in range(2, len(recent_highs) - 2):
            if (recent_highs[i] > recent_highs[i-1] and 
                recent_highs[i] > recent_highs[i+1]):
                peaks.append((i, recent_highs[i]))
        
        if len(peaks) < 2:
            return None
        
        # Check for similar peaks
        for i in range(len(peaks) - 1):
            peak1_idx, peak1 = peaks[i]
            peak2_idx, peak2 = peaks[i+1]
            
            diff = abs(peak1 - peak2) / peak1
            
            # Peaks within 3%, with valley between
            if diff < 0.03 and peak2_idx - peak1_idx > 3:
                # Find valley between
                valley = min(recent_lows[peak1_idx:peak2_idx])
                
                return {
                    "pattern": "DOUBLE_TOP",
                    "confidence": round((1 - diff) * 100, 1),
                    "neckline": valley,
                    "target": valley - (peak1 - valley),
                    "direction": "BEARISH"
                }
        
        return None
    
    def detect_double_bottom(self, highs: List[float], 
                            lows: List[float]) -> Optional[Dict]:
        """Detect Double Bottom pattern"""
        if len(lows) < 15:
            return None
        
        recent_lows = lows[-15:]
        recent_highs = highs[-15:]
        
        # Find two troughs at similar level
        troughs = []
        for i in range(2, len(recent_lows) - 2):
            if (recent_lows[i] < recent_lows[i-1] and 
                recent_lows[i] < recent_lows[i+1]):
                troughs.append((i, recent_lows[i]))
        
        if len(troughs) < 2:
            return None
        
        for i in range(len(troughs) - 1):
            trough1_idx, trough1 = troughs[i]
            trough2_idx, trough2 = troughs[i+1]
            
            diff = abs(trough1 - trough2) / trough1
            
            if diff < 0.03 and trough2_idx - trough1_idx > 3:
                # Find peak between
                peak = max(recent_highs[trough1_idx:trough2_idx])
                
                return {
                    "pattern": "DOUBLE_BOTTOM",
                    "confidence": round((1 - diff) * 100, 1),
                    "neckline": peak,
                    "target": peak + (peak - trough1),
                    "direction": "BULLISH"
                }
        
        return None
    
    def detect_triangle(self, highs: List[float], 
                       lows: List[float]) -> Optional[Dict]:
        """Detect triangle patterns"""
        if len(highs) < 15:
            return None
        
        recent_highs = highs[-15:]
        recent_lows = lows[-15:]
        
        # Check for converging trendlines
        high_slope = self._calculate_slope(recent_highs)
        low_slope = self._calculate_slope(recent_lows)
        
        # Ascending triangle: flat top, rising bottom
        if abs(high_slope) < 0.001 and low_slope > 0.001:
            return {
                "pattern": "ASCENDING_TRIANGLE",
                "confidence": 75,
                "direction": "BULLISH",
                "breakout_target": recent_highs[-1] + (recent_highs[-1] - recent_lows[0])
            }
        
        # Descending triangle: falling top, flat bottom
        if high_slope < -0.001 and abs(low_slope) < 0.001:
            return {
                "pattern": "DESCENDING_TRIANGLE",
                "confidence": 75,
                "direction": "BEARISH",
                "breakout_target": recent_lows[-1] - (recent_highs[0] - recent_lows[-1])
            }
        
        # Symmetrical triangle: converging
        if high_slope < -0.001 and low_slope > 0.001:
            return {
                "pattern": "SYMMETRICAL_TRIANGLE",
                "confidence": 70,
                "direction": "UNKNOWN",
                "breakout_target": "Measure height of pattern"
            }
        
        return None
    
    def _calculate_slope(self, data: List[float]) -> float:
        """Calculate slope using linear regression"""
        n = len(data)
        if n < 2:
            return 0
        
        x = list(range(n))
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(data)
        
        numerator = sum((x[i] - mean_x) * (data[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0
    
    def scan_all_patterns(self, symbol: str, highs: List[float], 
                         lows: List[float], closes: List[float]) -> List[Dict]:
        """Scan for all patterns"""
        patterns = []
        
        # Check each pattern
        hs = self.detect_head_and_shoulders(highs, lows)
        if hs:
            patterns.append({**hs, "symbol": symbol})
        
        dt = self.detect_double_top(highs, lows)
        if dt:
            patterns.append({**dt, "symbol": symbol})
        
        db = self.detect_double_bottom(highs, lows)
        if db:
            patterns.append({**db, "symbol": symbol})
        
        tri = self.detect_triangle(highs, lows)
        if tri:
            patterns.append({**tri, "symbol": symbol})
        
        return sorted(patterns, key=lambda x: x.get("confidence", 0), reverse=True)
