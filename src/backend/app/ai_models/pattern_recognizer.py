"""Pattern Recognizer - AI pattern detection in market data"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class PatternType(Enum):
    HEAD_SHOULDERS = "head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIANGLE = "triangle"
    FLAG = "flag"
    CUP_HANDLE = "cup_and_handle"

@dataclass
class PatternMatch:
    pattern_type: PatternType
    symbol: str
    confidence: float
    start_idx: int
    end_idx: int
    target_price: Optional[float] = None

class PatternRecognizer:
    def __init__(self):
        self.patterns: List[PatternMatch] = []
    
    def detect_pattern(self, prices: List[float], symbol: str) -> List[PatternMatch]:
        """Detect patterns in price series"""
        detected = []
        if len(prices) < 20:
            return detected
        
        # Simple detection logic
        for i in range(10, len(prices) - 10):
            local_max = max(prices[i-5:i+5])
            local_min = min(prices[i-5:i+5])
            
            if prices[i] == local_max:
                # Potential peak
                confidence = 0.6
                detected.append(PatternMatch(
                    PatternType.DOUBLE_TOP, symbol, confidence, i-5, i+5
                ))
        
        self.patterns.extend(detected)
        return detected
    
    def get_summary(self) -> Dict:
        if not self.patterns:
            return {'status': 'NO_PATTERNS'}
        by_type = {}
        for p in self.patterns:
            t = p.pattern_type.value
            if t not in by_type:
                by_type[t] = {'count': 0, 'avg_confidence': 0}
            by_type[t]['count'] += 1
            by_type[t]['avg_confidence'] += p.confidence
        
        for t in by_type:
            by_type[t]['avg_confidence'] = round(by_type[t]['avg_confidence'] / by_type[t]['count'], 2)
        
        return {
            'total_patterns': len(self.patterns),
            'by_type': by_type
        }
