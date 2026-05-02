"""
Portfolio Optimizer
===================
Markowitz Modern Portfolio Theory + Black-Litterman Model
Mean-variance optimization with risk parity and factor exposure
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from scipy.optimize import minimize
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Portfolio optimization result"""
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    diversification_ratio: float
    max_drawdown: float
    var_95: float
    method: str
    timestamp: datetime


class PortfolioOptimizer:
    """
    Production portfolio optimizer
    
    Methods:
    - Markowitz Mean-Variance Optimization
    - Black-Litterman (incorporating views)
    - Risk Parity (equal risk contribution)
    - Minimum Variance
    - Maximum Sharpe Ratio
    - Factor Exposure Optimization
    """
    
    def __init__(self, risk_free_rate: float = 0.04):
        self.risk_free_rate = risk_free_rate
        self.returns_data: pd.DataFrame = None
        self.covariance_matrix: pd.DataFrame = None
        self.tickers: List[str] = []
    
    def load_historical_returns(self, returns_df: pd.DataFrame):
        """Load historical returns data"""
        self.returns_data = returns_df
        self.tickers = list(returns_df.columns)
        self.covariance_matrix = returns_df.cov()
        logger.info(f"Loaded returns for {len(self.tickers)} assets")
    
    def generate_random_returns(self, tickers: List[str], 
                               periods: int = 252) -> pd.DataFrame:
        """Generate synthetic returns for testing"""
        np.random.seed(42)
        
        data = {}
        for ticker in tickers:
            # Different asset classes have different return/vol profiles
            if 'BOND' in ticker:
                mean, vol = 0.0003, 0.005
            elif 'GOLD' in ticker:
                mean, vol = 0.0002, 0.015
            elif 'TECH' in ticker:
                mean, vol = 0.001, 0.025
            else:
                mean, vol = 0.0007, 0.02
            
            data[ticker] = np.random.normal(mean, vol, periods)
        
        self.returns_data = pd.DataFrame(data)
        self.tickers = tickers
        self.covariance_matrix = self.returns_data.cov()
        
        return self.returns_data
    
    def markowitz_optimization(self, 
                              target_return: Optional[float] = None,
                              target_volatility: Optional[float] = None,
                              allow_short: bool = False) -> OptimizationResult:
        """
        Markowitz Mean-Variance Optimization
        
        Args:
            target_return: Target portfolio return (optional)
            target_volatility: Target volatility (optional)
            allow_short: Allow short positions
        """
        if self.returns_data is None:
            raise ValueError("Load returns data first")
        
        n = len(self.tickers)
        mean_returns = self.returns_data.mean()
        cov_matrix = self.covariance_matrix.values
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        if target_return is not None:
            constraints.append({
                'type': 'eq', 
                'fun': lambda x: np.dot(x, mean_returns) * 252 - target_return
            })
        
        if target_volatility is not None:
            target_var = target_volatility ** 2
            constraints.append({
                'type': 'eq',
                'fun': lambda x: np.dot(x, np.dot(cov_matrix, x)) * 252 - target_var
            })
        
        # Bounds
        if allow_short:
            bounds = tuple((-1, 1) for _ in range(n))
        else:
            bounds = tuple((0, 1) for _ in range(n))
        
        # Initial guess
        x0 = np.array([1/n] * n)
        
        # Objective function (minimize variance)
        def portfolio_variance(weights):
            return np.dot(weights, np.dot(cov_matrix, weights)) * 252
        
        # Optimize
        result = minimize(
            portfolio_variance,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            logger.warning(f"Optimization failed: {result.message}")
        
        optimal_weights = result.x
        
        return self._create_result(optimal_weights, mean_returns, cov_matrix, 'markowitz')
    
    def maximize_sharpe_ratio(self, allow_short: bool = False) -> OptimizationResult:
        """Find portfolio with maximum Sharpe ratio"""
        if self.returns_data is None:
            raise ValueError("Load returns data first")
        
        n = len(self.tickers)
        mean_returns = self.returns_data.mean()
        cov_matrix = self.covariance_matrix.values
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        # Bounds
        bounds = tuple((-1 if allow_short else 0, 1) for _ in range(n))
        
        # Initial guess
        x0 = np.array([1/n] * n)
        
        # Negative Sharpe (we minimize)
        def neg_sharpe(weights):
            port_return = np.dot(weights, mean_returns) * 252
            port_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)) * 252)
            if port_vol == 0:
                return 0
            return -(port_return - self.risk_free_rate) / port_vol
        
        result = minimize(
            neg_sharpe,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return self._create_result(result.x, mean_returns, cov_matrix, 'max_sharpe')
    
    def minimum_variance_portfolio(self, allow_short: bool = False) -> OptimizationResult:
        """Find minimum variance portfolio"""
        return self.markowitz_optimization(target_return=None, allow_short=allow_short)
    
    def risk_parity_optimization(self) -> OptimizationResult:
        """
        Risk Parity - Equal risk contribution from each asset
        """
        if self.returns_data is None:
            raise ValueError("Load returns data first")
        
        n = len(self.tickers)
        mean_returns = self.returns_data.mean()
        cov_matrix = self.covariance_matrix.values
        
        # Initial guess
        x0 = np.array([1/n] * n)
        
        # Bounds (long only for risk parity)
        bounds = tuple((0.01, 1) for _ in range(n))
        
        # Constraint: sum to 1
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        # Risk parity objective
        def risk_parity_obj(weights):
            port_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            marginal_risk = np.dot(cov_matrix, weights) / port_vol
            risk_contrib = weights * marginal_risk
            
            # Minimize variance of risk contributions
            return np.sum((risk_contrib - risk_contrib.mean()) ** 2)
        
        result = minimize(
            risk_parity_obj,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return self._create_result(result.x, mean_returns, cov_matrix, 'risk_parity')
    
    def black_litterman_optimization(self, 
                                  market_caps: Dict[str, float],
                                  views: Dict[str, Tuple[float, float]],
                                  tau: float = 0.025,
                                  confidence: float = 0.5) -> OptimizationResult:
        """
        Black-Litterman Model
        
        Args:
            market_caps: Market capitalizations for market weights
            views: Dict of {asset: (expected_return, confidence)}
            tau: Uncertainty parameter
            confidence: View confidence (0-1)
        """
        if self.returns_data is None:
            raise ValueError("Load returns data first")
        
        # Calculate market weights
        total_cap = sum(market_caps.values())
        market_weights = np.array([market_caps.get(t, 0) / total_cap for t in self.tickers])
        
        # Prior (implied) returns
        mean_returns = self.returns_data.mean()
        cov_matrix = self.covariance_matrix.values
        
        # Reverse optimization to get equilibrium returns
        lambda_param = 1.0  # Risk aversion
        pi = lambda_param * np.dot(cov_matrix, market_weights)
        
        # Build view matrix P and vector Q
        view_assets = list(views.keys())
        n_views = len(view_assets)
        n_assets = len(self.tickers)
        
        P = np.zeros((n_views, n_assets))
        Q = np.zeros(n_views)
        
        for i, asset in enumerate(view_assets):
            if asset in self.tickers:
                idx = self.tickers.index(asset)
                P[i, idx] = 1
                Q[i] = views[asset][0]
        
        # View uncertainty (Omega)
        Omega = np.diag([views[a][1] for a in view_assets])
        
        # Posterior returns
        tau_cov = tau * cov_matrix
        
        try:
            middle = np.linalg.inv(np.dot(np.dot(P, tau_cov), P.T) + Omega)
            posterior_mean = pi + np.dot(
                np.dot(np.dot(tau_cov, P.T), middle),
                (Q - np.dot(P, pi))
            )
            
            # Use posterior returns for optimization
            result = self._optimize_with_returns(posterior_mean, cov_matrix)
            return self._create_result(result, mean_returns, cov_matrix, 'black_litterman')
            
        except np.linalg.LinAlgError:
            logger.error("Black-Litterman matrix inversion failed")
            # Fallback to standard Markowitz
            return self.markowitz_optimization()
    
    def _optimize_with_returns(self, expected_returns: np.ndarray, 
                               cov_matrix: np.ndarray) -> np.ndarray:
        """Optimize given expected returns"""
        n = len(expected_returns)
        
        def neg_sharpe(weights):
            port_return = np.dot(weights, expected_returns) * 252
            port_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)) * 252)
            if port_vol == 0:
                return 0
            return -(port_return - self.risk_free_rate) / port_vol
        
        x0 = np.array([1/n] * n)
        bounds = tuple((0, 1) for _ in range(n))
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        result = minimize(
            neg_sharpe,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x
    
    def _create_result(self, weights: np.ndarray, mean_returns: pd.Series,
                      cov_matrix: np.ndarray, method: str) -> OptimizationResult:
        """Create optimization result object"""
        # Portfolio metrics
        port_return = np.dot(weights, mean_returns) * 252
        port_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)) * 252)
        sharpe = (port_return - self.risk_free_rate) / port_vol if port_vol > 0 else 0
        
        # Diversification ratio
        weighted_vols = np.sqrt(np.diag(cov_matrix)) * weights
        div_ratio = np.sum(weighted_vols) / port_vol if port_vol > 0 else 0
        
        # VaR
        var_95 = port_return - 1.645 * port_vol
        
        return OptimizationResult(
            weights={t: round(w, 4) for t, w in zip(self.tickers, weights)},
            expected_return=round(port_return, 4),
            volatility=round(port_vol, 4),
            sharpe_ratio=round(sharpe, 4),
            diversification_ratio=round(div_ratio, 4),
            max_drawdown=round(port_vol * 2, 4),  # Approximation
            var_95=round(var_95, 4),
            method=method,
            timestamp=datetime.now()
        )
    
    def efficient_frontier(self, n_points: int = 50) -> List[Dict]:
        """Generate efficient frontier points"""
        if self.returns_data is None:
            return []
        
        mean_returns = self.returns_data.mean()
        cov_matrix = self.covariance_matrix.values
        
        # Find min and max return
        min_ret = mean_returns.min() * 252
        max_ret = mean_returns.max() * 252
        
        target_returns = np.linspace(min_ret, max_ret, n_points)
        frontier = []
        
        for target in target_returns:
            try:
                result = self.markowitz_optimization(target_return=target)
                frontier.append({
                    'return': result.expected_return,
                    'volatility': result.volatility,
                    'sharpe': result.sharpe_ratio,
                    'weights': result.weights
                })
            except:
                continue
        
        return frontier
    
    def get_recommendation(self, risk_tolerance: str = 'moderate') -> Dict:
        """
        Get portfolio recommendation based on risk tolerance
        
        Args:
            risk_tolerance: 'conservative', 'moderate', 'aggressive'
        """
        if risk_tolerance == 'conservative':
            result = self.minimum_variance_portfolio()
        elif risk_tolerance == 'aggressive':
            result = self.maximize_sharpe_ratio()
        else:  # moderate
            result = self.risk_parity_optimization()
        
        return {
            'risk_profile': risk_tolerance,
            'optimization_method': result.method,
            'recommended_allocation': result.weights,
            'expected_return_pct': round(result.expected_return * 100, 2),
            'expected_volatility_pct': round(result.volatility * 100, 2),
            'sharpe_ratio': result.sharpe_ratio,
            'var_95_pct': round(result.var_95 * 100, 2),
            'diversification_ratio': result.diversification_ratio,
            'rebalancing_frequency': 'quarterly' if risk_tolerance == 'conservative' else 'monthly'
        }


# Quick usage functions
def optimize_portfolio_quick(returns_df: pd.DataFrame, 
                            method: str = 'max_sharpe') -> Dict:
    """Quick portfolio optimization"""
    optimizer = PortfolioOptimizer()
    optimizer.load_historical_returns(returns_df)
    
    if method == 'max_sharpe':
        result = optimizer.maximize_sharpe_ratio()
    elif method == 'min_variance':
        result = optimizer.minimum_variance_portfolio()
    elif method == 'risk_parity':
        result = optimizer.risk_parity_optimization()
    else:
        result = optimizer.markowitz_optimization()
    
    return {
        'weights': result.weights,
        'expected_return': result.expected_return,
        'volatility': result.volatility,
        'sharpe_ratio': result.sharpe_ratio
    }


def get_efficient_frontier_chart(returns_df: pd.DataFrame) -> List[Dict]:
    """Get data for efficient frontier chart"""
    optimizer = PortfolioOptimizer()
    optimizer.load_historical_returns(returns_df)
    return optimizer.efficient_frontier()
