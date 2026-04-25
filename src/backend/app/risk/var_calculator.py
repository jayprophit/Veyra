"""VaR Calculator - Value at Risk Metrics"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class VaRMethod(Enum):
    HISTORICAL = "historical"
    PARAMETRIC = "parametric"
    MONTE_CARLO = "monte_carlo"


@dataclass
class VaRResult:
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    method: str
    confidence: float
    holding_period_days: int


class VaRCalculator:
    """Value at Risk calculation engine"""
    
    def __init__(self, method: VaRMethod = VaRMethod.HISTORICAL):
        self.method = method
        self.confidence_levels = [0.95, 0.99]
    
    def calculate(
        self,
        portfolio_returns: pd.Series,
        portfolio_value: float,
        holding_period: int = 1
    ) -> VaRResult:
        """Calculate VaR for portfolio"""
        
        if self.method == VaRMethod.HISTORICAL:
            return self._historical_var(portfolio_returns, portfolio_value, holding_period)
        elif self.method == VaRMethod.PARAMETRIC:
            return self._parametric_var(portfolio_returns, portfolio_value, holding_period)
        else:
            return self._monte_carlo_var(portfolio_returns, portfolio_value, holding_period)
    
    def _historical_var(
        self,
        returns: pd.Series,
        value: float,
        days: int
    ) -> VaRResult:
        """Historical simulation VaR"""
        var_95 = np.percentile(returns, 5) * value * np.sqrt(days)
        var_99 = np.percentile(returns, 1) * value * np.sqrt(days)
        
        cvar_95 = returns[returns <= np.percentile(returns, 5)].mean() * value * np.sqrt(days)
        cvar_99 = returns[returns <= np.percentile(returns, 1)].mean() * value * np.sqrt(days)
        
        return VaRResult(
            var_95=round(abs(var_95), 2),
            var_99=round(abs(var_99), 2),
            cvar_95=round(abs(cvar_95), 2),
            cvar_99=round(abs(cvar_99), 2),
            method="historical",
            confidence=0.95,
            holding_period_days=days
        )
    
    def _parametric_var(
        self,
        returns: pd.Series,
        value: float,
        days: int
    ) -> VaRResult:
        """Parametric (variance-covariance) VaR"""
        mu = returns.mean()
        sigma = returns.std()
        
        z_95 = 1.645
        z_99 = 2.326
        
        var_95 = (mu - z_95 * sigma) * value * np.sqrt(days)
        var_99 = (mu - z_99 * sigma) * value * np.sqrt(days)
        
        return VaRResult(
            var_95=round(abs(var_95), 2),
            var_99=round(abs(var_99), 2),
            cvar_95=round(abs(var_95 * 1.25), 2),
            cvar_99=round(abs(var_99 * 1.5), 2),
            method="parametric",
            confidence=0.95,
            holding_period_days=days
        )
    
    def _monte_carlo_var(
        self,
        returns: pd.Series,
        value: float,
        days: int,
        simulations: int = 10000
    ) -> VaRResult:
        """Monte Carlo simulation VaR"""
        mu = returns.mean()
        sigma = returns.std()
        
        simulated = np.random.normal(mu, sigma, (simulations, days))
        port_returns = np.prod(1 + simulated, axis=1) - 1
        
        var_95 = np.percentile(port_returns, 5) * value
        var_99 = np.percentile(port_returns, 1) * value
        
        return VaRResult(
            var_95=round(abs(var_95), 2),
            var_99=round(abs(var_99), 2),
            cvar_95=round(abs(port_returns[port_returns <= var_95].mean() * value), 2),
            cvar_99=round(abs(port_returns[port_returns <= var_99].mean() * value), 2),
            method="monte_carlo",
            confidence=0.95,
            holding_period_days=days
        )
