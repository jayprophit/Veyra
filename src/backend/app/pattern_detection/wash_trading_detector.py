"""Wash Trading Detector - Detect wash trading patterns"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

@dataclass
class Trade:
    trade_id: str
    symbol: str
    buyer_id: str
    seller_id: str
    shares: int
    price: float
    timestamp: datetime

class WashTradingDetector:
    def __init__(self, volume_threshold: float = 0.1):
        self.trades: List[Trade] = []
        self.volume_threshold = volume_threshold
    
    def add(self, t: Trade):
        self.trades.append(t)
    
    def detect_suspicious_patterns(self) -> List[Dict]:
        """Detect potential wash trades"""
        suspicious = []
        
        for t in self.trades:
            if t.buyer_id == t.seller_id:
                suspicious.append({
                    'trade_id': t.trade_id,
                    'symbol': t.symbol,
                    'type': 'self_trade',
                    'shares': t.shares,
                    'timestamp': t.timestamp
                })
        
        return suspicious
    
    def get_summary(self) -> Dict:
        if not self.trades:
            return {'status': 'NO_TRADES'}
        
        suspicious = self.detect_suspicious_patterns()
        total_volume = sum(t.shares for t in self.trades)
        suspicious_volume = sum(s['shares'] for s in suspicious)
        
        return {
            'total_trades': len(self.trades),
            'suspicious_trades': len(suspicious),
            'suspicious_pct': round(len(suspicious) / len(self.trades) * 100, 2),
            'suspicious_volume_pct': round(suspicious_volume / total_volume * 100, 2) if total_volume else 0
        }
