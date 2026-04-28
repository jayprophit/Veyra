"""Pair Analyzer - Find and analyze cointegrated pairs for stat arb"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
import statistics
import math

@dataclass
class PriceSeries:
    symbol: str
    prices: List[float]
    timestamps: List[float]

class PairAnalyzer:
    """Analyze pairs for cointegration and spread trading"""
    
    def __init__(self):
        self.pairs_db: Dict[str, Dict] = {}
    
    def calculate_correlation(self, series1: List[float], series2: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(series1) != len(series2) or len(series1) < 2:
            return 0
        
        n = len(series1)
        mean1 = statistics.mean(series1)
        mean2 = statistics.mean(series2)
        
        numerator = sum((x - mean1) * (y - mean2) for x, y in zip(series1, series2))
        
        sum_sq1 = sum((x - mean1) ** 2 for x in series1)
        sum_sq2 = sum((y - mean2) ** 2 for y in series2)
        
        denominator = math.sqrt(sum_sq1 * sum_sq2)
        
        return numerator / denominator if denominator > 0 else 0
    
    def calculate_cointegration_test(self, series1: List[float], 
                                      series2: List[float]) -> Dict:
        """Simplified cointegration test (Engle-Granger style)"""
        if len(series1) != len(series2) or len(series1) < 30:
            return {"cointegrated": False, "error": "Insufficient data"}
        
        # Step 1: Run OLS regression (simplified)
        # y = alpha + beta * x + error
        mean1 = statistics.mean(series1)
        mean2 = statistics.mean(series2)
        
        # Calculate beta (hedge ratio)
        numerator = sum((x - mean1) * (y - mean2) for x, y in zip(series1, series2))
        denominator = sum((x - mean1) ** 2 for x in series1)
        
        beta = numerator / denominator if denominator != 0 else 1.0
        alpha = mean2 - beta * mean1
        
        # Step 2: Calculate residuals (spread)
        residuals = [y - (alpha + beta * x) for x, y in zip(series1, series2)]
        
        # Step 3: Test for stationarity of residuals (simplified ADF-like test)
        # Calculate half-life of mean reversion
        residual_changes = [residuals[i] - residuals[i-1] for i in range(1, len(residuals))]
        lagged_residuals = residuals[:-1]
        
        if not lagged_residuals or not residual_changes:
            return {"cointegrated": False}
        
        # Simple regression of delta(residual) on lagged residual
        mean_lag = statistics.mean(lagged_residuals)
        mean_delta = statistics.mean(residual_changes)
        
        num = sum((lag - mean_lag) * (delta - mean_delta) 
                  for lag, delta in zip(lagged_residuals, residual_changes))
        den = sum((lag - mean_lag) ** 2 for lag in lagged_residuals)
        
        theta = num / den if den != 0 else 0
        half_life = -math.log(2) / theta if theta < 0 else float('inf')
        
        # Cointegration criteria
        is_cointegrated = (
            abs(beta) > 0.3 and  # Meaningful hedge ratio
            half_life < 60 and   # Mean reverts within reasonable time
            half_life > 1        # Not too fast (noise)
        )
        
        # Calculate current z-score
        residual_mean = statistics.mean(residuals)
        residual_std = statistics.stdev(residuals) if len(residuals) > 1 else 1
        current_z = (residuals[-1] - residual_mean) / residual_std if residual_std > 0 else 0
        
        return {
            "cointegrated": is_cointegrated,
            "hedge_ratio": round(beta, 4),
            "alpha": round(alpha, 4),
            "half_life_days": round(half_life, 1) if half_life != float('inf') else "INF",
            "current_z_score": round(current_z, 2),
            "residual_volatility": round(residual_std, 4),
            "signal": "LONG_SPREAD" if current_z < -2 else "SHORT_SPREAD" if current_z > 2 else "NEUTRAL",
            "confidence": "HIGH" if abs(current_z) > 2.5 else "MODERATE" if abs(current_z) > 1.5 else "LOW"
        }
    
    def analyze_pair(self, series1: PriceSeries, series2: PriceSeries) -> Dict:
        """Complete pair analysis"""
        # Ensure same length
        min_len = min(len(series1.prices), len(series2.prices))
        prices1 = series1.prices[-min_len:]
        prices2 = series2.prices[-min_len:]
        
        # Calculate correlation
        correlation = self.calculate_correlation(prices1, prices2)
        
        # Cointegration test
        coint_result = self.calculate_cointegration_test(prices1, prices2)
        
        # Calculate spread history
        if coint_result.get("hedge_ratio"):
            hedge_ratio = coint_result["hedge_ratio"]
            spread = [y - hedge_ratio * x for x, y in zip(prices1, prices2)]
            
            # Calculate spread statistics
            spread_mean = statistics.mean(spread)
            spread_std = statistics.stdev(spread) if len(spread) > 1 else 0
            
            # Historical min/max z-scores
            z_scores = [(s - spread_mean) / spread_std for s in spread] if spread_std > 0 else []
            
            if z_scores:
                coint_result["z_score_range"] = {
                    "min": round(min(z_scores), 2),
                    "max": round(max(z_scores), 2)
                }
        
        return {
            "pair": f"{series1.symbol}-{series2.symbol}",
            "correlation": round(correlation, 4),
            "correlation_strength": "STRONG" if abs(correlation) > 0.8 else "MODERATE" if abs(correlation) > 0.6 else "WEAK",
            **coint_result
        }
    
    def find_cointegrated_pairs(self, price_data: Dict[str, List[float]], 
                                 min_correlation: float = 0.7) -> List[Dict]:
        """Find all cointegrated pairs from universe"""
        symbols = list(price_data.keys())
        cointegrated_pairs = []
        
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                series1 = PriceSeries(sym1, price_data[sym1], [])
                series2 = PriceSeries(sym2, price_data[sym2], [])
                
                result = self.analyze_pair(series1, series2)
                
                if result.get("cointegrated") and result.get("correlation", 0) >= min_correlation:
                    cointegrated_pairs.append(result)
        
        # Sort by half-life (shorter = better for trading)
        cointegrated_pairs.sort(
            key=lambda x: x.get("half_life_days", float('inf')) 
            if isinstance(x.get("half_life_days"), (int, float)) else float('inf')
        )
        
        return cointegrated_pairs
    
    def calculate_position_sizes(self, pair_analysis: Dict, 
                                 capital: float,
                                 target_volatility: float = 0.02) -> Dict:
        """Calculate position sizes for pair trade"""
        if not pair_analysis.get("cointegrated"):
            return {"error": "Pair not cointegrated"}
        
        hedge_ratio = pair_analysis["hedge_ratio"]
        residual_vol = pair_analysis["residual_volatility"]
        
        # Position sizing based on volatility targeting
        if residual_vol > 0:
            position_scale = target_volatility / residual_vol
        else:
            position_scale = 1.0
        
        # Split capital
        capital_per_leg = (capital * position_scale) / 2
        
        return {
            "pair": pair_analysis["pair"],
            "capital_allocated": round(capital * position_scale, 2),
            "leg1_notional": round(capital_per_leg, 2),
            "leg2_notional": round(capital_per_leg * abs(hedge_ratio), 2),
            "hedge_ratio": hedge_ratio,
            "target_volatility": target_volatility,
            "expected_half_life": pair_analysis.get("half_life_days", "N/A"),
            "current_signal": pair_analysis.get("signal", "NEUTRAL")
        }
