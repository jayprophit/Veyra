"""Correlation Analyzer - Calculate and analyze asset correlations"""
from typing import Dict, List
from dataclasses import dataclass
import statistics
import math

@dataclass
class AssetReturns:
    symbol: str
    asset_class: str
    returns: List[float]  # Periodic returns (e.g., daily, monthly)

class CorrelationAnalyzer:
    """Analyze correlations between assets"""
    
    def __init__(self):
        self.assets: Dict[str, AssetReturns] = {}
    
    def add_asset(self, asset: AssetReturns):
        """Add asset return data"""
        self.assets[asset.symbol] = asset
    
    def calculate_correlation(self, symbol1: str, symbol2: str) -> Dict:
        """Calculate Pearson correlation coefficient between two assets"""
        if symbol1 not in self.assets or symbol2 not in self.assets:
            return {"error": "Asset data not found"}
        
        returns1 = self.assets[symbol1].returns
        returns2 = self.assets[symbol2].returns
        
        # Ensure same length
        min_len = min(len(returns1), len(returns2))
        returns1 = returns1[:min_len]
        returns2 = returns2[:min_len]
        
        if len(returns1) < 2:
            return {"error": "Insufficient data points"}
        
        # Calculate means
        mean1 = statistics.mean(returns1)
        mean2 = statistics.mean(returns2)
        
        # Calculate covariance and variances
        covariance = sum((r1 - mean1) * (r2 - mean2) for r1, r2 in zip(returns1, returns2))
        
        var1 = sum((r - mean1) ** 2 for r in returns1)
        var2 = sum((r - mean2) ** 2 for r in returns2)
        
        if var1 == 0 or var2 == 0:
            return {"error": "Zero variance in returns"}
        
        correlation = covariance / math.sqrt(var1 * var2)
        
        # Interpret correlation strength
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            strength = "VERY_STRONG"
        elif abs_corr >= 0.6:
            strength = "STRONG"
        elif abs_corr >= 0.4:
            strength = "MODERATE"
        elif abs_corr >= 0.2:
            strength = "WEAK"
        else:
            strength = "VERY_WEAK"
        
        return {
            "symbol1": symbol1,
            "symbol2": symbol2,
            "correlation": round(correlation, 4),
            "correlation_pct": round(correlation * 100, 2),
            "strength": strength,
            "direction": "POSITIVE" if correlation > 0 else "NEGATIVE" if correlation < 0 else "NONE",
            "diversification_value": "LOW" if abs_corr > 0.8 else "MODERATE" if abs_corr > 0.5 else "HIGH",
            "sample_size": len(returns1)
        }
    
    def build_correlation_matrix(self) -> Dict:
        """Build full correlation matrix for all assets"""
        symbols = list(self.assets.keys())
        n = len(symbols)
        
        if n < 2:
            return {"error": "Need at least 2 assets for matrix"}
        
        matrix = {}
        
        for i, sym1 in enumerate(symbols):
            matrix[sym1] = {}
            for j, sym2 in enumerate(symbols):
                if i == j:
                    matrix[sym1][sym2] = 1.0
                elif i < j:
                    corr_data = self.calculate_correlation(sym1, sym2)
                    matrix[sym1][sym2] = corr_data.get("correlation", 0)
                else:
                    matrix[sym1][sym2] = matrix[sym2][sym1]
        
        return {
            "symbols": symbols,
            "matrix": matrix,
            "asset_classes": list(set(a.asset_class for a in self.assets.values())),
            "summary": self._summarize_matrix(matrix, symbols)
        }
    
    def _summarize_matrix(self, matrix: Dict, symbols: List[str]) -> Dict:
        """Generate summary statistics for correlation matrix"""
        correlations = []
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                correlations.append(abs(matrix[sym1][sym2]))
        
        if not correlations:
            return {}
        
        avg_correlation = statistics.mean(correlations)
        
        # Find highest and lowest correlations
        corr_pairs = []
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                corr_pairs.append((sym1, sym2, matrix[sym1][sym2]))
        
        corr_pairs.sort(key=lambda x: x[2], reverse=True)
        highest = corr_pairs[0] if corr_pairs else None
        
        corr_pairs.sort(key=lambda x: abs(x[2]))
        lowest = corr_pairs[0] if corr_pairs else None
        
        # Count by strength
        strong_positive = sum(1 for c in correlations if c >= 0.7)
        moderate = sum(1 for c in correlations if 0.4 <= c < 0.7)
        weak = sum(1 for c in correlations if c < 0.4)
        
        return {
            "average_correlation": round(avg_correlation, 4),
            "highest_correlation": {
                "pair": f"{highest[0]}-{highest[1]}",
                "value": round(highest[2], 4)
            } if highest else None,
            "lowest_correlation": {
                "pair": f"{lowest[0]}-{lowest[1]}",
                "value": round(lowest[2], 4)
            } if lowest else None,
            "distribution": {
                "strong_positive": strong_positive,
                "moderate": moderate,
                "weak": weak,
                "total_pairs": len(correlations)
            },
            "diversification_quality": "EXCELLENT" if avg_correlation < 0.3 else "GOOD" if avg_correlation < 0.5 else "FAIR" if avg_correlation < 0.7 else "POOR"
        }
    
    def find_diversification_pairs(self, target_symbol: str, 
                                   max_correlation: float = 0.5) -> List[Dict]:
        """Find assets that provide diversification for target symbol"""
        if target_symbol not in self.assets:
            return []
        
        diversifiers = []
        
        for symbol in self.assets:
            if symbol == target_symbol:
                continue
            
            corr_data = self.calculate_correlation(target_symbol, symbol)
            correlation = abs(corr_data.get("correlation", 1))
            
            if correlation <= max_correlation:
                diversifiers.append({
                    "symbol": symbol,
                    "asset_class": self.assets[symbol].asset_class,
                    "correlation": corr_data["correlation"],
                    "correlation_abs": round(correlation, 4),
                    "diversification_value": corr_data["diversification_value"]
                })
        
        return sorted(diversifiers, key=lambda x: x["correlation_abs"])
    
    def calculate_portfolio_diversification(self, portfolio_weights: Dict[str, float]) -> Dict:
        """Calculate effective diversification of weighted portfolio"""
        matrix_data = self.build_correlation_matrix()
        
        if "error" in matrix_data:
            return matrix_data
        
        matrix = matrix_data["matrix"]
        symbols = list(portfolio_weights.keys())
        
        # Calculate weighted average correlation
        weighted_corr_sum = 0
        weight_sum = 0
        
        for i, sym1 in enumerate(symbols):
            for j, sym2 in enumerate(symbols):
                if i != j:
                    weight = portfolio_weights.get(sym1, 0) * portfolio_weights.get(sym2, 0)
                    weighted_corr_sum += matrix[sym1][sym2] * weight
                    weight_sum += weight
        
        avg_weighted_correlation = weighted_corr_sum / weight_sum if weight_sum > 0 else 1
        
        # Calculate diversification ratio (1 = perfectly diversified, >1 = concentrated)
        # Simplified: inverse of average correlation
        diversification_ratio = 1 / (1 + avg_weighted_correlation)
        
        return {
            "portfolio_avg_correlation": round(avg_weighted_correlation, 4),
            "diversification_ratio": round(diversification_ratio, 4),
            "effective_positions": round(diversification_ratio * len(symbols), 1),
            "assessment": "WELL_DIVERSIFIED" if avg_weighted_correlation < 0.3 else "MODERATELY_DIVERSIFIED" if avg_weighted_correlation < 0.6 else "CONCENTRATED_RISK"
        }
