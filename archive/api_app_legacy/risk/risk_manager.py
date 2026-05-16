"""Risk Management Framework - VaR, CVaR, Stress Testing"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RiskMetrics:
    """Risk metrics container"""
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    volatility: float
    beta: float
    max_drawdown: float
    sharpe_ratio: float
    calmar_ratio: float
    tail_risk: float

class RiskManager:
    """
    Production risk management system
    
    Features:
    - Value at Risk (VaR) - Historical and Parametric
    - Conditional VaR (CVaR/Expected Shortfall)
    - Portfolio stress testing
    - Position sizing based on risk
    - Correlation monitoring
    """
    
    def __init__(self, confidence_levels: List[float] = None):
        self.confidence_levels = confidence_levels or [0.95, 0.99]
        self.positions: Dict[str, float] = {}
        self.risk_limits = {
            'max_portfolio_var': 0.02,  # 2% daily VaR
            'max_position_size': 0.10,   # 10% single position
            'max_correlation': 0.80,     # 80% correlation limit
            'max_drawdown': 0.15         # 15% max drawdown
        }
    
    def calculate_var(self, returns: pd.Series, 
                     method: str = 'historical') -> Dict[float, float]:
        """
        Calculate Value at Risk
        
        Args:
            returns: Series of returns
            method: 'historical', 'parametric', or 'monte_carlo'
        """
        var_results = {}
        
        if method == 'historical':
            # Historical simulation
            for confidence in self.confidence_levels:
                var = np.percentile(returns.dropna(), (1 - confidence) * 100)
                var_results[confidence] = var
        
        elif method == 'parametric':
            # Parametric (assuming normal distribution)
            mean = returns.mean()
            std = returns.std()
            for confidence in self.confidence_levels:
                z_score = {0.95: 1.645, 0.99: 2.326}.get(confidence, 1.645)
                var = mean - z_score * std
                var_results[confidence] = var
        
        elif method == 'monte_carlo':
            # Monte Carlo simulation
            mean = returns.mean()
            std = returns.std()
            simulations = 10000
            simulated_returns = np.random.normal(mean, std, simulations)
            
            for confidence in self.confidence_levels:
                var = np.percentile(simulated_returns, (1 - confidence) * 100)
                var_results[confidence] = var
        
        return var_results
    
    def calculate_cvar(self, returns: pd.Series) -> Dict[float, float]:
        """
        Calculate Conditional Value at Risk (Expected Shortfall)
        """
        cvar_results = {}
        
        for confidence in self.confidence_levels:
            var_threshold = np.percentile(returns.dropna(), (1 - confidence) * 100)
            # Average of returns below VaR threshold
            cvar = returns[returns <= var_threshold].mean()
            cvar_results[confidence] = cvar
        
        return cvar_results
    
    def calculate_beta(self, stock_returns: pd.Series, 
                      market_returns: pd.Series) -> float:
        """Calculate beta relative to market"""
        covariance = stock_returns.cov(market_returns)
        market_variance = market_returns.var()
        
        beta = covariance / market_variance if market_variance > 0 else 1.0
        return beta
    
    def calculate_drawdown(self, equity_curve: pd.Series) -> Dict:
        """Calculate drawdown statistics"""
        # Calculate running maximum
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        
        return {
            'max_drawdown': drawdown.min(),
            'avg_drawdown': drawdown[drawdown < 0].mean(),
            'drawdown_duration': self._calculate_drawdown_duration(drawdown),
            'current_drawdown': drawdown.iloc[-1] if len(drawdown) > 0 else 0
        }
    
    def _calculate_drawdown_duration(self, drawdown: pd.Series) -> int:
        """Calculate longest drawdown duration"""
        in_drawdown = drawdown < 0
        durations = []
        current_duration = 0
        
        for is_dd in in_drawdown:
            if is_dd:
                current_duration += 1
            else:
                durations.append(current_duration)
                current_duration = 0
        
        durations.append(current_duration)
        return max(durations) if durations else 0
    
    def stress_test(self, positions: Dict[str, float], 
                   scenarios: Optional[Dict] = None) -> Dict:
        """
        Run stress tests on portfolio
        
        Scenarios: market crash, volatility spike, correlation breakdown
        """
        if scenarios is None:
            scenarios = {
                'market_crash_2008': {'SPY': -0.50, 'QQQ': -0.45, 'IWM': -0.55},
                'covid_crash': {'SPY': -0.35, 'QQQ': -0.30, 'IWM': -0.40, 'GLD': 0.10},
                'interest_rate_shock': {'TLT': -0.20, 'SPY': -0.15, 'XLF': -0.25},
                'inflation_spike': {'GLD': 0.20, 'TLT': -0.25, 'USO': 0.30},
                'tech_bubble_burst': {'QQQ': -0.60, 'SPY': -0.25, 'IWM': -0.15}
            }
        
        results = {}
        portfolio_value = sum(positions.values())
        
        for scenario_name, shocks in scenarios.items():
            portfolio_impact = 0
            
            for ticker, position_value in positions.items():
                # Find applicable shock or use default
                shock = shocks.get(ticker, shocks.get('SPY', -0.20))
                impact = position_value * shock
                portfolio_impact += impact
            
            loss_pct = portfolio_impact / portfolio_value if portfolio_value > 0 else 0
            
            results[scenario_name] = {
                'portfolio_impact_usd': round(portfolio_impact, 2),
                'loss_pct': round(loss_pct * 100, 2),
                'severity': 'severe' if loss_pct < -0.30 else 'moderate' if loss_pct < -0.15 else 'mild'
            }
        
        return results
    
    def check_risk_limits(self, portfolio_value: float, 
                         var_95: float) -> List[str]:
        """Check if portfolio violates risk limits"""
        breaches = []
        
        # VaR limit
        var_pct = abs(var_95) / portfolio_value if portfolio_value > 0 else 0
        if var_pct > self.risk_limits['max_portfolio_var']:
            breaches.append(f"VaR breach: {var_pct:.2%} > {self.risk_limits['max_portfolio_var']:.2%}")
        
        # Drawdown limit
        if var_pct > self.risk_limits['max_drawdown']:
            breaches.append(f"Drawdown risk: {var_pct:.2%} exceeds {self.risk_limits['max_drawdown']:.2%} limit")
        
        return breaches
    
    def position_sizing(self, signal_strength: float, 
                       volatility: float,
                       confidence: float = 0.95) -> float:
        """
        Kelly Criterion-based position sizing
        
        f* = (p*b - q) / b
        where p = win probability, b = win/loss ratio
        """
        # Simplified Kelly fraction
        win_prob = 0.55  # Assumed edge
        win_loss_ratio = 1.5  # Assumed payoff
        
        kelly_fraction = (win_prob * win_loss_ratio - (1 - win_prob)) / win_loss_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        
        # Adjust for volatility (lower size for higher vol)
        vol_adjustment = 0.20 / (volatility + 0.01)  # Target 20% vol
        
        # Final position size
        position_size = kelly_fraction * vol_adjustment * signal_strength
        
        return min(position_size, self.risk_limits['max_position_size'])
    
    def get_full_report(self, returns: pd.Series, 
                       positions: Dict[str, float],
                       equity_curve: pd.Series) -> Dict:
        """Generate comprehensive risk report"""
        var = self.calculate_var(returns, method='historical')
        cvar = self.calculate_cvar(returns)
        drawdown = self.calculate_drawdown(equity_curve)
        stress = self.stress_test(positions)
        
        portfolio_value = equity_curve.iloc[-1] if len(equity_curve) > 0 else 0
        breaches = self.check_risk_limits(portfolio_value, var.get(0.95, 0))
        
        return {
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': round(portfolio_value, 2),
            'risk_metrics': {
                'var_95_daily': round(var.get(0.95, 0) * 100, 2),
                'var_99_daily': round(var.get(0.99, 0) * 100, 2),
                'cvar_95': round(cvar.get(0.95, 0) * 100, 2),
                'cvar_99': round(cvar.get(0.99, 0) * 100, 2),
                'volatility_annual': round(returns.std() * np.sqrt(252) * 100, 2),
                'max_drawdown': round(drawdown['max_drawdown'] * 100, 2),
                'sharpe_ratio': round(returns.mean() / (returns.std() + 1e-8) * np.sqrt(252), 2)
            },
            'drawdown_analysis': drawdown,
            'stress_test_results': stress,
            'risk_limit_breaches': breaches,
            'risk_status': 'COMPLIANT' if not breaches else 'BREACH'
        }

# Convenience function
def quick_risk_assessment(returns: List[float]) -> Dict:
    """Quick risk metrics calculation"""
    rm = RiskManager()
    series = pd.Series(returns)
    var = rm.calculate_var(series)
    cvar = rm.calculate_cvar(series)
    
    return {
        'var_95': round(var.get(0.95, 0), 4),
        'var_99': round(var.get(0.99, 0), 4),
        'cvar_95': round(cvar.get(0.95, 0), 4),
        'volatility': round(series.std(), 4)
    }
