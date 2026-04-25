"""
Portfolio Optimizer
====================
Modern Portfolio Theory (Markowitz) implementation
with advanced risk metrics and constraints

Inspired by: Harry Markowitz (Nobel Prize), Renaissance Technologies
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PortfolioAllocation:
    """Optimized portfolio allocation result"""
    symbol: str
    weight: float
    expected_return: float
    risk_contribution: float
    sharpe_contribution: float


@dataclass
class OptimizationResult:
    """Complete optimization output"""
    objective: str  # 'sharpe', 'risk', 'return'
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    allocations: List[PortfolioAllocation]
    efficient_frontier: List[Dict]
    rebalance_threshold: float
    max_drawdown_estimate: float
    var_95: float
    var_99: float


class PortfolioOptimizer:
    """
    Markowitz Modern Portfolio Theory optimizer
    
    Features:
    - Mean-variance optimization
    - Efficient frontier generation
    - Risk parity weighting
    - Maximum Sharpe ratio
    - Minimum volatility
    - Target return optimization
    - Transaction cost modeling
    - Constraint handling
    """
    
    def __init__(
        self,
        risk_free_rate: float = 0.02,
        max_position_size: float = 0.25,
        min_position_size: float = 0.0,
        allow_short: bool = False
    ):
        self.risk_free_rate = risk_free_rate
        self.max_position_size = max_position_size
        self.min_position_size = min_position_size
        self.allow_short = allow_short
        
    def optimize(
        self,
        symbols: List[str],
        historical_returns: pd.DataFrame,
        objective: str = "sharpe",
        target_return: Optional[float] = None,
        target_risk: Optional[float] = None,
        current_weights: Optional[Dict[str, float]] = None,
        transaction_cost: float = 0.001
    ) -> OptimizationResult:
        """
        Run portfolio optimization
        
        Args:
            symbols: List of asset symbols
            historical_returns: DataFrame of historical returns
            objective: 'sharpe', 'risk', 'return', 'risk_parity'
            target_return: Target annual return (optional)
            target_risk: Target annual volatility (optional)
            current_weights: Current portfolio weights (optional)
            transaction_cost: Transaction cost as decimal
        
        Returns:
            OptimizationResult with allocations and metrics
        """
        # Calculate expected returns (annualized)
        expected_returns = historical_returns.mean() * 252
        
        # Calculate covariance matrix (annualized)
        cov_matrix = historical_returns.cov() * 252
        
        # Number of assets
        n_assets = len(symbols)
        
        # Generate efficient frontier
        efficient_frontier = self._generate_efficient_frontier(
            expected_returns, cov_matrix, n_assets
        )
        
        # Optimize based on objective
        if objective == "sharpe":
            weights = self._maximize_sharpe(expected_returns, cov_matrix)
        elif objective == "risk":
            weights = self._minimize_volatility(expected_returns, cov_matrix)
        elif objective == "return":
            weights = self._maximize_return(expected_returns, cov_matrix, target_risk)
        elif objective == "risk_parity":
            weights = self._risk_parity(expected_returns, cov_matrix)
        else:
            weights = self._equal_weight(n_assets)
        
        # Calculate portfolio metrics
        port_return = np.dot(weights, expected_returns)
        port_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = (port_return - self.risk_free_rate) / port_risk if port_risk > 0 else 0
        
        # Calculate VaR
        var_95 = self._calculate_var(weights, historical_returns, 0.95)
        var_99 = self._calculate_var(weights, historical_returns, 0.99)
        
        # Create allocations
        allocations = []
        for i, symbol in enumerate(symbols):
            risk_contrib = self._risk_contribution(weights, cov_matrix, i)
            allocations.append(PortfolioAllocation(
                symbol=symbol,
                weight=round(weights[i], 4),
                expected_return=round(expected_returns[symbol], 4),
                risk_contribution=round(risk_contrib, 4),
                sharpe_contribution=round(weights[i] * expected_returns[symbol] / port_risk, 4) if port_risk > 0 else 0
            ))
        
        # Estimate max drawdown
        max_dd = self._estimate_max_drawdown(weights, historical_returns)
        
        return OptimizationResult(
            objective=objective,
            expected_return=round(port_return, 4),
            expected_risk=round(port_risk, 4),
            sharpe_ratio=round(sharpe, 4),
            allocations=allocations,
            efficient_frontier=efficient_frontier,
            rebalance_threshold=0.05,  # 5% drift triggers rebalance
            max_drawdown_estimate=round(max_dd, 4),
            var_95=round(var_95, 4),
            var_99=round(var_99, 4)
        )
    
    def _maximize_sharpe(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame
    ) -> np.ndarray:
        """Find weights that maximize Sharpe ratio"""
        n = len(expected_returns)
        
        # Use gradient-free optimization for simplicity
        best_sharpe = -np.inf
        best_weights = np.ones(n) / n
        
        # Try multiple random starting points
        for _ in range(1000):
            weights = np.random.random(n)
            weights = weights / weights.sum()
            
            # Apply constraints
            weights = np.clip(weights, self.min_position_size, self.max_position_size)
            weights = weights / weights.sum()  # Renormalize
            
            port_return = np.dot(weights, expected_returns)
            port_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            if port_risk > 0:
                sharpe = (port_return - self.risk_free_rate) / port_risk
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_weights = weights
        
        return best_weights
    
    def _minimize_volatility(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame
    ) -> np.ndarray:
        """Find minimum volatility portfolio"""
        n = len(expected_returns)
        
        # Inverse variance weighting as approximation
        inv_variance = 1.0 / np.diag(cov_matrix)
        weights = inv_variance / inv_variance.sum()
        
        # Apply constraints
        weights = np.clip(weights, self.min_position_size, self.max_position_size)
        weights = weights / weights.sum()
        
        return weights
    
    def _maximize_return(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        target_risk: Optional[float]
    ) -> np.ndarray:
        """Maximize return for given risk level"""
        n = len(expected_returns)
        
        if target_risk is None:
            # Just pick highest return assets
            weights = np.zeros(n)
            weights[np.argmax(expected_returns)] = 1.0
            return weights
        
        # Otherwise use efficient frontier
        frontier = self._generate_efficient_frontier(expected_returns, cov_matrix, n)
        
        # Find portfolio closest to target risk
        closest = min(frontier, key=lambda x: abs(x['risk'] - target_risk))
        
        return np.array(closest['weights'])
    
    def _risk_parity(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame
    ) -> np.ndarray:
        """Equal risk contribution weighting"""
        n = len(expected_returns)
        weights = np.ones(n) / n
        
        # Iterative approach to equalize risk contributions
        for _ in range(10):
            # Calculate risk contributions
            port_var = np.dot(weights.T, np.dot(cov_matrix, weights))
            marginal_risk = np.dot(cov_matrix, weights) / np.sqrt(port_var)
            risk_contrib = weights * marginal_risk
            
            # Adjust weights to equalize
            avg_risk = risk_contrib.mean()
            adjustment = avg_risk / (risk_contrib + 1e-8)
            weights = weights * adjustment
            weights = weights / weights.sum()
            
            # Apply constraints
            weights = np.clip(weights, self.min_position_size, self.max_position_size)
            weights = weights / weights.sum()
        
        return weights
    
    def _equal_weight(self, n: int) -> np.ndarray:
        """Simple equal weighting"""
        return np.ones(n) / n
    
    def _generate_efficient_frontier(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        n_assets: int,
        n_points: int = 50
    ) -> List[Dict]:
        """Generate efficient frontier points"""
        frontier = []
        
        min_return = expected_returns.min()
        max_return = expected_returns.max()
        
        for i in range(n_points):
            target = min_return + (max_return - min_return) * i / (n_points - 1)
            
            # Simple optimization for this target
            weights = self._optimize_for_target(
                expected_returns, cov_matrix, target, n_assets
            )
            
            port_return = np.dot(weights, expected_returns)
            port_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (port_return - self.risk_free_rate) / port_risk if port_risk > 0 else 0
            
            frontier.append({
                'return': round(port_return, 4),
                'risk': round(port_risk, 4),
                'sharpe': round(sharpe, 4),
                'weights': weights.tolist()
            })
        
        return frontier
    
    def _optimize_for_target(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        target: float,
        n: int
    ) -> np.ndarray:
        """Optimize for target return"""
        # Simple approach: blend min variance and max return
        min_var_weights = self._minimize_volatility(expected_returns, cov_matrix)
        max_ret_weights = np.zeros(n)
        max_ret_weights[np.argmax(expected_returns)] = 1.0
        
        min_var_return = np.dot(min_var_weights, expected_returns)
        max_ret_return = expected_returns.max()
        
        if max_ret_return - min_var_return < 1e-6:
            return min_var_weights
        
        # Blend proportionally
        blend = (target - min_var_return) / (max_ret_return - min_var_return)
        blend = max(0, min(1, blend))
        
        weights = (1 - blend) * min_var_weights + blend * max_ret_weights
        weights = weights / weights.sum()
        
        return weights
    
    def _risk_contribution(
        self,
        weights: np.ndarray,
        cov_matrix: pd.DataFrame,
        asset_idx: int
    ) -> float:
        """Calculate risk contribution of an asset"""
        port_var = np.dot(weights.T, np.dot(cov_matrix, weights))
        if port_var == 0:
            return 0
        marginal_risk = np.dot(cov_matrix, weights)[asset_idx] / np.sqrt(port_var)
        return weights[asset_idx] * marginal_risk
    
    def _calculate_var(
        self,
        weights: np.ndarray,
        historical_returns: pd.DataFrame,
        confidence: float
    ) -> float:
        """Calculate historical Value at Risk"""
        port_returns = historical_returns.dot(weights)
        return np.percentile(port_returns, (1 - confidence) * 100)
    
    def _estimate_max_drawdown(
        self,
        weights: np.ndarray,
        historical_returns: pd.DataFrame
    ) -> float:
        """Estimate maximum drawdown"""
        port_returns = historical_returns.dot(weights)
        cumulative = (1 + port_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def get_recommendations(
        self,
        current_portfolio: Dict[str, float],
        optimized: OptimizationResult
    ) -> List[str]:
        """Generate rebalancing recommendations"""
        recommendations = []
        
        opt_weights = {a.symbol: a.weight for a in optimized.allocations}
        
        for symbol in set(list(current_portfolio.keys()) + list(opt_weights.keys())):
            current = current_portfolio.get(symbol, 0)
            target = opt_weights.get(symbol, 0)
            diff = target - current
            
            if abs(diff) > optimized.rebalance_threshold:
                action = "BUY" if diff > 0 else "SELL"
                recommendations.append(
                    f"{action} {symbol}: {abs(diff)*100:.1f}% "
                    f"(${abs(diff) * 100000:.0f} on $100K portfolio)"
                )
        
        return recommendations


# Convenience function
def optimize_portfolio(
    symbols: List[str],
    prices: pd.DataFrame,
    objective: str = "sharpe"
) -> OptimizationResult:
    """
    Quick portfolio optimization
    
    Example:
        result = optimize_portfolio(
            ['AAPL', 'MSFT', 'GOOGL'],
            price_data,
            objective='sharpe'
        )
        print(f"Optimal Sharpe: {result.sharpe_ratio}")
        for alloc in result.allocations:
            print(f"  {alloc.symbol}: {alloc.weight*100:.1f}%")
    """
    # Calculate returns
    returns = prices.pct_change().dropna()
    
    optimizer = PortfolioOptimizer()
    return optimizer.optimize(symbols, returns, objective=objective)
