"""Visual Trading Signals - Trading signals from visual data"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TradingSignal:
    signal_id: str
    symbol: str
    signal_type: str
    strength: float

class VisualTradingSignals:
    def __init__(self):
        self.signals: List[TradingSignal] = []
    
    def add(self, s: TradingSignal):
        self.signals.append(s)
    
    def get_summary(self) -> Dict:
        return {'signals': len(self.signals), 'avg_strength': round(sum(s.strength for s in self.signals) / len(self.signals), 2) if self.signals else 0}
