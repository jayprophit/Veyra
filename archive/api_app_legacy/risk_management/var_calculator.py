"""VaR Calculator - Value at Risk and CVaR calculations"""
from typing import Dict, List
from dataclasses import dataclass
import statistics
import math

@dataclass
class VaRResult:
    confidence_level: float
    time_horizon: int  # days
    var_amount: float
    var_pct: float
    cvar_amount: float  # Conditional VaR (expected shortfall)
    method: str

class VaRCalculator:
    """Calculate Value at Risk for portfolios"""
    
    def __init__(self):
        self.confidence_levels = [0.95, 0.99]
        self.methods = ["historical", "parametric", "monte_carlo"]
    
    def calculate_historical_var(self, portfolio_value: float,
                                 historical_returns: List[float],
                                 confidence: float = 0.95,
                                 days: int = 1) -> VaRResult:
        """Calculate VaR using historical simulation"""
        if not historical_returns:
            return None
        
        # Sort returns
        sorted_returns = sorted(historical_returns)
        
        # Find percentile
        percentile = (1 - confidence) * 100
        index = int(len(sorted_returns) * (1 - confidence))
        
        var_return = sorted_returns[max(0, index)]
        
        # Scale for days
        var_return_scaled = var_return * math.sqrt(days)
        
        # Calculate VaR
        var_amount = portfolio_value * abs(var_return_scaled)
        var_pct = abs(var_return_scaled) * 100
        
        # CVaR (average of returns beyond VaR)
        tail_returns = sorted_returns[:index] if index > 0 else [var_return]
        cvar_return = statistics.mean(tail_returns) if tail_returns else var_return
        cvar_amount = portfolio_value * abs(cvar_return) * math.sqrt(days)
        
        return VaRResult(
            confidence_level=confidence,
            time_horizon=days,
            var_amount=round(var_amount, 2),
            var_pct=round(var_pct, 2),
            cvar_amount=round(cvar_amount, 2),
            method="historical"
        )
    
    def calculate_parametric_var(self, portfolio_value: float,
                                 historical_returns: List[float],
                                 confidence: float = 0.95,
                                 days: int = 1) -> VaRResult:
        """Calculate VaR using parametric (variance-covariance) method"""
        if len(historical_returns) < 2:
            return None
        
        mean = statistics.mean(historical_returns)
        std = statistics.stdev(historical_returns)
        
        # Z-score for confidence level
        z_scores = {0.95: 1.645, 0.99: 2.326}
        z = z_scores.get(confidence, 1.645)
        
        # VaR
        var_return = -(mean - z * std)  # Negative for loss
        var_return_scaled = var_return * math.sqrt(days)
        
        var_amount = portfolio_value * abs(var_return_scaled)
        var_pct = abs(var_return_scaled) * 100
        
        # CVaR for normal distribution
        cvar_return = -(mean - std * (math.exp(-z*z/2) / (math.sqrt(2*math.pi) * (1-confidence))))
        cvar_amount = portfolio_value * abs(cvar_return) * math.sqrt(days)
        
        return VaRResult(
            confidence_level=confidence,
            time_horizon=days,
            var_amount=round(var_amount, 2),
            var_pct=round(var_pct, 2),
            cvar_amount=round(cvar_amount, 2),
            method="parametric"
        )
    
    def calculate_component_var(self, portfolio_value: float,
                                positions: Dict[str, float],
                                returns_data: Dict[str, List[float]]) -> Dict:
        """Calculate VaR contribution by position"""
        component_vars = {}
        
        for symbol, weight in positions.items():
            if symbol not in returns_data:
                continue
            
            returns = returns_data[symbol]
            position_value = portfolio_value * weight
            
            var_result = self.calculate_historical_var(
                position_value, returns, confidence=0.95, days=1
            )
            
            if var_result:
                component_vars[symbol] = {
                    "position_value": position_value,
                    "weight_pct": round(weight * 100, 2),
                    "var_amount": var_result.var_amount,
                    "var_pct_of_portfolio": round(var_result.var_amount / portfolio_value * 100, 2)
                }
        
        # Total portfolio VaR
        total_var = sum(v["var_amount"] for v in component_vars.values())
        
        return {
            "component_var": component_vars,
            "total_portfolio_var": round(total_var, 2),
            "diversification_benefit": "Present" if total_var < portfolio_value * 0.02 else "Limited",
            "concentration_risk": self._identify_concentration(component_vars, portfolio_value)
        }
    
    def _identify_concentration(self, component_vars: Dict, 
                                portfolio_value: float) -> List[str]:
        """Identify concentrated positions"""
        alerts = []
        
        for symbol, data in component_vars.items():
            if data["var_pct_of_portfolio"] > 5:  # >5% VaR contribution
                alerts.append(f"{symbol}: {data['var_pct_of_portfolio']:.1f}% of portfolio risk")
        
        return alerts
    
    def var_backtest(self, historical_returns: List[float],
                    var_results: List[float],
                    confidence: float = 0.95) -> Dict:
        """Backtest VaR model"""
        exceptions = sum(1 for actual, var in zip(historical_returns, var_results) 
                        if actual < -var)
        
        total = len(historical_returns)
        exception_rate = exceptions / total if total > 0 else 0
        expected_exceptions = (1 - confidence)
        
        # Kupiec test
        ratio = exception_rate / expected_exceptions if expected_exceptions > 0 else 0
        
        return {
            "total_observations": total,
            "exceptions": exceptions,
            "exception_rate": round(exception_rate * 100, 2),
            "expected_rate": round(expected_exceptions * 100, 2),
            "test_result": "PASS" if 0.5 < ratio < 1.5 else "FAIL",
            "model_accuracy": "GOOD" if 0.8 < ratio < 1.2 else "POOR"
        }
    
    def get_risk_report(self, portfolio_value: float,
                       historical_returns: List[float]) -> Dict:
        """Generate comprehensive risk report"""
        # Calculate multiple VaR measures
        var_95_1d = self.calculate_historical_var(portfolio_value, historical_returns, 0.95, 1)
        var_99_1d = self.calculate_historical_var(portfolio_value, historical_returns, 0.99, 1)
        var_95_10d = self.calculate_historical_var(portfolio_value, historical_returns, 0.95, 10)
        
        # Parametric for comparison
        var_parametric = self.calculate_parametric_var(portfolio_value, historical_returns, 0.95, 1)
        
        return {
            "portfolio_value": portfolio_value,
            "risk_metrics": {
                "var_95_1d": var_95_1d.var_amount if var_95_1d else 0,
                "var_99_1d": var_99_1d.var_amount if var_99_1d else 0,
                "var_95_10d": var_95_10d.var_amount if var_95_10d else 0,
                "cvar_95": var_95_1d.cvar_amount if var_95_1d else 0
            },
            "risk_as_pct": {
                "daily_var_95": var_95_1d.var_pct if var_95_1d else 0,
                "daily_var_99": var_99_1d.var_pct if var_99_1d else 0,
                "ten_day_var_95": var_95_10d.var_pct if var_95_10d else 0
            },
            "method_comparison": {
                "historical_var": var_95_1d.var_amount if var_95_1d else 0,
                "parametric_var": var_parametric.var_amount if var_parametric else 0
            },
            "interpretation": f"With 95% confidence, portfolio will not lose more than ${var_95_1d.var_amount:,.0f} in 1 day"
        }
