"""
Position Sizing Calculator
==========================
Kelly Criterion, Optimal f, Fixed Fractional, Volatility-based sizing
Risk management integrated position sizing
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SizingMethod(Enum):
    KELLY = "kelly_criterion"
    OPTIMAL_F = "optimal_f"
    FIXED_FRACTIONAL = "fixed_fractional"
    FIXED_RATIO = "fixed_ratio"
    VOLATILITY_BASED = "volatility_based"
    RISK_PARITY = "risk_parity"


@dataclass
class SizingResult:
    """Position sizing result"""
    method: str
    position_size_pct: float
    position_size_dollars: float
    max_risk_pct: float
    recommended_shares: int
    reasoning: str


class PositionSizingCalculator:
    """
    Professional position sizing algorithms
    
    Methods:
    - Kelly Criterion: Maximizes expected log wealth
    - Optimal f: Maximizes geometric growth
    - Fixed Fractional: Fixed % risk per trade
    - Volatility-based: ATR or volatility adjusted
    """
    
    def __init__(self, account_value: float = 100000):
        self.account_value = account_value
    
    def kelly_criterion(self, win_rate: float, 
                       avg_win: float, 
                       avg_loss: float) -> SizingResult:
        """
        Kelly Criterion position sizing
        
        f* = (p*b - q) / b
        where:
        p = win rate
        q = loss rate = 1 - p
        b = avg win / avg loss (win/loss ratio)
        """
        if avg_loss == 0:
            return SizingResult(
                method='kelly_criterion',
                position_size_pct=0,
                position_size_dollars=0,
                max_risk_pct=0,
                recommended_shares=0,
                reasoning='Invalid: Average loss is zero'
            )
        
        p = win_rate
        q = 1 - p
        b = avg_win / avg_loss
        
        kelly_pct = (p * b - q) / b
        
        # Half-Kelly for safety (many traders use half or quarter Kelly)
        half_kelly = kelly_pct / 2
        
        # Cap at 25% max position
        safe_pct = min(half_kelly, 0.25)
        
        position_dollars = self.account_value * safe_pct
        
        return SizingResult(
            method='kelly_criterion',
            position_size_pct=round(safe_pct * 100, 2),
            position_size_dollars=round(position_dollars, 2),
            max_risk_pct=round(safe_pct * 0.5 * 100, 2),  # Assume 50% of position at risk
            recommended_shares=0,  # Would need price
            reasoning=f'Win rate: {win_rate:.1%}, W/L ratio: {b:.2f}, Raw Kelly: {kelly_pct:.1%}'
        )
    
    def fixed_fractional(self, risk_per_trade_pct: float = 0.02,
                        entry_price: float = 100,
                        stop_loss: float = 95) -> SizingResult:
        """
        Fixed fractional position sizing
        
        Risk fixed % of account per trade
        """
        risk_dollars = self.account_value * risk_per_trade_pct
        risk_per_share = entry_price - stop_loss
        
        if risk_per_share <= 0:
            return SizingResult(
                method='fixed_fractional',
                position_size_pct=0,
                position_size_dollars=0,
                max_risk_pct=0,
                recommended_shares=0,
                reasoning='Invalid: Stop loss must be below entry'
            )
        
        shares = int(risk_dollars / risk_per_share)
        position_dollars = shares * entry_price
        position_pct = position_dollars / self.account_value
        
        return SizingResult(
            method='fixed_fractional',
            position_size_pct=round(position_pct * 100, 2),
            position_size_dollars=round(position_dollars, 2),
            max_risk_pct=round(risk_per_trade_pct * 100, 2),
            recommended_shares=shares,
            reasoning=f'Risking {risk_per_trade_pct:.1%} per trade, ${risk_dollars:.0f} risk'
        )
    
    def volatility_based(self, atr: float,
                        entry_price: float,
                        risk_multiple: float = 2.0,
                        risk_per_trade_pct: float = 0.02) -> SizingResult:
        """
        Volatility-based position sizing using ATR
        
        Position size = (Account Risk $) / (ATR * Risk Multiple)
        """
        risk_dollars = self.account_value * risk_per_trade_pct
        risk_per_share = atr * risk_multiple
        
        if risk_per_share <= 0:
            return SizingResult(
                method='volatility_based',
                position_size_pct=0,
                position_size_dollars=0,
                max_risk_pct=0,
                recommended_shares=0,
                reasoning='Invalid ATR'
            )
        
        shares = int(risk_dollars / risk_per_share)
        position_dollars = shares * entry_price
        position_pct = position_dollars / self.account_value
        
        return SizingResult(
            method='volatility_based',
            position_size_pct=round(position_pct * 100, 2),
            position_size_dollars=round(position_dollars, 2),
            max_risk_pct=round(risk_per_trade_pct * 100, 2),
            recommended_shares=shares,
            reasoning=f'ATR: ${atr:.2f}, Risk multiple: {risk_multiple}x, Stop: ${risk_per_share:.2f}'
        )
    
    def optimal_f(self, trade_history: List[float]) -> SizingResult:
        """
        Optimal f position sizing (Ralph Vince)
        
        Maximizes geometric growth rate
        """
        if len(trade_history) < 10:
            return SizingResult(
                method='optimal_f',
                position_size_pct=0,
                position_size_dollars=0,
                max_risk_pct=0,
                recommended_shares=0,
                reasoning='Insufficient trade history (need 10+)'
            )
        
        returns = np.array(trade_history)
        biggest_loss = abs(min(returns))
        
        if biggest_loss == 0:
            return SizingResult(
                method='optimal_f',
                position_size_pct=0,
                position_size_dollars=0,
                max_risk_pct=0,
                recommended_shares=0,
                reasoning='No losses in history'
            )
        
        # Simplified optimal f calculation
        avg_return = np.mean(returns)
        
        # Optimal f ≈ Expected Return / Biggest Loss
        optimal_f = avg_return / biggest_loss
        
        # Safety: use half optimal f and cap at 25%
        safe_f = min(optimal_f / 2, 0.25)
        
        position_dollars = self.account_value * safe_f
        
        return SizingResult(
            method='optimal_f',
            position_size_pct=round(safe_f * 100, 2),
            position_size_dollars=round(position_dollars, 2),
            max_risk_pct=round(safe_f * 100, 2),
            recommended_shares=0,
            reasoning=f'Biggest loss: ${biggest_loss:.2f}, Avg return: ${avg_return:.2f}'
        )
    
    def risk_parity_sizing(self, volatility: float,
                          target_volatility: float = 0.10) -> SizingResult:
        """
        Risk parity position sizing
        
        Allocate based on inverse volatility
        """
        if volatility <= 0:
            return SizingResult(
                method='risk_parity',
                position_size_pct=0,
                position_size_dollars=0,
                max_risk_pct=0,
                recommended_shares=0,
                reasoning='Invalid volatility'
            )
        
        # Position size inversely proportional to volatility
        position_pct = target_volatility / volatility
        
        # Cap at reasonable limits
        position_pct = min(position_pct, 0.30)
        
        position_dollars = self.account_value * position_pct
        
        return SizingResult(
            method='risk_parity',
            position_size_pct=round(position_pct * 100, 2),
            position_size_dollars=round(position_dollars, 2),
            max_risk_pct=round(position_pct * volatility * 100, 2),
            recommended_shares=0,
            reasoning=f'Stock volatility: {volatility:.1%}, Target: {target_volatility:.1%}'
        )
    
    def calculate_all_methods(self, **kwargs) -> Dict[str, SizingResult]:
        """Calculate position size using all methods"""
        results = {}
        
        # Kelly
        if 'win_rate' in kwargs and 'avg_win' in kwargs and 'avg_loss' in kwargs:
            results['kelly'] = self.kelly_criterion(
                kwargs['win_rate'], kwargs['avg_win'], kwargs['avg_loss']
            )
        
        # Fixed Fractional
        if 'entry_price' in kwargs and 'stop_loss' in kwargs:
            results['fixed_fractional'] = self.fixed_fractional(
                entry_price=kwargs['entry_price'],
                stop_loss=kwargs['stop_loss']
            )
        
        # Volatility-based
        if 'atr' in kwargs and 'entry_price' in kwargs:
            results['volatility_based'] = self.volatility_based(
                atr=kwargs['atr'],
                entry_price=kwargs['entry_price']
            )
        
        # Optimal f
        if 'trade_history' in kwargs:
            results['optimal_f'] = self.optimal_f(kwargs['trade_history'])
        
        # Risk Parity
        if 'volatility' in kwargs:
            results['risk_parity'] = self.risk_parity_sizing(kwargs['volatility'])
        
        return results
    
    def get_recommended_size(self, methods_results: Dict[str, SizingResult]) -> SizingResult:
        """Get consensus recommended size from multiple methods"""
        if not methods_results:
            return SizingResult('', 0, 0, 0, 0, 'No methods calculated')
        
        # Average the position sizes
        avg_pct = np.mean([r.position_size_pct for r in methods_results.values()])
        
        # Conservative: use minimum
        min_pct = min([r.position_size_pct for r in methods_results.values()])
        
        # Recommended: average of methods, capped at 20%
        recommended_pct = min(avg_pct, 20)
        
        return SizingResult(
            method='consensus',
            position_size_pct=round(recommended_pct, 2),
            position_size_dollars=round(self.account_value * recommended_pct / 100, 2),
            max_risk_pct=round(recommended_pct * 0.5, 2),
            recommended_shares=0,
            reasoning=f'Consensus of {len(methods_results)} methods. Conservative cap at 20%.'
        )


# Usage
def quick_position_size(account: float, entry: float, 
                       stop: float, risk_pct: float = 0.02) -> Dict:
    """Quick fixed fractional position size"""
    calc = PositionSizingCalculator(account)
    result = calc.fixed_fractional(risk_pct, entry, stop)
    
    return {
        'shares': result.recommended_shares,
        'position_value': result.position_size_dollars,
        'position_pct': result.position_size_pct,
        'max_risk': result.max_risk_pct
    }


def kelly_position_size(account: float, win_rate: float,
                       avg_win: float, avg_loss: float) -> Dict:
    """Kelly criterion position size"""
    calc = PositionSizingCalculator(account)
    result = calc.kelly_criterion(win_rate, avg_win, avg_loss)
    
    return {
        'position_pct': result.position_size_pct,
        'position_value': result.position_size_dollars,
        'reasoning': result.reasoning
    }
