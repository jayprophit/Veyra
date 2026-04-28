"""Smart Beta"""
from typing import Dict

class SmartBeta:
    def factor_tilt(self, market_cap_weight: float, factor_weight: float, factor_performance: float) -> Dict:
        blended_return = (market_cap_weight * 0.10) + (factor_weight * factor_performance)
        return {"expected_return": blended_return, "tilt": factor_weight}
    
    def minimum_variance(self, volatility: float, correlation: float) -> Dict:
        variance_reduction = (1 - correlation) * 0.5
        return {"expected_vol": volatility * (1 - variance_reduction), "reduction": variance_reduction}
