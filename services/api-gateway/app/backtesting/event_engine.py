"""Event-Driven Backtesting Engine"""
import pandas as pd
import numpy as np
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class EventType(Enum):
    MARKET = "market"
    SIGNAL = "signal"
    ORDER = "order"
    FILL = "fill"

@dataclass
class Event:
    type: EventType
    timestamp: datetime
    data: Dict

class EventEngine:
    """Event-driven backtesting engine with realistic execution"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, float] = {}
        self.trades: List[Dict] = []
        self.events: List[Event] = []
        self.current_time = None
        
    def run_backtest(self, data: pd.DataFrame, strategy: Callable) -> Dict:
        """Run event-driven backtest"""
        for timestamp, row in data.iterrows():
            self.current_time = timestamp
            
            # Create market event
            market_event = Event(EventType.MARKET, timestamp, dict(row))
            self.events.append(market_event)
            
            # Generate signals
            signals = strategy(market_event, self.positions, self.cash)
            
            for signal in signals:
                signal_event = Event(EventType.SIGNAL, timestamp, signal)
                self.events.append(signal_event)
                self._process_signal(signal_event)
        
        return self._calculate_performance()
    
    def _process_signal(self, event: Event):
        """Process trading signal"""
        signal = event.data
        ticker = signal.get('ticker')
        action = signal.get('action')
        quantity = signal.get('quantity')
        price = signal.get('price')
        
        if action == 'BUY':
            cost = quantity * price
            if cost <= self.cash:
                self.cash -= cost
                self.positions[ticker] = self.positions.get(ticker, 0) + quantity
                self.trades.append({
                    'timestamp': event.timestamp,
                    'ticker': ticker,
                    'action': 'BUY',
                    'quantity': quantity,
                    'price': price,
                    'cost': cost
                })
        
        elif action == 'SELL':
            current = self.positions.get(ticker, 0)
            if current >= quantity:
                proceeds = quantity * price
                self.cash += proceeds
                self.positions[ticker] -= quantity
                self.trades.append({
                    'timestamp': event.timestamp,
                    'ticker': ticker,
                    'action': 'SELL',
                    'quantity': quantity,
                    'price': price,
                    'proceeds': proceeds
                })
    
    def _calculate_performance(self) -> Dict:
        """Calculate backtest performance metrics"""
        if not self.trades:
            return {'error': 'No trades executed'}
        
        # Calculate returns
        final_value = self.cash + sum(
            self.positions.get(t, 0) * self.trades[-1].get('price', 0) 
            for t in self.positions
        )
        
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Calculate daily returns for Sharpe
        daily_returns = self._calculate_daily_returns()
        
        sharpe = 0
        if len(daily_returns) > 1:
            sharpe = np.mean(daily_returns) / (np.std(daily_returns) + 1e-8) * np.sqrt(252)
        
        # Max drawdown
        drawdown = self._calculate_drawdown()
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': round(final_value, 2),
            'total_return_pct': round(total_return * 100, 2),
            'sharpe_ratio': round(sharpe, 2),
            'max_drawdown_pct': round(drawdown * 100, 2),
            'total_trades': len(self.trades),
            'win_rate': self._calculate_win_rate(),
            'positions': self.positions,
            'cash': round(self.cash, 2)
        }
    
    def _calculate_daily_returns(self) -> List[float]:
        """Calculate daily returns from trades"""
        if not self.trades:
            return []
        
        # Group by day
        daily_values = {}
        for trade in self.trades:
            day = trade['timestamp'].date()
            daily_values[day] = daily_values.get(day, 0) + trade.get('cost', 0) + trade.get('proceeds', 0)
        
        returns = []
        prev_value = self.initial_capital
        for day, value in sorted(daily_values.items()):
            ret = (value - prev_value) / prev_value if prev_value > 0 else 0
            returns.append(ret)
            prev_value = value
        
        return returns
    
    def _calculate_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.trades:
            return 0
        
        values = [self.initial_capital]
        current = self.initial_capital
        
        for trade in self.trades:
            if 'cost' in trade:
                current -= trade['cost']
            if 'proceeds' in trade:
                current += trade['proceeds']
            values.append(current)
        
        peak = values[0]
        max_dd = 0
        
        for v in values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def _calculate_win_rate(self) -> float:
        """Calculate percentage of winning trades"""
        if not self.trades:
            return 0
        
        wins = sum(1 for t in self.trades if t.get('proceeds', 0) > t.get('cost', 0))
        return round(wins / len(self.trades) * 100, 2)

# Example strategies
def mean_reversion_strategy(event: Event, positions: Dict, cash: float) -> List[Dict]:
    """Simple mean reversion strategy"""
    data = event.data
    price = data.get('close')
    ticker = data.get('ticker', 'SPY')
    
    # Simple logic: buy when price below 20-day MA
    signals = []
    if price and data.get('sma20') and price < data.get('sma20') * 0.95:
        signals.append({
            'ticker': ticker,
            'action': 'BUY',
            'quantity': 10,
            'price': price
        })
    elif price and data.get('sma20') and price > data.get('sma20') * 1.05:
        if positions.get(ticker, 0) > 0:
            signals.append({
                'ticker': ticker,
                'action': 'SELL',
                'quantity': positions[ticker],
                'price': price
            })
    
    return signals

# Quick usage
def run_quick_backtest(data: pd.DataFrame) -> Dict:
    """Run quick backtest with mean reversion"""
    engine = EventEngine(initial_capital=100000)
    return engine.run_backtest(data, mean_reversion_strategy)
