"""
Advanced Risk Analytics Engine
==============================
Goldman Sachs Marquee-level risk analytics and portfolio optimization
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from scipy import stats
from scipy.optimize import minimize
import json

logger = logging.getLogger(__name__)


class RiskMetric(Enum):
    """Risk metric types"""
    VAR = "var"  # Value at Risk
    CVAR = "cvar"  # Conditional Value at Risk
    BETA = "beta"  # Market beta
    SHARPE = "sharpe"  # Sharpe ratio
    SORTINO = "sortino"  # Sortino ratio
    TREYNOR = "treynor"  # Treynor ratio
    INFORMATION = "information"  # Information ratio
    ALPHA = "alpha"  # Alpha
    DURATION = "duration"  # Duration
    CONVEXITY = "convexity"  # Convexity
    GREEKS = "greeks"  # Option Greeks


@dataclass
class RiskFactor:
    """Risk factor definition"""
    name: str
    factor_type: str  # market, credit, liquidity, operational
    weight: float
    correlation_matrix: Optional[np.ndarray] = None
    volatilities: Optional[np.ndarray] = None


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics"""
    var_1d: float
    var_5d: float
    var_10d: float
    cvar_1d: float
    cvar_5d: float
    cvar_10d: float
    beta: float
    alpha: float
    sharpe_ratio: float
    sortino_ratio: float
    treynor_ratio: float
    information_ratio: float
    max_drawdown: float
    volatility: float
    tracking_error: float
    downside_deviation: float
    upside_capture: float
    downside_capture: float
    correlation_with_market: float
    r_squared: float
    information_coefficient: float


@dataclass
class StressTestScenario:
    """Stress test scenario definition"""
    name: str
    description: str
    market_shocks: Dict[str, float]  # Market factor shocks
    factor_correlations: Optional[Dict[str, float]] = None
    probability: float = 0.01  # Probability of occurrence
    severity: str = "medium"  # low, medium, high, extreme


class AdvancedRiskEngine:
    """Advanced risk analytics engine with institutional-grade capabilities"""
    
    def __init__(self):
        self.risk_factors: List[RiskFactor] = []
        self.market_data_cache: Dict[str, pd.DataFrame] = {}
        self.portfolio_positions: Dict[str, Dict] = {}
        self.risk_models: Dict[str, Any] = {}
        self.stress_scenarios: List[StressTestScenario] = []
        self.backtest_results: List[Dict] = []
        
        # Initialize default risk factors
        self._initialize_risk_factors()
        self._initialize_stress_scenarios()
        
    def _initialize_risk_factors(self):
        """Initialize default risk factors"""
        # Market risk factors
        self.risk_factors.extend([
            RiskFactor("equity_market", "market", 0.4),
            RiskFactor("interest_rate", "market", 0.25),
            RiskFactor("credit_spread", "market", 0.15),
            RiskFactor("commodity", "market", 0.1),
            RiskFactor("fx", "market", 0.1),
        ])
        
        # Alternative risk factors
        self.risk_factors.extend([
            RiskFactor("liquidity", "liquidity", 0.3),
            RiskFactor("volatility", "market", 0.2),
            RiskFactor("momentum", "market", 0.15),
            RiskFactor("value", "market", 0.15),
            RiskFactor("quality", "market", 0.1),
            RiskFactor("size", "market", 0.1),
        ])
        
    def _initialize_stress_scenarios(self):
        """Initialize stress test scenarios"""
        self.stress_scenarios = [
            StressTestScenario(
                name="2008_Financial_Crisis",
                description="2008 Financial Crisis scenario",
                market_shocks={
                    "equity_market": -0.4,
                    "interest_rate": -0.02,
                    "credit_spread": 0.05,
                    "volatility": 2.0,
                    "liquidity": -0.3
                },
                probability=0.005,
                severity="extreme"
            ),
            StressTestScenario(
                name="COVID_19_March_2020",
                description="COVID-19 market crash",
                market_shocks={
                    "equity_market": -0.35,
                    "volatility": 3.0,
                    "credit_spread": 0.03,
                    "liquidity": -0.25
                },
                probability=0.01,
                severity="high"
            ),
            StressTestScenario(
                name="Interest_Rate_Shock",
                description="Sudden interest rate increase",
                market_shocks={
                    "interest_rate": 0.02,
                    "bond_prices": -0.15,
                    "equity_market": -0.1,
                    "fx": 0.05
                },
                probability=0.02,
                severity="medium"
            ),
            StressTestScenario(
                name="Credit_Crisis",
                description="Credit market stress",
                market_shocks={
                    "credit_spread": 0.04,
                    "equity_market": -0.2,
                    "liquidity": -0.2
                },
                probability=0.015,
                severity="high"
            )
        ]
        
    async def calculate_comprehensive_risk_metrics(self, portfolio_data: Dict[str, Any]) -> RiskMetrics:
        """Calculate comprehensive risk metrics for portfolio"""
        try:
            # Extract portfolio returns
            returns = self._extract_portfolio_returns(portfolio_data)
            market_returns = self._get_market_returns()
            
            # Calculate basic metrics
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
            downside_returns = returns[returns < 0]
            downside_deviation = np.std(downside_returns) * np.sqrt(252)
            
            # Calculate VaR and CVaR
            var_1d = self._calculate_var(returns, confidence_level=0.95)
            var_5d = var_1d * np.sqrt(5)
            var_10d = var_1d * np.sqrt(10)
            
            cvar_1d = self._calculate_cvar(returns, confidence_level=0.95)
            cvar_5d = cvar_1d * np.sqrt(5)
            cvar_10d = cvar_1d * np.sqrt(10)
            
            # Calculate market beta and alpha
            beta, alpha = self._calculate_beta_alpha(returns, market_returns)
            
            # Calculate performance ratios
            risk_free_rate = 0.02  # 2% risk-free rate
            excess_returns = returns - risk_free_rate / 252
            
            sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
            sortino_ratio = np.mean(excess_returns) / downside_deviation if downside_deviation > 0 else 0
            treynor_ratio = np.mean(excess_returns) * 252 / beta if beta != 0 else 0
            
            # Calculate maximum drawdown
            cumulative_returns = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdown)
            
            # Calculate tracking error and information ratio
            benchmark_returns = self._get_benchmark_returns()
            tracking_error = np.std(returns - benchmark_returns) * np.sqrt(252)
            information_ratio = np.mean(returns - benchmark_returns) / tracking_error if tracking_error > 0 else 0
            
            # Calculate upside/downside capture
            upside_market_returns = market_returns[market_returns > 0]
            upside_portfolio_returns = returns[market_returns > 0]
            upside_capture = np.mean(upside_portfolio_returns) / np.mean(upside_market_returns) if np.mean(upside_market_returns) != 0 else 0
            
            downside_market_returns = market_returns[market_returns < 0]
            downside_portfolio_returns = returns[market_returns < 0]
            downside_capture = np.mean(downside_portfolio_returns) / np.mean(downside_market_returns) if np.mean(downside_market_returns) != 0 else 0
            
            # Calculate correlation and R-squared
            correlation_with_market = np.corrcoef(returns, market_returns)[0, 1]
            r_squared = correlation_with_market ** 2
            
            # Calculate information coefficient
            information_coefficient = self._calculate_information_coefficient(returns, market_returns)
            
            return RiskMetrics(
                var_1d=var_1d,
                var_5d=var_5d,
                var_10d=var_10d,
                cvar_1d=cvar_1d,
                cvar_5d=cvar_5d,
                cvar_10d=cvar_10d,
                beta=beta,
                alpha=alpha,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                treynor_ratio=treynor_ratio,
                information_ratio=information_ratio,
                max_drawdown=max_drawdown,
                volatility=volatility,
                tracking_error=tracking_error,
                downside_deviation=downside_deviation,
                upside_capture=upside_capture,
                downside_capture=downside_capture,
                correlation_with_market=correlation_with_market,
                r_squared=r_squared,
                information_coefficient=information_coefficient
            )
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            raise
            
    def _extract_portfolio_returns(self, portfolio_data: Dict[str, Any]) -> np.ndarray:
        """Extract portfolio returns from portfolio data"""
        # Mock implementation - would extract from actual portfolio data
        np.random.seed(42)
        return np.random.normal(0.0005, 0.02, 252)  # Daily returns for 1 year
        
    def _get_market_returns(self) -> np.ndarray:
        """Get market returns (e.g., S&P 500)"""
        # Mock implementation - would fetch from market data provider
        np.random.seed(123)
        return np.random.normal(0.0003, 0.015, 252)
        
    def _get_benchmark_returns(self) -> np.ndarray:
        """Get benchmark returns"""
        # Mock implementation
        return self._get_market_returns()
        
    def _calculate_var(self, returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence_level) * 100)
        
    def _calculate_cvar(self, returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var = self._calculate_var(returns, confidence_level)
        return np.mean(returns[returns <= var])
        
    def _calculate_beta_alpha(self, portfolio_returns: np.ndarray, market_returns: np.ndarray) -> Tuple[float, float]:
        """Calculate portfolio beta and alpha"""
        # Linear regression of portfolio returns vs market returns
        X = market_returns.reshape(-1, 1)
        y = portfolio_returns
        
        # Add intercept
        X_with_intercept = np.column_stack([np.ones(len(X)), X])
        
        # Calculate regression coefficients
        coefficients = np.linalg.lstsq(X_with_intercept, y, rcond=None)[0]
        alpha = coefficients[0] * 252  # Annualized alpha
        beta = coefficients[1]
        
        return beta, alpha
        
    def _calculate_information_coefficient(self, portfolio_returns: np.ndarray, market_returns: np.ndarray) -> float:
        """Calculate information coefficient (rank correlation)"""
        # Use Spearman correlation
        return stats.spearmanr(portfolio_returns, market_returns).correlation
        
    async def run_stress_tests(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive stress tests"""
        try:
            stress_results = {}
            
            for scenario in self.stress_scenarios:
                result = await self._apply_stress_scenario(portfolio_data, scenario)
                stress_results[scenario.name] = result
                
            return {
                "stress_test_results": stress_results,
                "worst_case_scenario": self._identify_worst_case(stress_results),
                "risk_concentration": self._analyze_risk_concentration(stress_results),
                "scenario_correlation": self._calculate_scenario_correlations(stress_results)
            }
            
        except Exception as e:
            logger.error(f"Error running stress tests: {e}")
            raise
            
    async def _apply_stress_scenario(self, portfolio_data: Dict[str, Any], scenario: StressTestScenario) -> Dict[str, Any]:
        """Apply stress scenario to portfolio"""
        try:
            # Calculate portfolio value under stress
            portfolio_value = portfolio_data.get("total_value", 1000000)
            stressed_value = portfolio_value
            
            # Apply market shocks
            for factor, shock in scenario.market_shocks.items():
                factor_exposure = self._get_factor_exposure(portfolio_data, factor)
                impact = factor_exposure * shock
                stressed_value *= (1 + impact)
                
            # Calculate loss and return
            loss = portfolio_value - stressed_value
            loss_percentage = loss / portfolio_value
            
            return {
                "scenario_name": scenario.name,
                "original_value": portfolio_value,
                "stressed_value": stressed_value,
                "loss": loss,
                "loss_percentage": loss_percentage,
                "probability": scenario.probability,
                "severity": scenario.severity,
                "expected_loss": loss * scenario.probability,
                "risk_contribution": self._calculate_risk_contribution(portfolio_data, scenario)
            }
            
        except Exception as e:
            logger.error(f"Error applying stress scenario {scenario.name}: {e}")
            return {"error": str(e)}
            
    def _get_factor_exposure(self, portfolio_data: Dict[str, Any], factor: str) -> float:
        """Get portfolio exposure to specific risk factor"""
        # Mock implementation - would calculate from portfolio holdings
        factor_exposures = {
            "equity_market": 0.6,
            "interest_rate": 0.2,
            "credit_spread": 0.15,
            "volatility": 0.1,
            "liquidity": 0.05,
            "bond_prices": 0.25,
            "fx": 0.1
        }
        return factor_exposures.get(factor, 0.0)
        
    def _calculate_risk_contribution(self, portfolio_data: Dict[str, Any], scenario: StressTestScenario) -> Dict[str, float]:
        """Calculate risk contribution by asset class"""
        # Mock implementation
        return {
            "equities": 0.6,
            "bonds": 0.25,
            "alternatives": 0.1,
            "cash": 0.05
        }
        
    def _identify_worst_case(self, stress_results: Dict[str, Any]) -> Dict[str, Any]:
        """Identify worst case scenario"""
        worst_case = None
        max_loss = 0
        
        for scenario_name, result in stress_results.items():
            if "error" not in result and result.get("loss_percentage", 0) > max_loss:
                max_loss = result["loss_percentage"]
                worst_case = result
                
        return worst_case or {}
        
    def _analyze_risk_concentration(self, stress_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk concentration across scenarios"""
        # Mock implementation
        return {
            "concentration_score": 0.75,
            "dominant_factors": ["equity_market", "volatility"],
            "diversification_benefit": 0.15
        }
        
    def _calculate_scenario_correlations(self, stress_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate correlations between stress scenarios"""
        # Mock implementation
        return {
            "2008_Financial_Crisis_vs_COVID_19": 0.85,
            "Interest_Rate_Shock_vs_Credit_Crisis": 0.65,
            "average_correlation": 0.75
        }
        
    async def optimize_portfolio(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Portfolio optimization using advanced techniques"""
        try:
            # Get expected returns and covariance matrix
            expected_returns = self._get_expected_returns()
            covariance_matrix = self._get_covariance_matrix()
            
            # Define optimization objective (e.g., maximize Sharpe ratio)
            def objective(weights):
                portfolio_return = np.sum(expected_returns * weights)
                portfolio_variance = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
                sharpe_ratio = portfolio_return / portfolio_variance
                return -sharpe_ratio  # Negative because we want to maximize
                
            # Define constraints
            constraints_list = [
                {"type": "eq", "fun": lambda x: np.sum(x) - 1},  # Weights sum to 1
            ]
            
            # Add user-defined constraints
            if constraints.get("max_weight"):
                constraints_list.append({
                    "type": "ineq", 
                    "fun": lambda x: constraints["max_weight"] - x
                })
                
            if constraints.get("min_weight"):
                constraints_list.append({
                    "type": "ineq", 
                    "fun": lambda x: x - constraints["min_weight"]
                })
                
            # Bounds for weights
            bounds = tuple((0, 1) for _ in range(len(expected_returns)))
            
            # Initial guess (equal weights)
            initial_weights = np.array([1/len(expected_returns)] * len(expected_returns))
            
            # Run optimization
            result = minimize(
                objective,
                initial_weights,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints_list
            )
            
            if result.success:
                optimal_weights = result.x
                
                # Calculate optimized portfolio metrics
                optimized_return = np.sum(expected_returns * optimal_weights)
                optimized_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(covariance_matrix, optimal_weights)))
                optimized_sharpe = optimized_return / optimized_risk
                
                return {
                    "success": True,
                    "optimal_weights": optimal_weights.tolist(),
                    "expected_return": optimized_return,
                    "expected_risk": optimized_risk,
                    "sharpe_ratio": optimized_sharpe,
                    "optimization_details": {
                        "iterations": result.nit,
                        "message": result.message,
                        "objective_value": -result.fun
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.message
                }
                
        except Exception as e:
            logger.error(f"Error in portfolio optimization: {e}")
            return {"success": False, "error": str(e)}
            
    def _get_expected_returns(self) -> np.ndarray:
        """Get expected returns for optimization"""
        # Mock implementation - would calculate from historical data
        return np.array([0.08, 0.06, 0.10, 0.04, 0.12])  # Expected returns for 5 assets
        
    def _get_covariance_matrix(self) -> np.ndarray:
        """Get covariance matrix for optimization"""
        # Mock implementation - would calculate from historical data
        return np.array([
            [0.04, 0.02, 0.03, 0.01, 0.02],
            [0.02, 0.03, 0.02, 0.01, 0.01],
            [0.03, 0.02, 0.05, 0.02, 0.03],
            [0.01, 0.01, 0.02, 0.02, 0.01],
            [0.02, 0.01, 0.03, 0.01, 0.06]
        ])
        
    async def calculate_risk_attribution(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk attribution by component"""
        try:
            # Calculate total portfolio risk
            total_risk = self._calculate_portfolio_risk(portfolio_data)
            
            # Calculate component contributions
            component_contributions = {}
            components = ["equities", "bonds", "alternatives", "cash", "derivatives"]
            
            for component in components:
                contribution = self._calculate_component_risk(portfolio_data, component)
                component_contributions[component] = {
                    "absolute_risk": contribution,
                    "percentage_risk": contribution / total_risk if total_risk > 0 else 0,
                    "marginal_risk": self._calculate_marginal_risk(portfolio_data, component)
                }
                
            return {
                "total_portfolio_risk": total_risk,
                "component_contributions": component_contributions,
                "risk_budget_analysis": self._analyze_risk_budget(component_contributions),
                "diversification_ratio": self._calculate_diversification_ratio(portfolio_data)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk attribution: {e}")
            raise
            
    def _calculate_portfolio_risk(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate total portfolio risk"""
        # Mock implementation
        return 0.15  # 15% annualized volatility
        
    def _calculate_component_risk(self, portfolio_data: Dict[str, Any], component: str) -> float:
        """Calculate risk contribution of specific component"""
        # Mock implementation
        component_risks = {
            "equities": 0.08,
            "bonds": 0.04,
            "alternatives": 0.03,
            "cash": 0.005,
            "derivatives": 0.02
        }
        return component_risks.get(component, 0.0)
        
    def _calculate_marginal_risk(self, portfolio_data: Dict[str, Any], component: str) -> float:
        """Calculate marginal risk of component"""
        # Mock implementation
        return 0.001
        
    def _analyze_risk_budget(self, contributions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk budget vs actual risk"""
        # Mock implementation
        return {
            "budget_utilization": 0.85,
            "over_budget_components": ["equities"],
            "under_budget_components": ["cash", "bonds"],
            "recommendations": ["Reduce equity exposure", "Increase bond allocation"]
        }
        
    def _calculate_diversification_ratio(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate diversification ratio"""
        # Mock implementation
        return 1.25
        
    async def generate_risk_report(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        try:
            # Calculate all risk metrics
            risk_metrics = await self.calculate_comprehensive_risk_metrics(portfolio_data)
            stress_test_results = await self.run_stress_tests(portfolio_data)
            risk_attribution = await self.calculate_risk_attribution(portfolio_data)
            
            # Generate risk score
            risk_score = self._calculate_overall_risk_score(risk_metrics, stress_test_results)
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(risk_metrics, stress_test_results, risk_attribution)
            
            return {
                "report_timestamp": datetime.now().isoformat(),
                "portfolio_summary": {
                    "total_value": portfolio_data.get("total_value", 0),
                    "risk_score": risk_score,
                    "risk_grade": self._get_risk_grade(risk_score),
                    "overall_assessment": self._get_risk_assessment(risk_score)
                },
                "risk_metrics": risk_metrics,
                "stress_test_results": stress_test_results,
                "risk_attribution": risk_attribution,
                "recommendations": recommendations,
                "regulatory_compliance": self._check_regulatory_compliance(risk_metrics),
                "risk_limits": self._check_risk_limits(risk_metrics, portfolio_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
            raise
            
    def _calculate_overall_risk_score(self, risk_metrics: RiskMetrics, stress_results: Dict[str, Any]) -> float:
        """Calculate overall risk score (0-100)"""
        # Component scores
        var_score = min(100, risk_metrics.var_10d * 1000)  # VaR score
        volatility_score = min(100, risk_metrics.volatility * 100)  # Volatility score
        drawdown_score = min(100, abs(risk_metrics.max_drawdown) * 200)  # Drawdown score
        sharpe_score = max(0, 100 - risk_metrics.sharpe_ratio * 10)  # Sharpe score (inverted)
        
        # Stress test score
        worst_case_loss = 0
        for result in stress_results.get("stress_test_results", {}).values():
            if "loss_percentage" in result:
                worst_case_loss = max(worst_case_loss, result["loss_percentage"])
        stress_score = min(100, worst_case_loss * 100)
        
        # Weighted average
        overall_score = (
            var_score * 0.25 +
            volatility_score * 0.2 +
            drawdown_score * 0.2 +
            sharpe_score * 0.15 +
            stress_score * 0.2
        )
        
        return overall_score
        
    def _get_risk_grade(self, risk_score: float) -> str:
        """Get risk grade based on score"""
        if risk_score < 20:
            return "A+ (Very Low Risk)"
        elif risk_score < 40:
            return "A (Low Risk)"
        elif risk_score < 60:
            return "B (Medium Risk)"
        elif risk_score < 80:
            return "C (High Risk)"
        else:
            return "D (Very High Risk)"
            
    def _get_risk_assessment(self, risk_score: float) -> str:
        """Get risk assessment description"""
        if risk_score < 20:
            return "Portfolio exhibits very low risk characteristics with excellent risk-adjusted returns."
        elif risk_score < 40:
            return "Portfolio demonstrates low risk with good diversification and moderate volatility."
        elif risk_score < 60:
            return "Portfolio shows moderate risk levels with balanced risk-return profile."
        elif risk_score < 80:
            return "Portfolio has elevated risk levels requiring active risk management."
        else:
            return "Portfolio exhibits high risk characteristics requiring immediate attention."
            
    def _generate_risk_recommendations(self, risk_metrics: RiskMetrics, stress_results: Dict[str, Any], 
                                      attribution: Dict[str, Any]) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        # VaR recommendations
        if risk_metrics.var_10d > 0.05:
            recommendations.append("Consider reducing position sizes to lower 10-day VaR below 5%")
            
        # Volatility recommendations
        if risk_metrics.volatility > 0.2:
            recommendations.append("Portfolio volatility is high (>20%). Consider adding defensive assets.")
            
        # Drawdown recommendations
        if risk_metrics.max_drawdown < -0.2:
            recommendations.append("Maximum drawdown exceeds 20%. Implement tighter risk controls.")
            
        # Sharpe ratio recommendations
        if risk_metrics.sharpe_ratio < 0.5:
            recommendations.append("Low Sharpe ratio indicates suboptimal risk-adjusted returns.")
            
        # Stress test recommendations
        worst_case = stress_results.get("worst_case_scenario", {})
        if worst_case.get("loss_percentage", 0) > 0.3:
            recommendations.append("Stress test shows potential losses >30%. Review portfolio composition.")
            
        # Concentration recommendations
        concentration = attribution.get("risk_budget_analysis", {})
        if concentration.get("budget_utilization", 0) > 0.9:
            recommendations.append("Risk budget utilization is high. Consider diversification.")
            
        return recommendations
        
    def _check_regulatory_compliance(self, risk_metrics: RiskMetrics) -> Dict[str, Any]:
        """Check regulatory compliance"""
        return {
            "sox_compliant": risk_metrics.var_10d < 0.1,
            "basel_iii_compliant": risk_metrics.var_1d < 0.02,
            "risk_limits_compliant": risk_metrics.volatility < 0.25,
            "leverage_compliant": True,  # Would check actual leverage
            "liquidity_compliant": True  # Would check liquidity ratios
        }
        
    def _check_risk_limits(self, risk_metrics: RiskMetrics, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check against internal risk limits"""
        limits = {
            "max_var_10d": 0.05,
            "max_volatility": 0.2,
            "max_drawdown": 0.15,
            "min_sharpe": 0.5
        }
        
        return {
            "var_limit_breached": risk_metrics.var_10d > limits["max_var_10d"],
            "volatility_limit_breached": risk_metrics.volatility > limits["max_volatility"],
            "drawdown_limit_breached": abs(risk_metrics.max_drawdown) > limits["max_drawdown"],
            "sharpe_limit_breached": risk_metrics.sharpe_ratio < limits["min_sharpe"],
            "overall_compliance": all([
                risk_metrics.var_10d <= limits["max_var_10d"],
                risk_metrics.volatility <= limits["max_volatility"],
                abs(risk_metrics.max_drawdown) <= limits["max_drawdown"],
                risk_metrics.sharpe_ratio >= limits["min_sharpe"]
            ])
        }


# Global advanced risk engine instance
_advanced_risk_engine = None

def get_advanced_risk_engine() -> AdvancedRiskEngine:
    """Get the global advanced risk engine instance"""
    global _advanced_risk_engine
    if _advanced_risk_engine is None:
        _advanced_risk_engine = AdvancedRiskEngine()
    return _advanced_risk_engine
