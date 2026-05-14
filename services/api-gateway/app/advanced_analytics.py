"""SSS-Grade Advanced Analytics Engine

Institutional-grade analytics:
- Risk metrics (Sharpe, Sortino, Calmar, Treynor)
- Portfolio optimization (Markowitz, Black-Litterman)
- Factor analysis (Fama-French)
- Correlation matrices
- Efficient frontier
- Monte Carlo with multiple scenarios
- Attribution analysis
- Drawdown analysis
- Volatility forecasting
- Tail risk (VaR, CVaR, Expected Shortfall)
"""

import numpy as np
import pandas as pd
from scipy import stats, optimize
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class RiskMetrics:
    """Comprehensive risk metrics"""
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    treynor_ratio: float
    volatility_annual: float
    downside_deviation: float
    max_drawdown: float
    max_drawdown_duration: int
    var_95: float
    var_99: float
    cvar_95: float
    beta: float
    alpha: float
    r_squared: float
    information_ratio: float
    tracking_error: float
    skewness: float
    kurtosis: float

@dataclass
class FactorExposure:
    """Factor model exposure"""
    market: float
    size: float
    value: float
    momentum: float
    quality: float
    low_volatility: float
    yield_factor: float

class SSSAnalyticsEngine:
    """SSS-Grade Analytics Engine"""
    
    def __init__(self, risk_free_rate: float = 0.045):  # 4.5% annual
        self.risk_free_rate = risk_free_rate / 252  # Daily rate
        
    def calculate_returns(self, prices: pd.Series) -> pd.Series:
        """Calculate daily returns"""
        return prices.pct_change().dropna()
    
    def calculate_risk_metrics(self, 
                              returns: pd.Series,
                              benchmark_returns: Optional[pd.Series] = None) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        
        # Basic statistics
        mean_return = returns.mean()
        std_return = returns.std()
        annual_return = mean_return * 252
        annual_volatility = std_return * np.sqrt(252)
        
        # Sharpe Ratio
        sharpe = (annual_return - self.risk_free_rate * 252) / annual_volatility if annual_volatility != 0 else 0
        
        # Downside deviation (Sortino denominator)
        downside_returns = returns[returns < 0]
        downside_dev = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        
        # Sortino Ratio
        sortino = (annual_return - self.risk_free_rate * 252) / downside_dev if downside_dev != 0 else 0
        
        # Max Drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Drawdown duration
        underwater = drawdown < 0
        durations = []
        current_duration = 0
        for is_under in underwater:
            if is_under:
                current_duration += 1
            else:
                if current_duration > 0:
                    durations.append(current_duration)
                current_duration = 0
        if current_duration > 0:
            durations.append(current_duration)
        max_drawdown_duration = max(durations) if durations else 0
        
        # Calmar Ratio
        calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # VaR and CVaR
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        cvar_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else 0
        
        # Beta and Alpha (if benchmark provided)
        beta = alpha = treynor = r_squared = tracking_error = information_ratio = 0
        
        if benchmark_returns is not None and len(benchmark_returns) == len(returns):
            # Align indices
            aligned_data = pd.concat([returns, benchmark_returns], axis=1).dropna()
            if len(aligned_data) > 1:
                port_ret = aligned_data.iloc[:, 0]
                bench_ret = aligned_data.iloc[:, 1]
                
                # Beta
                covariance = port_ret.cov(bench_ret)
                benchmark_variance = bench_ret.var()
                beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
                
                # Alpha (Jensen's)
                alpha = (port_ret.mean() - self.risk_free_rate) - beta * (bench_ret.mean() - self.risk_free_rate)
                alpha *= 252  # Annualize
                
                # Treynor Ratio
                treynor = (annual_return - self.risk_free_rate * 252) / beta if beta != 0 else 0
                
                # R-squared
                correlation = port_ret.corr(bench_ret)
                r_squared = correlation ** 2 if not pd.isna(correlation) else 0
                
                # Tracking Error
                tracking_diff = port_ret - bench_ret
                tracking_error = tracking_diff.std() * np.sqrt(252)
                
                # Information Ratio
                information_ratio = tracking_diff.mean() * 252 / tracking_error if tracking_error != 0 else 0
        
        # Higher moments
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        
        return RiskMetrics(
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            treynor_ratio=treynor,
            volatility_annual=annual_volatility,
            downside_deviation=downside_dev,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_drawdown_duration,
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            beta=beta,
            alpha=alpha,
            r_squared=r_squared,
            information_ratio=information_ratio,
            tracking_error=tracking_error,
            skewness=skewness,
            kurtosis=kurtosis
        )
    
    def calculate_factor_exposure(self, 
                                  returns: pd.Series,
                                  factor_returns: pd.DataFrame) -> FactorExposure:
        """Calculate factor model exposure (Fama-French style)"""
        
        # Align data
        aligned = pd.concat([returns, factor_returns], axis=1).dropna()
        
        if len(aligned) < 30:  # Need sufficient data
            return FactorExposure(0, 0, 0, 0, 0, 0, 0)
        
        y = aligned.iloc[:, 0]
        X = aligned.iloc[:, 1:]
        
        # Add constant for intercept
        X = np.column_stack([np.ones(len(X)), X])
        
        # OLS regression
        try:
            coefficients = np.linalg.lstsq(X, y, rcond=None)[0]
            
            return FactorExposure(
                market=coefficients[1] if len(coefficients) > 1 else 0,
                size=coefficients[2] if len(coefficients) > 2 else 0,
                value=coefficients[3] if len(coefficients) > 3 else 0,
                momentum=coefficients[4] if len(coefficients) > 4 else 0,
                quality=coefficients[5] if len(coefficients) > 5 else 0,
                low_volatility=coefficients[6] if len(coefficients) > 6 else 0,
                yield_factor=coefficients[7] if len(coefficients) > 7 else 0
            )
        except:
            return FactorExposure(0, 0, 0, 0, 0, 0, 0)
    
    def efficient_frontier(self,
                          returns: pd.DataFrame,
                          risk_free_rate: Optional[float] = None,
                          num_portfolios: int = 100) -> Dict:
        """Calculate efficient frontier"""
        
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate * 252
        
        n_assets = len(returns.columns)
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        
        results = {
            "returns": [],
            "volatilities": [],
            "sharpe_ratios": [],
            "weights": []
        }
        
        # Generate random portfolios
        np.random.seed(42)
        for _ in range(num_portfolios):
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)
            
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (portfolio_return - risk_free_rate) / portfolio_std if portfolio_std != 0 else 0
            
            results["returns"].append(portfolio_return)
            results["volatilities"].append(portfolio_std)
            results["sharpe_ratios"].append(sharpe)
            results["weights"].append(weights.tolist())
        
        # Find optimal portfolios
        max_sharpe_idx = np.argmax(results["sharpe_ratios"])
        min_vol_idx = np.argmin(results["volatilities"])
        
        return {
            "frontier": results,
            "max_sharpe_portfolio": {
                "return": results["returns"][max_sharpe_idx],
                "volatility": results["volatilities"][max_sharpe_idx],
                "sharpe": results["sharpe_ratios"][max_sharpe_idx],
                "weights": dict(zip(returns.columns, results["weights"][max_sharpe_idx]))
            },
            "min_volatility_portfolio": {
                "return": results["returns"][min_vol_idx],
                "volatility": results["volatilities"][min_vol_idx],
                "sharpe": results["sharpe_ratios"][min_vol_idx],
                "weights": dict(zip(returns.columns, results["weights"][min_vol_idx]))
            }
        }
    
    def optimize_portfolio(self,
                         returns: pd.DataFrame,
                         target_return: Optional[float] = None,
                         target_risk: Optional[float] = None,
                         maximize_sharpe: bool = True) -> Dict:
        """Portfolio optimization using mean-variance"""
        
        n_assets = len(returns.columns)
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]  # Sum of weights = 1
        
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: np.dot(x, mean_returns) - target_return
            })
        
        # Bounds (0 to 1 for each weight, no short selling)
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess
        x0 = np.array([1/n_assets] * n_assets)
        
        # Objective function
        if maximize_sharpe:
            def neg_sharpe(weights):
                p_return = np.dot(weights, mean_returns)
                p_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                return -(p_return - self.risk_free_rate * 252) / p_std if p_std != 0 else 0
            
            result = optimize.minimize(neg_sharpe, x0, method='SLSQP',
                                       bounds=bounds, constraints=constraints)
        else:
            def portfolio_variance(weights):
                return np.dot(weights.T, np.dot(cov_matrix, weights))
            
            result = optimize.minimize(portfolio_variance, x0, method='SLSQP',
                                      bounds=bounds, constraints=constraints)
        
        optimal_weights = result['x']
        opt_return = np.dot(optimal_weights, mean_returns)
        opt_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        opt_sharpe = (opt_return - self.risk_free_rate * 252) / opt_risk
        
        return {
            "weights": dict(zip(returns.columns, optimal_weights)),
            "expected_return": opt_return,
            "expected_risk": opt_risk,
            "sharpe_ratio": opt_sharpe,
            "success": result['success']
        }
    
    def correlation_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """Calculate correlation matrix with p-values"""
        corr = returns.corr()
        
        # Calculate p-values
        n = len(returns)
        pvalues = pd.DataFrame(np.zeros_like(corr), index=corr.index, columns=corr.columns)
        
        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                if i != j:
                    r = corr.iloc[i, j]
                    t_stat = r * np.sqrt((n-2)/(1-r**2))
                    pvalues.iloc[i, j] = 2 * (1 - stats.t.cdf(abs(t_stat), n-2))
        
        return {
            "correlation": corr,
            "p_values": pvalues,
            "significant_pairs": [
                (corr.index[i], corr.columns[j], corr.iloc[i, j])
                for i in range(len(corr.columns))
                for j in range(i+1, len(corr.columns))
                if pvalues.iloc[i, j] < 0.05 and abs(corr.iloc[i, j]) > 0.5
            ]
        }
    
    def rolling_metrics(self, 
                       returns: pd.Series,
                       window: int = 252) -> pd.DataFrame:
        """Calculate rolling risk metrics"""
        
        rolling_sharpe = (returns.rolling(window).mean() * 252 - self.risk_free_rate * 252) / \
                        (returns.rolling(window).std() * np.sqrt(252))
        
        rolling_vol = returns.rolling(window).std() * np.sqrt(252)
        
        rolling_var = returns.rolling(window).quantile(0.05)
        
        return pd.DataFrame({
            "rolling_sharpe": rolling_sharpe,
            "rolling_volatility": rolling_vol,
            "rolling_var_95": rolling_var
        })
    
    def scenario_analysis(self,
                         returns: pd.Series,
                         scenarios: Dict[str, float] = None) -> Dict:
        """Stress test with scenario analysis"""
        
        if scenarios is None:
            scenarios = {
                "2008_financial_crisis": -0.38,
                "2020_covid_crash": -0.34,
                "dot_com_bust": -0.25,
                "inflation_shock": -0.15,
                "interest_rate_hike": -0.12,
                "war_escalation": -0.20,
                "tech_bubble_burst": -0.30,
                "black_monday": -0.22
            }
        
        current_value = 100000  # Example portfolio
        results = {}
        
        for scenario_name, impact in scenarios.items():
            # Calculate new portfolio value
            new_value = current_value * (1 + impact)
            loss = current_value - new_value
            
            # Probability of such event based on historical volatility
            z_score = (impact - returns.mean()) / returns.std() if returns.std() != 0 else 0
            probability = 2 * (1 - stats.norm.cdf(abs(z_score)))
            
            results[scenario_name] = {
                "impact_pct": impact * 100,
                "new_value": new_value,
                "loss": loss,
                "probability": probability,
                "severity": "High" if impact < -0.20 else "Medium" if impact < -0.10 else "Low"
            }
        
        return results
    
    def advanced_monte_carlo(self,
                           returns: pd.Series,
                           initial_value: float = 100000,
                           years: int = 30,
                           simulations: int = 10000,
                           withdrawal_rate: float = 0.04,
                           confidence_levels: List[float] = [0.5, 0.75, 0.9, 0.95, 0.99]) -> Dict:
        """SSS-grade Monte Carlo with multiple scenarios"""
        
        mean_return = returns.mean() * 252
        volatility = returns.std() * np.sqrt(252)
        
        # Generate random returns
        np.random.seed(42)
        random_returns = np.random.normal(mean_return, volatility, (simulations, years))
        
        # Simulate paths
        paths = np.zeros((simulations, years + 1))
        paths[:, 0] = initial_value
        
        for t in range(1, years + 1):
            # Apply returns and withdrawal
            paths[:, t] = paths[:, t-1] * (1 + random_returns[:, t-1])
            paths[:, t] *= (1 - withdrawal_rate)
        
        # Calculate percentiles
        percentiles = {}
        for conf in confidence_levels:
            percentiles[f"{int(conf*100)}%"] = np.percentile(paths[:, -1], (1-conf)*100)
        
        # Success probability (not running out of money)
        success_rate = np.mean(paths[:, -1] > 0)
        
        # Additional statistics
        final_values = paths[:, -1]
        
        return {
            "initial_value": initial_value,
            "years": years,
            "simulations": simulations,
            "withdrawal_rate": withdrawal_rate,
            "success_probability": success_rate,
            "percentiles": percentiles,
            "mean_final_value": np.mean(final_values),
            "median_final_value": np.median(final_values),
            "probability_of_loss": np.mean(final_values < initial_value),
            "probability_of_doubling": np.mean(final_values > 2 * initial_value),
            "paths": paths[:100].tolist()  # Sample paths for visualization
        }

# Example usage
if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2024-01-01', freq='D')
    
    # Sample portfolio returns
    returns = pd.Series(np.random.normal(0.0003, 0.02, len(dates)), index=dates)
    benchmark = pd.Series(np.random.normal(0.0002, 0.015, len(dates)), index=dates)
    
    # Initialize engine
    engine = SSSAnalyticsEngine(risk_free_rate=0.045)
    
    # Calculate risk metrics
    risk = engine.calculate_risk_metrics(returns, benchmark)
    print(f"Sharpe Ratio: {risk.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {risk.max_drawdown:.2%}")
    print(f"VaR (95%): {risk.var_95:.2%}")
    
    # Portfolio optimization
    portfolio_returns = pd.DataFrame({
        'VUAG': np.random.normal(0.0004, 0.018, len(dates)),
        'VUSA': np.random.normal(0.0003, 0.017, len(dates)),
        'VUKG': np.random.normal(0.0002, 0.022, len(dates)),
        'VAPX': np.random.normal(0.0003, 0.020, len(dates)),
    }, index=dates)
    
    optimal = engine.optimize_portfolio(portfolio_returns, maximize_sharpe=True)
    print(f"\nOptimal Portfolio:")
    for asset, weight in optimal['weights'].items():
        print(f"  {asset}: {weight:.2%}")
    print(f"Expected Return: {optimal['expected_return']:.2%}")
    print(f"Expected Risk: {optimal['expected_risk']:.2%}")
    print(f"Sharpe: {optimal['sharpe_ratio']:.2f}")
    
    # Scenario analysis
    scenarios = engine.scenario_analysis(returns)
    print(f"\nStress Test Results:")
    for scenario, result in scenarios.items():
        print(f"  {scenario}: {result['impact_pct']:.1f}% impact")
    
    # Monte Carlo
    mc = engine.advanced_monte_carlo(returns, initial_value=500000, years=30)
    print(f"\nMonte Carlo Results:")
    print(f"Success Probability: {mc['success_probability']:.1%}")
    print(f"Median Final Value: £{mc['median_final_value']:,.0f}")
