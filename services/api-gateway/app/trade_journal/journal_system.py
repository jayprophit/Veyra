"""
Trade Journal System
====================
Track trades, performance metrics, psychological factors
Analyze win/loss patterns, optimize strategy
"""
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import pandas as pd
import numpy as np


class TradeOutcome(Enum):
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"


class TradeType(Enum):
    LONG = "long"
    SHORT = "short"
    OPTIONS_CALL = "call"
    OPTIONS_PUT = "put"


@dataclass
class TradeEntry:
    """Trade journal entry"""
    id: str
    date_entry: datetime
    date_exit: Optional[datetime] = None
    ticker: str = ""
    trade_type: str = ""
    entry_price: float = 0
    exit_price: float = 0
    shares: int = 0
    position_size: float = 0
    stop_loss: float = 0
    target_price: float = 0
    pnl: float = 0
    pnl_pct: float = 0
    outcome: str = ""
    strategy: str = ""
    setup: str = ""
    entry_reason: str = ""
    exit_reason: str = ""
    market_condition: str = ""
    emotions: str = ""
    mistakes: str = ""
    lessons: str = ""
    rating: int = 0  # 1-10
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TradeJournal:
    """
    Comprehensive trade journaling system
    
    Features:
    - Trade entry/exit tracking
    - Performance analytics
    - Strategy analysis
    - Psychological tracking
    """
    
    def __init__(self, filename: str = "trade_journal.json"):
        self.filename = filename
        self.trades: List[TradeEntry] = []
        self.load_journal()
    
    def load_journal(self):
        """Load existing journal from file"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for trade_dict in data:
                    trade_dict['date_entry'] = datetime.fromisoformat(trade_dict['date_entry'])
                    if trade_dict.get('date_exit'):
                        trade_dict['date_exit'] = datetime.fromisoformat(trade_dict['date_exit'])
                    self.trades.append(TradeEntry(**trade_dict))
        except FileNotFoundError:
            pass
    
    def save_journal(self):
        """Save journal to file"""
        data = []
        for trade in self.trades:
            trade_dict = asdict(trade)
            trade_dict['date_entry'] = trade.date_entry.isoformat()
            if trade.date_exit:
                trade_dict['date_exit'] = trade.date_exit.isoformat()
            data.append(trade_dict)
        
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_trade(self, trade: TradeEntry):
        """Add new trade to journal"""
        self.trades.append(trade)
        self.save_journal()
    
    def close_trade(self, trade_id: str, exit_price: float, 
                   exit_date: datetime, exit_reason: str):
        """Close an open trade"""
        for trade in self.trades:
            if trade.id == trade_id and not trade.date_exit:
                trade.exit_price = exit_price
                trade.date_exit = exit_date
                trade.exit_reason = exit_reason
                
                # Calculate P&L
                if trade.trade_type == 'long':
                    trade.pnl = (exit_price - trade.entry_price) * trade.shares
                else:
                    trade.pnl = (trade.entry_price - exit_price) * trade.shares
                
                trade.pnl_pct = (trade.pnl / trade.position_size) * 100
                
                # Determine outcome
                if trade.pnl > 0:
                    trade.outcome = TradeOutcome.WIN.value
                elif trade.pnl < 0:
                    trade.outcome = TradeOutcome.LOSS.value
                else:
                    trade.outcome = TradeOutcome.BREAKEVEN.value
                
                self.save_journal()
                return trade
        
        return None
    
    def get_performance_metrics(self) -> Dict:
        """Calculate trading performance metrics"""
        if not self.trades:
            return {}
        
        closed_trades = [t for t in self.trades if t.date_exit]
        
        if not closed_trades:
            return {}
        
        wins = [t for t in closed_trades if t.outcome == TradeOutcome.WIN.value]
        losses = [t for t in closed_trades if t.outcome == TradeOutcome.LOSS.value]
        
        total_trades = len(closed_trades)
        win_rate = len(wins) / total_trades if total_trades > 0 else 0
        
        total_pnl = sum(t.pnl for t in closed_trades)
        
        avg_win = np.mean([t.pnl for t in wins]) if wins else 0
        avg_loss = np.mean([t.pnl for t in losses]) if losses else 0
        
        win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Profit factor
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Expectancy
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * abs(avg_loss))
        
        return {
            'total_trades': total_trades,
            'win_rate': round(win_rate * 100, 2),
            'total_pnl': round(total_pnl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'win_loss_ratio': round(win_loss_ratio, 2),
            'profit_factor': round(profit_factor, 2),
            'expectancy_per_trade': round(expectancy, 2),
            'largest_win': round(max([t.pnl for t in wins]) if wins else 0, 2),
            'largest_loss': round(min([t.pnl for t in losses]) if losses else 0, 2)
        }
    
    def analyze_by_strategy(self) -> Dict[str, Dict]:
        """Analyze performance by strategy"""
        if not self.trades:
            return {}
        
        closed_trades = [t for t in self.trades if t.date_exit]
        
        strategies = {}
        for trade in closed_trades:
            strat = trade.strategy
            if strat not in strategies:
                strategies[strat] = []
            strategies[strat].append(trade)
        
        analysis = {}
        for strat, trades in strategies.items():
            wins = [t for t in trades if t.outcome == TradeOutcome.WIN.value]
            
            analysis[strat] = {
                'total_trades': len(trades),
                'win_rate': round(len(wins) / len(trades) * 100, 2) if trades else 0,
                'total_pnl': round(sum(t.pnl for t in trades), 2),
                'avg_pnl': round(np.mean([t.pnl for t in trades]), 2) if trades else 0
            }
        
        return analysis
    
    def get_recent_trades(self, n: int = 10) -> List[TradeEntry]:
        """Get n most recent trades"""
        sorted_trades = sorted(
            self.trades,
            key=lambda x: x.date_entry,
            reverse=True
        )
        return sorted_trades[:n]
    
    def get_open_trades(self) -> List[TradeEntry]:
        """Get all open trades"""
        return [t for t in self.trades if not t.date_exit]
    
    def get_trade_history_df(self) -> pd.DataFrame:
        """Get trade history as DataFrame"""
        if not self.trades:
            return pd.DataFrame()
        
        data = []
        for trade in self.trades:
            data.append({
                'id': trade.id,
                'date': trade.date_entry.strftime('%Y-%m-%d'),
                'ticker': trade.ticker,
                'type': trade.trade_type,
                'entry': trade.entry_price,
                'exit': trade.exit_price,
                'pnl': trade.pnl,
                'pnl_pct': trade.pnl_pct,
                'outcome': trade.outcome,
                'strategy': trade.strategy
            })
        
        return pd.DataFrame(data)


# Usage
def create_trade_entry(ticker: str, entry_price: float, 
                      shares: int, strategy: str) -> TradeEntry:
    """Create new trade entry"""
    return TradeEntry(
        id=f"{ticker}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        date_entry=datetime.now(),
        ticker=ticker,
        trade_type='long',
        entry_price=entry_price,
        shares=shares,
        position_size=entry_price * shares,
        strategy=strategy,
        rating=5
    )


def get_performance_summary(journal: TradeJournal) -> Dict:
    """Quick performance summary"""
    return journal.get_performance_metrics()
