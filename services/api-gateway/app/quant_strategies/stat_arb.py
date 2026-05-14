"""Statistical Arbitrage - Multi-factor mean reversion"""
from typing import Dict, List
from dataclasses import dataclass
import statistics

@dataclass
class FactorExposure:
    symbol: str
    market_beta: float
    size_factor: float
    value_factor: float
    momentum_factor: float

class StatisticalArbitrage:
    """Multi-factor statistical arbitrage strategy"""
    
    def __init__(self):
        self.factors = ["market", "size", "value", "momentum", "quality"]
        self.lookback = 90
    
    def calculate_factor_exposures(self, symbol: str, 
                                   returns: List[float],
                                   factor_returns: Dict[str, List[float]]) -> FactorExposure:
        """Calculate factor exposures via regression"""
        # Simplified factor exposure calculation
        market_beta = self._calculate_beta(returns, factor_returns.get("market", []))
        
        # Other factors (simplified)
        size_factor = self._calculate_beta(returns, factor_returns.get("size", []))
        value_factor = self._calculate_beta(returns, factor_returns.get("value", []))
        momentum_factor = self._calculate_beta(returns, factor_returns.get("momentum", []))
        
        return FactorExposure(
            symbol=symbol,
            market_beta=market_beta,
            size_factor=size_factor,
            value_factor=value_factor,
            momentum_factor=momentum_factor
        )
    
    def _calculate_beta(self, stock_returns: List[float], 
                       market_returns: List[float]) -> float:
        """Calculate beta"""
        if len(stock_returns) != len(market_returns) or len(stock_returns) == 0:
            return 1.0
        
        covariance = self._calculate_covariance(stock_returns, market_returns)
        market_variance = statistics.variance(market_returns) if len(market_returns) > 1 else 0.001
        
        return covariance / market_variance if market_variance > 0 else 1.0
    
    def _calculate_covariance(self, x: List[float], y: List[float]) -> float:
        """Calculate covariance"""
        if len(x) != len(y) or len(x) == 0:
            return 0
        
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        return sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / (len(x) - 1)
    
    def find_alpha_opportunities(self, universe: List[str],
                                 prices: Dict[str, List[float]],
                                 factor_data: Dict[str, List[float]]) -> List[Dict]:
        """Find stocks with abnormal returns not explained by factors"""
        opportunities = []
        
        for symbol in universe:
            if symbol not in prices or len(prices[symbol]) < self.lookback:
                continue
            
            # Calculate returns
            symbol_prices = prices[symbol][-self.lookback:]
            returns = [(symbol_prices[i] - symbol_prices[i-1]) / symbol_prices[i-1] 
                      for i in range(1, len(symbol_prices))]
            
            # Calculate factor exposures
            exposures = self.calculate_factor_exposures(symbol, returns, factor_data)
            
            # Calculate expected return from factors
            expected_return = (
                exposures.market_beta * statistics.mean(factor_data.get("market", [0])) +
                exposures.size_factor * statistics.mean(factor_data.get("size", [0])) +
                exposures.value_factor * statistics.mean(factor_data.get("value", [0])) +
                exposures.momentum_factor * statistics.mean(factor_data.get("momentum", [0]))
            )
            
            # Calculate actual return
            actual_return = statistics.mean(returns) if returns else 0
            
            # Alpha = actual - expected
            alpha = actual_return - expected_return
            
            # If significant alpha (positive or negative)
            if abs(alpha) > 0.001:  # 0.1% daily alpha threshold
                opportunities.append({
                    "symbol": symbol,
                    "alpha_daily": round(alpha * 100, 3),  # in bps
                    "expected_return": round(expected_return * 100, 3),
                    "actual_return": round(actual_return * 100, 3),
                    "market_beta": round(exposures.market_beta, 2),
                    "signal": "LONG" if alpha > 0 else "SHORT",
                    "confidence": "HIGH" if abs(alpha) > 0.002 else "MEDIUM"
                })
        
        return sorted(opportunities, key=lambda x: abs(x["alpha_daily"]), reverse=True)
    
    def construct_factor_neutral_portfolio(self, 
                                          signals: List[Dict],
                                          target_value: float) -> Dict:
        """Construct market and factor neutral portfolio"""
        longs = [s for s in signals if s["signal"] == "LONG"][:5]
        shorts = [s for s in signals if s["signal"] == "SHORT"][:5]
        
        # Equal weight within long/short
        long_weight = target_value / 2 / len(longs) if longs else 0
        short_weight = target_value / 2 / len(shorts) if shorts else 0
        
        positions = []
        
        for signal in longs:
            positions.append({
                "symbol": signal["symbol"],
                "side": "LONG",
                "target_value": long_weight,
                "expected_alpha": signal["alpha_daily"]
            })
        
        for signal in shorts:
            positions.append({
                "symbol": signal["symbol"],
                "side": "SHORT",
                "target_value": -short_weight,
                "expected_alpha": signal["alpha_daily"]
            })
        
        # Calculate portfolio beta (should be near 0)
        port_beta = sum(
            p["target_value"] * next(s["market_beta"] for s in signals if s["symbol"] == p["symbol"])
            for p in positions
        ) / target_value
        
        return {
            "positions": positions,
            "total_long": sum(p["target_value"] for p in positions if p["side"] == "LONG"),
            "total_short": abs(sum(p["target_value"] for p in positions if p["side"] == "SHORT")),
            "portfolio_beta": round(port_beta, 3),
            "expected_daily_alpha_bps": round(
                sum(p["target_value"] * p["expected_alpha"] for p in positions) / target_value, 2
            ),
            "factor_neutral": abs(port_beta) < 0.1
        }
    
    def get_risk_decomposition(self, portfolio: List[Dict],
                              factor_cov_matrix: Dict) -> Dict:
        """Decompose portfolio risk by factor"""
        factor_risks = {}
        
        for factor in self.factors:
            if factor in factor_cov_matrix:
                # Simplified risk contribution
                factor_risks[factor] = {
                    "variance_contribution": factor_cov_matrix[factor].get("variance", 0),
                    "pct_of_total_risk": 20  # Placeholder
                }
        
        return {
            "factor_breakdown": factor_risks,
            "diversification_score": len([f for f in factor_risks if factor_risks[f]["variance_contribution"] < 0.1]),
            "concentration_risk": "HIGH" if any(f["pct_of_total_risk"] > 50 for f in factor_risks.values()) else "LOW"
        }
