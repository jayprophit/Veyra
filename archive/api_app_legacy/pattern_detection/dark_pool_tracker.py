"""Dark Pool Tracker - Monitor dark pool trading activity"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

@dataclass
class DarkPoolTrade:
    trade_id: str
    symbol: str
    shares: int
    price: float
    timestamp: datetime
    venue: str
    side: str  # 'buy', 'sell'

class DarkPoolTracker:
    def __init__(self):
        self.trades: List[DarkPoolTrade] = []
    
    def add(self, t: DarkPoolTrade):
        self.trades.append(t)
    
    def get_by_symbol(self, symbol: str) -> List[DarkPoolTrade]:
        return [t for t in self.trades if t.symbol == symbol]
    
    def calculate_volume_imbalance(self, symbol: str) -> Dict:
        symbol_trades = self.get_by_symbol(symbol)
        buy_vol = sum(t.shares for t in symbol_trades if t.side == 'buy')
        sell_vol = sum(t.shares for t in symbol_trades if t.side == 'sell')
        total = buy_vol + sell_vol
        
        return {
            'symbol': symbol,
            'buy_volume': buy_vol,
            'sell_volume': sell_vol,
            'total_volume': total,
            'imbalance_pct': round((buy_vol - sell_vol) / total * 100, 1) if total else 0
        }
    
    def get_summary(self) -> Dict:
        if not self.trades:
            return {'status': 'NO_TRADES'}
        
        by_symbol = {}
        for t in self.trades:
            s = t.symbol
            if s not in by_symbol:
                by_symbol[s] = {'trades': 0, 'volume': 0}
            by_symbol[s]['trades'] += 1
            by_symbol[s]['volume'] += t.shares
        
        return {
            'total_trades': len(self.trades),
            'total_volume': sum(t.shares for t in self.trades),
            'by_symbol': by_symbol
        }
