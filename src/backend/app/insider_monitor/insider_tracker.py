"""Insider Trading Monitor - Track SEC Form 4 filings"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

@dataclass
class InsiderTrade:
    ticker: str
    insider_name: str
    insider_title: str
    transaction_type: str  # 'P' = Purchase, 'S' = Sale
    shares: int
    price: float
    transaction_date: datetime

class InsiderMonitor:
    """Monitor and analyze insider trading activity"""
    
    def __init__(self):
        self.trades: Dict[str, List[InsiderTrade]] = defaultdict(list)
    
    def add_trade(self, trade: InsiderTrade):
        self.trades[trade.ticker].append(trade)
    
    def analyze_cluster_buying(self, ticker: str, days: int = 30) -> Dict:
        """Detect cluster buying (multiple insiders buying)"""
        if ticker not in self.trades:
            return {}
        
        cutoff = datetime.now() - timedelta(days=days)
        recent_purchases = [t for t in self.trades[ticker] 
                          if t.transaction_type == 'P' and t.transaction_date >= cutoff]
        
        unique_insiders = set(t.insider_name for t in recent_purchases)
        
        if len(unique_insiders) < 3:
            return {}
        
        total_value = sum(t.shares * t.price for t in recent_purchases)
        
        return {
            'signal': 'CLUSTER_BUYING',
            'ticker': ticker,
            'unique_insiders': len(unique_insiders),
            'total_value': round(total_value, 2),
            'confidence': min(len(unique_insiders) / 5, 1.0),
            'interpretation': 'Bullish' if len(unique_insiders) >= 3 else 'Neutral'
        }
    
    def get_buy_sell_ratio(self, ticker: str, days: int = 90) -> Dict:
        """Calculate insider buy/sell ratio"""
        if ticker not in self.trades:
            return {}
        
        cutoff = datetime.now() - timedelta(days=days)
        recent_trades = [t for t in self.trades[ticker] if t.transaction_date >= cutoff]
        
        buy_value = sum(t.shares * t.price for t in recent_trades if t.transaction_type == 'P')
        sell_value = sum(t.shares * t.price for t in recent_trades if t.transaction_type == 'S')
        
        ratio = buy_value / sell_value if sell_value > 0 else float('inf')
        
        return {
            'ticker': ticker,
            'buy_value': round(buy_value, 2),
            'sell_value': round(sell_value, 2),
            'ratio': round(ratio, 2) if ratio != float('inf') else 'Infinite',
            'signal': 'BULLISH' if buy_value > sell_value * 1.5 else 'BEARISH' if sell_value > buy_value * 1.5 else 'NEUTRAL'
        }

# Usage
def check_insider_signals(ticker: str) -> Dict:
    monitor = InsiderMonitor()
    return monitor.analyze_cluster_buying(ticker)
