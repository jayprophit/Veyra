"""Advanced Portfolio Analytics."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PortfolioMetrics:
    total_value: float
    total_return: float
    total_return_pct: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    alpha: float
    beta: float
    var_95: float
    correlation_matrix: Optional[Dict] = None

class PortfolioAnalytics:
    """Professional-grade portfolio analytics."""
    
    def calculate_metrics(self, 
                         returns: pd.Series,
                         benchmark_returns: Optional[pd.Series] = None,
                         risk_free_rate: float = 0.02) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics."""
        
        total_return = (returns + 1).prod() - 1
        
        # Annualized metrics
        periods_per_year = 252
        ann_return = returns.mean() * periods_per_year
        ann_vol = returns.std() * np.sqrt(periods_per_year)
        
        # Sharpe ratio
        sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0
        
        # Maximum drawdown
        cum_returns = (1 + returns).cumprod()
        running_max = cum_returns.expanding().max()
        drawdown = (cum_returns - running_max) / running_max
        max_dd = drawdown.min()
        
        # VaR (Value at Risk)
        var_95 = np.percentile(returns, 5)
        
        # Alpha and Beta (if benchmark provided)
        alpha, beta = 0.0, 1.0
        if benchmark_returns is not None and len(returns) == len(benchmark_returns):
            aligned_returns = pd.DataFrame({'portfolio': returns, 'benchmark': benchmark_returns})
            aligned_returns = aligned_returns.dropna()
            
            if len(aligned_returns) > 1:
                cov_matrix = np.cov(aligned_returns['portfolio'], aligned_returns['benchmark'])
                beta = cov_matrix[0, 1] / cov_matrix[1, 1] if cov_matrix[1, 1] != 0 else 1.0
                alpha = ann_return - (risk_free_rate + beta * (aligned_returns['benchmark'].mean() * periods_per_year - risk_free_rate))
        
        return PortfolioMetrics(
            total_value=0.0,
            total_return=total_return,
            total_return_pct=total_return * 100,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd * 100,
            volatility=ann_vol * 100,
            alpha=alpha,
            beta=beta,
            var_95=var_95
        )
    
    def monte_carlo_simulation(self,
                              mean_return: float,
                              volatility: float,
                              initial_value: float = 100000,
                              days: int = 252,
                              simulations: int = 1000) -> Dict[str, Any]:
        """Run Monte Carlo simulation for portfolio projections."""
        
        results = []
        for _ in range(simulations):
            daily_returns = np.random.normal(mean_return, volatility, days)
            price_series = initial_value * (1 + daily_returns).cumprod()
            results.append(price_series[-1])
        
        results = np.array(results)
        
        return {
            'initial_value': initial_value,
            'projected_value_mean': float(np.mean(results)),
            'projected_value_median': float(np.median(results)),
            'projected_value_std': float(np.std(results)),
            'percentile_95': float(np.percentile(results, 95)),
            'percentile_75': float(np.percentile(results, 75)),
            'percentile_25': float(np.percentile(results, 25)),
            'percentile_5': float(np.percentile(results, 5)),
            'probability_of_profit': float(np.mean(results > initial_value)),
            'simulations': simulations,
            'days': days
        }
    
    def efficient_frontier(self,
                          returns: pd.DataFrame,
                          num_portfolios: int = 100) -> List[Dict]:
        """Generate efficient frontier for portfolio optimization."""
        
        n_assets = len(returns.columns)
        results = []
        
        for _ in range(num_portfolios):
            # Random weights
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)
            
            # Portfolio return and volatility
            port_return = np.sum(returns.mean() * weights) * 252
            port_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            
            results.append({
                'return': float(port_return),
                'volatility': float(port_vol),
                'sharpe': float((port_return - 0.02) / port_vol) if port_vol > 0 else 0,
                'weights': {col: float(w) for col, w in zip(returns.columns, weights)}
            })
        
        return sorted(results, key=lambda x: x['sharpe'], reverse=True)

analytics = PortfolioAnalytics()
