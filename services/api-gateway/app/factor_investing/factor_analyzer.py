"""Factor Analyzer - Analyze stock exposure to risk factors"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class FactorExposure:
    market_beta: float
    size_factor: float  # SMB
    value_factor: float  # HML
    momentum_factor: float  # UMD
    quality_factor: float
    volatility_factor: float

@dataclass
class StockFactorData:
    symbol: str
    market_cap: float
    pe_ratio: float
    pb_ratio: float
    roe: float
    returns_12m: float
    volatility: float
    debt_to_equity: float

class FactorAnalyzer:
    """Analyze stock factor exposures"""
    
    def __init__(self):
        self.factor_premia = {
            "market": 0.05,
            "size": 0.02,
            "value": 0.03,
            "momentum": 0.04,
            "quality": 0.025,
            "low_vol": 0.015
        }
    
    def calculate_factor_exposures(self, stock: StockFactorData, 
                                  market_median_cap: float = 10e9) -> FactorExposure:
        """Calculate factor exposures for a stock"""
        
        # Market beta (simplified)
        market_beta = 1.0 if stock.market_cap > market_median_cap else 1.1
        
        # Size factor (negative for large cap, positive for small cap)
        size_factor = -1.0 if stock.market_cap > market_median_cap * 2 else \
                      0.0 if stock.market_cap > market_median_cap else 1.0
        
        # Value factor (based on P/B and P/E)
        value_score = 0
        if stock.pb_ratio < 2:
            value_score += 1
        if stock.pe_ratio < 15:
            value_score += 1
        value_factor = value_score - 1  # Center around 0
        
        # Momentum factor
        if stock.returns_12m > 0.30:
            momentum_factor = 1.5
        elif stock.returns_12m > 0.15:
            momentum_factor = 0.5
        elif stock.returns_12m < -0.15:
            momentum_factor = -1.0
        else:
            momentum_factor = 0
        
        # Quality factor (ROE, low debt)
        quality_score = 0
        if stock.roe > 0.15:
            quality_score += 1
        if stock.debt_to_equity < 0.5:
            quality_score += 1
        quality_factor = quality_score - 1
        
        # Low volatility factor
        if stock.volatility < 0.15:
            volatility_factor = -1.0  # Low vol
        elif stock.volatility > 0.30:
            volatility_factor = 1.0  # High vol
        else:
            volatility_factor = 0
        
        return FactorExposure(
            market_beta=market_beta,
            size_factor=size_factor,
            value_factor=value_factor,
            momentum_factor=momentum_factor,
            quality_factor=quality_factor,
            volatility_factor=volatility_factor
        )
    
    def calculate_factor_attribution(self, stock: StockFactorData) -> Dict:
        """Calculate expected return from factor exposures"""
        exposures = self.calculate_factor_exposures(stock)
        
        factor_returns = (
            (exposures.market_beta - 1) * self.factor_premia["market"] +
            exposures.size_factor * self.factor_premia["size"] +
            exposures.value_factor * self.factor_premia["value"] +
            exposures.momentum_factor * self.factor_premia["momentum"] +
            exposures.quality_factor * self.factor_premia["quality"] +
            exposures.volatility_factor * self.factor_premia["low_vol"]
        )
        
        return {
            "symbol": stock.symbol,
            "expected_factor_return": round(factor_returns * 100, 2),
            "exposures": {
                "market_beta": round(exposures.market_beta, 2),
                "size": round(exposures.size_factor, 2),
                "value": round(exposures.value_factor, 2),
                "momentum": round(exposures.momentum_factor, 2),
                "quality": round(exposures.quality_factor, 2),
                "low_volatility": round(-exposures.volatility_factor, 2)
            },
            "dominant_factor": self._identify_dominant_factor(exposures),
            "style_classification": self._classify_style(exposures)
        }
    
    def _identify_dominant_factor(self, exp: FactorExposure) -> str:
        """Identify the strongest factor exposure"""
        factors = {
            "value": abs(exp.value_factor),
            "momentum": abs(exp.momentum_factor),
            "quality": abs(exp.quality_factor),
            "size": abs(exp.size_factor),
            "volatility": abs(exp.volatility_factor)
        }
        return max(factors, key=factors.get)
    
    def _classify_style(self, exp: FactorExposure) -> str:
        """Classify stock by investment style"""
        if exp.value_factor > 0.5 and exp.quality_factor > 0:
            return "QUALITY_VALUE"
        elif exp.momentum_factor > 0.5:
            return "MOMENTUM_GROWTH"
        elif exp.size_factor > 0:
            return "SMALL_CAP"
        elif exp.quality_factor > 0.5:
            return "QUALITY_DEFENSIVE"
        elif exp.volatility_factor < 0:
            return "LOW_VOLATILITY"
        return "BLEND"
    
    def screen_by_factor(self, stocks: List[StockFactorData], 
                        target_factor: str,
                        min_exposure: float = 0.5) -> List[Dict]:
        """Screen stocks by factor exposure"""
        results = []
        
        for stock in stocks:
            attr = self.calculate_factor_attribution(stock)
            exposure = attr["exposures"].get(target_factor, 0)
            
            if exposure >= min_exposure:
                results.append({
                    "symbol": stock.symbol,
                    "market_cap_b": round(stock.market_cap / 1e9, 1),
                    "factor_exposure": exposure,
                    "expected_return": attr["expected_factor_return"],
                    "style": attr["style_classification"]
                })
        
        return sorted(results, key=lambda x: x["factor_exposure"], reverse=True)
