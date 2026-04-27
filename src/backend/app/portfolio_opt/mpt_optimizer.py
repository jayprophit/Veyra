"""Modern Portfolio Theory Optimizer - Markowitz efficient frontier"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
import statistics
import math

@dataclass
class Portfolio:
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float

class ModernPortfolioOptimizer:
    """Markowitz Modern Portfolio Theory implementation"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        self.assets: List[str] = []
        self.returns: Dict[str, List[float]] = {}
    
    def add_asset(self, symbol: str, historical_returns: List[float]):
        """Add asset to optimization universe"""
        self.assets.append(symbol)
        self.returns[symbol] = historical_returns
    
    def calculate_expected_returns(self) -> Dict[str, float]:
        """Calculate expected returns from historical data"""
        expected = {}
        for symbol, rets in self.returns.items():
            expected[symbol] = statistics.mean(rets) if rets else 0
        return expected
    
    def calculate_covariance_matrix(self) -> Dict[str, Dict[str, float]]:
        """Calculate covariance matrix"""
        cov = {a: {} for a in self.assets}
        
        for i, a1 in enumerate(self.assets):
            for a2 in self.assets[i:]:
                if len(self.returns[a1]) == len(self.returns[a2]) and len(self.returns[a1]) > 1:
                    cov_val = self._covariance(self.returns[a1], self.returns[a2])
                else:
                    cov_val = 0
                
                cov[a1][a2] = cov_val
                cov[a2][a1] = cov_val
        
        return cov
    
    def _covariance(self, x: List[float], y: List[float]) -> float:
        """Calculate covariance between two series"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        return sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / (len(x) - 1)
    
    def portfolio_volatility(self, weights: Dict[str, float]) -> float:
        """Calculate portfolio volatility"""
        cov_matrix = self.calculate_covariance_matrix()
        
        variance = 0
        for a1 in self.assets:
            for a2 in self.assets:
                variance += weights[a1] * weights[a2] * cov_matrix[a1][a2]
        
        return math.sqrt(variance) if variance > 0 else 0
    
    def portfolio_return(self, weights: Dict[str, float]) -> float:
        """Calculate portfolio expected return"""
        expected = self.calculate_expected_returns()
        return sum(weights[a] * expected[a] for a in self.assets)
    
    def sharpe_ratio(self, weights: Dict[str, float]) -> float:
        """Calculate Sharpe ratio"""
        port_return = self.portfolio_return(weights)
        port_vol = self.portfolio_volatility(weights)
        
        if port_vol == 0:
            return 0
        
        return (port_return - self.risk_free_rate) / port_vol
    
    def optimize_max_sharpe(self) -> Portfolio:
        """Find portfolio with maximum Sharpe ratio"""
        # Simplified: equal weight as starting point
        n = len(self.assets)
        equal_weight = 1.0 / n if n > 0 else 0
        
        best_sharpe = -float('inf')
        best_weights = {a: equal_weight for a in self.assets}
        
        # Try a few simple combinations (simplified optimization)
        for _ in range(100):
            # Random weight adjustment
            import random
            weights = {a: random.random() for a in self.assets}
            total = sum(weights.values())
            weights = {a: w/total for a, w in weights.items()}
            
            sharpe = self.sharpe_ratio(weights)
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_weights = weights
        
        return Portfolio(
            weights=best_weights,
            expected_return=self.portfolio_return(best_weights),
            volatility=self.portfolio_volatility(best_weights),
            sharpe_ratio=best_sharpe
        )
    
    def optimize_min_volatility(self, target_return: float = None) -> Portfolio:
        """Find minimum volatility portfolio"""
        # Start with equal weights
        n = len(self.assets)
        if n == 0:
            return Portfolio({}, 0, 0, 0)
        
        equal_weight = 1.0 / n
        weights = {a: equal_weight for a in self.assets}
        
        # Simplified: use lowest volatility assets
        volatilities = {a: statistics.stdev(self.returns[a]) if len(self.returns[a]) > 1 else 0 
                      for a in self.assets}
        
        # Inverse volatility weighting
        inv_vols = {a: 1/v if v > 0 else 0 for a, v in volatilities.items()}
        total_inv = sum(inv_vols.values())
        
        if total_inv > 0:
            weights = {a: v/total_inv for a, v in inv_vols.items()}
        
        return Portfolio(
            weights=weights,
            expected_return=self.portfolio_return(weights),
            volatility=self.portfolio_volatility(weights),
            sharpe_ratio=self.sharpe_ratio(weights)
        )
    
    def generate_efficient_frontier(self, points: int = 10) -> List[Portfolio]:
        """Generate efficient frontier portfolios"""
        frontier = []
        
        # Min vol portfolio
        min_vol = self.optimize_min_volatility()
        frontier.append(min_vol)
        
        # Max return portfolio (100% in highest return asset)
        expected = self.calculate_expected_returns()
        best_asset = max(expected, key=expected.get)
        max_ret_weights = {a: 1.0 if a == best_asset else 0 for a in self.assets}
        
        max_return = self.portfolio_return(max_ret_weights)
        max_vol = self.portfolio_volatility(max_ret_weights)
        
        frontier.append(Portfolio(
            weights=max_ret_weights,
            expected_return=max_return,
            volatility=max_vol,
            sharpe_ratio=self.sharpe_ratio(max_ret_weights)
        ))
        
        # Intermediate portfolios (simplified)
        for i in range(1, points - 1):
            w = i / (points - 1)
            weights = {a: (1-w) * min_vol.weights[a] + w * max_ret_weights[a] 
                      for a in self.assets}
            
            frontier.append(Portfolio(
                weights=weights,
                expected_return=self.portfolio_return(weights),
                volatility=self.portfolio_volatility(weights),
                sharpe_ratio=self.sharpe_ratio(weights)
            ))
        
        return sorted(frontier, key=lambda p: p.volatility)
    
    def get_allocation_recommendation(self, risk_tolerance: str) -> Dict:
        """Get allocation based on risk tolerance"""
        frontier = self.generate_efficient_frontier()
        
        if risk_tolerance == "CONSERVATIVE":
            portfolio = frontier[0]  # Min vol
        elif risk_tolerance == "MODERATE":
            portfolio = frontier[len(frontier)//2]  # Middle
        elif risk_tolerance == "AGGRESSIVE":
            portfolio = frontier[-1]  # Max return
        else:
            portfolio = max(frontier, key=lambda p: p.sharpe_ratio)  # Max Sharpe
        
        return {
            "risk_tolerance": risk_tolerance,
            "optimal_weights": {k: round(v, 3) for k, v in portfolio.weights.items()},
            "expected_return": round(portfolio.expected_return * 100, 2),
            "expected_volatility": round(portfolio.volatility * 100, 2),
            "sharpe_ratio": round(portfolio.sharpe_ratio, 3),
            "efficient_portfolio": True
        }
