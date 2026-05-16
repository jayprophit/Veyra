"""Spread Capture - Simulate market making spread capture strategies"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Quote:
    symbol: str
    bid: float
    ask: float
    bid_size: int
    ask_size: int
    timestamp: datetime

@dataclass
class Trade:
    symbol: str
    price: float
    size: int
    side: str  # buy or sell
    timestamp: datetime

class SpreadCapture:
    """Simulate market making spread capture"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quotes: List[Quote] = []
        self.trades: List[Trade] = []
        self.position = 0
        self.cash = 0.0
        self.total_trades = 0
        self.profitable_trades = 0
    
    def add_quote(self, quote: Quote):
        """Add market quote"""
        self.quotes.append(quote)
    
    def calculate_spread(self, quote: Quote) -> Dict:
        """Calculate bid-ask spread metrics"""
        spread = quote.ask - quote.bid
        spread_pct = (spread / ((quote.bid + quote.ask) / 2)) * 100
        mid_price = (quote.bid + quote.ask) / 2
        
        return {
            "symbol": quote.symbol,
            "bid": quote.bid,
            "ask": quote.ask,
            "spread": round(spread, 4),
            "spread_pct": round(spread_pct, 3),
            "mid_price": round(mid_price, 2),
            "spread_category": "WIDE" if spread_pct > 0.5 else "NORMAL" if spread_pct > 0.1 else "TIGHT"
        }
    
    def simulate_trade(self, side: str, size: int, aggressive: bool = False) -> Dict:
        """Simulate a market making trade"""
        if not self.quotes:
            return {"error": "No quotes available"}
        
        latest = self.quotes[-1]
        
        # Determine execution price
        if aggressive:
            # Hit the bid or lift the offer
            price = latest.ask if side == "buy" else latest.bid
        else:
            # Passive - provide liquidity (assume mid for simulation)
            price = (latest.bid + latest.ask) / 2
        
        # Execute
        if side == "buy":
            self.position += size
            self.cash -= price * size
        else:
            self.position -= size
            self.cash += price * size
        
        trade = Trade(self.symbol, price, size, side, datetime.utcnow())
        self.trades.append(trade)
        self.total_trades += 1
        
        # P&L calculation (mark to mid)
        current_mid = (latest.bid + latest.ask) / 2
        unrealized_pnl = self.position * current_mid + self.cash
        
        return {
            "side": side,
            "price": price,
            "size": size,
            "position": self.position,
            "cash": round(self.cash, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "trade_count": self.total_trades
        }
    
    def calculate_pnl(self) -> Dict:
        """Calculate P&L for market making activity"""
        if not self.quotes:
            return {"error": "No price data"}
        
        current_mid = (self.quotes[-1].bid + self.quotes[-1].ask) / 2
        
        # Mark to market
        position_value = self.position * current_mid
        total_value = self.cash + position_value
        
        # Calculate spread capture
        realized_pnl = 0
        for i, trade in enumerate(self.trades[:-1]):
            if trade.side == "buy":
                # Look for matching sell
                for j in range(i + 1, len(self.trades)):
                    if self.trades[j].side == "sell":
                        realized_pnl += (self.trades[j].price - trade.price) * min(trade.size, self.trades[j].size)
                        break
        
        # Trading statistics
        buy_trades = len([t for t in self.trades if t.side == "buy"])
        sell_trades = len([t for t in self.trades if t.side == "sell"])
        
        # Average spread captured (simplified)
        avg_spread_captured = 0
        if self.total_trades > 0:
            total_spread = sum((q.ask - q.bid) for q in self.quotes) / len(self.quotes)
            avg_spread_captured = total_spread * 0.5  # Assume capture half the spread
        
        return {
            "symbol": self.symbol,
            "final_position": self.position,
            "cash_balance": round(self.cash, 2),
            "position_value": round(position_value, 2),
            "total_value": round(total_value, 2),
            "realized_pnl": round(realized_pnl, 2),
            "unrealized_pnl": round(total_value - sum(t.price * t.size for t in self.trades if t.side == "buy") + sum(t.price * t.size for t in self.trades if t.side == "sell"), 2),
            "total_trades": self.total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "avg_spread_captured": round(avg_spread_captured, 4),
            "trading_performance": "PROFITABLE" if realized_pnl > 0 else "BREAK_EVEN" if realized_pnl == 0 else "LOSS"
        }
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        pnl = self.calculate_pnl()
        
        if "error" in pnl:
            return pnl
        
        # Calculate per-trade metrics
        per_trade_pnl = pnl["realized_pnl"] / self.total_trades if self.total_trades > 0 else 0
        
        # Win rate (trades that captured positive spread)
        # Simplified: assume buys below mid and sells above mid are wins
        wins = 0
        for i in range(0, len(self.trades) - 1, 2):
            if i + 1 < len(self.trades):
                if self.trades[i].side == "buy" and self.trades[i+1].side == "sell":
                    if self.trades[i+1].price > self.trades[i].price:
                        wins += 1
        
        win_rate = (wins / (self.total_trades / 2) * 100) if self.total_trades > 0 else 0
        
        return {
            **pnl,
            "per_trade_pnl": round(per_trade_pnl, 3),
            "win_rate": round(win_rate, 1),
            "sharpe_estimate": "POSITIVE" if pnl["realized_pnl"] > 0 and win_rate > 50 else "NEGATIVE",
            "strategy_assessment": "VIABLE" if pnl["realized_pnl"] > 0 else "NEEDS_IMPROVEMENT"
        }
