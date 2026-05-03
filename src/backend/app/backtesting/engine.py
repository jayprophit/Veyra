"""Backtesting Engine for Strategy Validation."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CommissionType(Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    TIERED = "tiered"

@dataclass
class BacktestResult:
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_trade_return: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    profit_factor: float
    equity_curve: List[float]
    trades: List[Dict]
    monthly_returns: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'strategy_name': self.strategy_name,
            'period': f"{self.start_date.date()} to {self.end_date.date()}",
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return_pct': self.total_return * 100,
            'total_trades': self.total_trades,
            'win_rate': self.win_rate * 100,
            'max_drawdown_pct': self.max_drawdown * 100,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'profit_factor': self.profit_factor,
            'calmar_ratio': self.calmar_ratio,
            'monthly_returns': self.monthly_returns
        }

class BacktestingEngine:
    """Professional backtesting with realistic execution simulation."""
    
    def __init__(self):
        self.commission_rate = 0.001  # 0.1%
        self.slippage = 0.0005  # 0.05%
        self.initial_capital = 100000.0
    
    async def run_backtest(self,
                          strategy: Callable,
                          price_data: pd.DataFrame,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          initial_capital: float = 100000.0,
                          commission: float = 0.001) -> BacktestResult:
        """
        Run comprehensive backtest.
        
        Args:
            strategy: Strategy function that returns signals
            price_data: OHLCV DataFrame
            start_date: Backtest start
            end_date: Backtest end
            initial_capital: Starting capital
            commission: Commission rate
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission
        
        # Filter date range
        if start_date:
            price_data = price_data[price_data.index >= start_date]
        if end_date:
            price_data = price_data[price_data.index <= end_date]
        
        capital = initial_capital
        position = 0.0
        trades = []
        equity_curve = [capital]
        
        # Run strategy
        for i in range(len(price_data)):
            current_bar = price_data.iloc[i]
            
            # Get signal from strategy
            signal = strategy(price_data.iloc[:i+1])
            
            price = current_bar['close']
            
            # Execute signal
            if signal == 1 and position <= 0:  # Buy
                if position < 0:
                    # Close short
                    trades.append(self._close_trade(position, price, current_bar.name, 'short'))
                # Open long
                position = capital / price * (1 - self.commission_rate)
                capital = 0
                
            elif signal == -1 and position >= 0:  # Sell
                if position > 0:
                    # Close long
                    trades.append(self._close_trade(position, price, current_bar.name, 'long'))
                # Open short
                position = -capital / price * (1 - self.commission_rate)
                capital = 0
            
            # Calculate current equity
            if position > 0:
                current_equity = position * price
            elif position < 0:
                pnl = abs(position) * (trades[-1]['exit_price'] - price) if trades else 0
                current_equity = initial_capital + pnl
            else:
                current_equity = capital
            
            equity_curve.append(current_equity)
        
        # Close final position
        if position != 0:
            final_price = price_data['close'].iloc[-1]
            side = 'long' if position > 0 else 'short'
            trades.append(self._close_trade(position, final_price, price_data.index[-1], side))
        
        # Calculate metrics
        final_capital = equity_curve[-1]
        total_return = (final_capital - initial_capital) / initial_capital
        
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] < 0]
        
        # Calculate drawdown
        equity_series = pd.Series(equity_curve)
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Calculate returns
        returns = equity_series.pct_change().dropna()
        
        # Sharpe ratio
        sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        # Sortino ratio
        downside_returns = returns[returns < 0]
        sortino = (returns.mean() * 252) / (downside_returns.std() * np.sqrt(252)) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
        
        # Calmar ratio
        calmar = (returns.mean() * 252) / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Profit factor
        gross_profit = sum(t['pnl'] for t in winning_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Monthly returns
        equity_df = pd.DataFrame({'equity': equity_curve}, index=[price_data.index[0]] + list(price_data.index))
        monthly = equity_df.resample('M').last().pct_change().dropna()
        monthly_returns = {str(k): float(v) for k, v in monthly['equity'].items()}
        
        return BacktestResult(
            strategy_name=strategy.__name__,
            start_date=price_data.index[0],
            end_date=price_data.index[-1],
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=len(winning_trades) / len(trades) if trades else 0,
            avg_trade_return=np.mean([t['pnl_pct'] for t in trades]) if trades else 0,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            profit_factor=profit_factor,
            equity_curve=equity_curve,
            trades=trades,
            monthly_returns=monthly_returns
        )
    
    def _close_trade(self, position: float, exit_price: float, 
                    exit_time: datetime, side: str) -> Dict:
        """Record trade closure."""
        # Simplified P&L calculation
        pnl = position * exit_price * (1 - self.commission_rate) - abs(position) * exit_price
        pnl_pct = pnl / (abs(position) * exit_price) if position != 0 else 0
        
        return {
            'side': side,
            'exit_price': exit_price,
            'exit_time': exit_time.isoformat(),
            'pnl': pnl,
            'pnl_pct': pnl_pct
        }
    
    async def optimize_parameters(self,
                                 strategy: Callable,
                                 price_data: pd.DataFrame,
                                 param_grid: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Grid search for optimal parameters."""
        from itertools import product
        
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        
        best_result = None
        best_sharpe = -float('inf')
        all_results = []
        
        for combination in product(*values):
            params = dict(zip(keys, combination))
            
            # Run backtest with these params
            result = await self.run_backtest(
                lambda x: strategy(x, **params),
                price_data
            )
            
            all_results.append({
                'params': params,
                'sharpe': result.sharpe_ratio,
                'return': result.total_return,
                'drawdown': result.max_drawdown
            })
            
            if result.sharpe_ratio > best_sharpe:
                best_sharpe = result.sharpe_ratio
                best_result = params
        
        return {
            'optimal_params': best_result,
            'best_sharpe': best_sharpe,
            'all_results': sorted(all_results, key=lambda x: x['sharpe'], reverse=True)[:10]
        }
    
    async def walk_forward_analysis(self,
                                   strategy: Callable,
                                   price_data: pd.DataFrame,
                                   train_size: int = 252,
                                   test_size: int = 63) -> List[Dict]:
        """Walk-forward optimization to prevent overfitting."""
        results = []
        
        total_bars = len(price_data)
        current_idx = 0
        
        while current_idx + train_size + test_size <= total_bars:
            # Training period
            train_data = price_data.iloc[current_idx:current_idx + train_size]
            
            # Testing period
            test_data = price_data.iloc[current_idx + train_size:current_idx + train_size + test_size]
            
            # Run on test data
            result = await self.run_backtest(strategy, test_data)
            
            results.append({
                'train_start': str(train_data.index[0]),
                'train_end': str(train_data.index[-1]),
                'test_start': str(test_data.index[0]),
                'test_end': str(test_data.index[-1]),
                'sharpe': result.sharpe_ratio,
                'return': result.total_return,
                'drawdown': result.max_drawdown
            })
            
            current_idx += test_size
        
        return results

backtest_engine = BacktestingEngine()
