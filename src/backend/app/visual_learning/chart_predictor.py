"""Chart Predictor - Predict chart patterns"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ChartPattern:
    pattern_id: str
    symbol: str
    confidence: float

class ChartPredictor:
    def __init__(self):
        self.patterns: List[ChartPattern] = []
    
    def add(self, p: ChartPattern):
        self.patterns.append(p)
    
    def get_summary(self) -> Dict:
        return {'patterns': len(self.patterns), 'avg_confidence': round(sum(p.confidence for p in self.patterns) / len(self.patterns), 2) if self.patterns else 0}
