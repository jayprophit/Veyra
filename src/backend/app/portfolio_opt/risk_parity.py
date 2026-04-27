"""Risk Parity Allocator - Equal risk contribution"""
from typing import Dict, List
import statistics
import math

class RiskParityAllocator:
    """Allocate capital based on equal risk contribution"""
    
    def __init__(self):
        self.assets: List[str] = []
        self.volatilities: Dict[str, float] = {}
        self.correlations: Dict[str, Dict[str, float]] = {}
    
    def add_asset(self, symbol: str, volatility: float, 
                 correlations: Dict[str, float] = None):
        """Add asset with volatility and correlations"""
        self.assets.append(symbol)
        self.volatilities[symbol] = volatility
        if correlations:
            self.correlations[symbol] = correlations
    
    def calculate_risk_contribution(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Calculate risk contribution of each asset"""
        contributions = {}
        total_risk = 0
        
        # Calculate portfolio variance
        portfolio_var = 0
        for a1 in self.assets:
            for a2 in self.assets:
                cov = self.volatilities[a1] * self.volatilities[a2] * \
                      self.correlations.get(a1, {}).get(a2, 0)
                portfolio_var += weights[a1] * weights[a2] * cov
        
        portfolio_vol = math.sqrt(portfolio_var) if portfolio_var > 0 else 0.001
        
        # Marginal contribution to risk
        for a in self.assets:
            marginal = 0
            for b in self.assets:
                cov = self.volatilities[a] * self.volatilities[b] * \
                      self.correlations.get(a, {}).get(b, 0)
                marginal += weights[b] * cov
            
            contributions[a] = weights[a] * marginal / portfolio_vol
        
        return contributions
    
    def allocate_equal_risk(self, target_volatility: float = 0.10) -> Dict:
        """Allocate for equal risk contribution"""
        n = len(self.assets)
        if n == 0:
            return {}
        
        # Start with inverse volatility weights
        inv_vols = {a: 1/v if v > 0 else 0 for a, v in self.volatilities.items()}
        total_inv = sum(inv_vols.values())
        
        if total_inv == 0:
            return {a: 1/n for a in self.assets}
        
        weights = {a: inv_vols[a]/total_inv for a in self.assets}
        
        # Iterative optimization (simplified)
        for _ in range(10):
            risk_contrib = self.calculate_risk_contribution(weights)
            total_risk = sum(risk_contrib.values())
            
            if total_risk == 0:
                break
            
            # Adjust weights to equalize risk contribution
            target_risk = total_risk / n
            adjustments = {a: risk_contrib[a] - target_risk for a in self.assets}
            
            # Apply dampened adjustments
            for a in self.assets:
                weights[a] *= (1 - 0.1 * adjustments[a] / target_risk if target_risk > 0 else 1)
            
            # Normalize
            total = sum(weights.values())
            if total > 0:
                weights = {a: w/total for a, w in weights.items()}
        
        # Scale to target volatility
        current_vol = self._portfolio_volatility(weights)
        if current_vol > 0:
            leverage = target_volatility / current_vol
        else:
            leverage = 1.0
        
        return {
            "weights": {k: round(v, 3) for k, v in weights.items()},
            "target_volatility": target_volatility,
            "expected_volatility": round(current_vol, 3),
            "leverage": round(leverage, 2),
            "risk_contributions": {k: round(v, 4) for k, v in risk_contrib.items()},
            "equal_risk": max(abs(v - target_risk) for v in risk_contrib.values()) < target_risk * 0.1
        }
    
    def _portfolio_volatility(self, weights: Dict[str, float]) -> float:
        """Calculate portfolio volatility"""
        variance = 0
        for a1 in self.assets:
            for a2 in self.assets:
                cov = self.volatilities[a1] * self.volatilities[a2] * \
                      self.correlations.get(a1, {}).get(a2, 0)
                variance += weights[a1] * weights[a2] * cov
        
        return math.sqrt(variance) if variance > 0 else 0
    
    def compare_to_equal_weight(self) -> Dict:
        """Compare risk parity to equal weight"""
        n = len(self.assets)
        equal_weight = {a: 1/n for a in self.assets}
        
        equal_risk = self.calculate_risk_contribution(equal_weight)
        parity = self.allocate_equal_risk()
        parity_weights = {a: parity["weights"][a] for a in self.assets}
        parity_risk = parity["risk_contributions"]
        
        return {
            "equal_weight_risk_concentration": self._concentration_metric(equal_risk),
            "risk_parity_concentration": self._concentration_metric(parity_risk),
            "improvement": "BETTER" if self._concentration_metric(parity_risk) < self._concentration_metric(equal_risk) else "SIMILAR",
            "recommendation": "Use Risk Parity" if self._concentration_metric(parity_risk) < 0.5 else "Either approach"
        }
    
    def _concentration_metric(self, risk_contrib: Dict[str, float]) -> float:
        """Calculate Herfindahl-style concentration metric"""
        total = sum(risk_contrib.values())
        if total == 0:
            return 1.0
        
        shares = [v/total for v in risk_contrib.values()]
        return sum(s**2 for s in shares)
