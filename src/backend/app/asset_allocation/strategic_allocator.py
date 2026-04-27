"""Strategic Allocator - Long-term asset allocation optimization"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class AssetClass:
    name: str
    expected_return: float
    volatility: float
    correlation_with_others: Dict[str, float]

class StrategicAllocator:
    """Optimize strategic asset allocation"""
    
    def __init__(self, risk_tolerance: str = "moderate"):
        self.risk_tolerance = risk_tolerance
        self.asset_classes: Dict[str, AssetClass] = {}
        self.target_allocations = {}
    
    def add_asset_class(self, asset: AssetClass):
        """Add asset class to allocation universe"""
        self.asset_classes[asset.name] = asset
    
    def get_model_portfolio(self, portfolio_type: str = "balanced") -> Dict:
        """Get model portfolio allocation based on type"""
        models = {
            "conservative": {
                "stocks": 0.30,
                "bonds": 0.50,
                "cash": 0.15,
                "alternatives": 0.05
            },
            "balanced": {
                "stocks": 0.50,
                "bonds": 0.35,
                "cash": 0.05,
                "alternatives": 0.10
            },
            "growth": {
                "stocks": 0.70,
                "bonds": 0.20,
                "cash": 0.02,
                "alternatives": 0.08
            },
            "aggressive": {
                "stocks": 0.85,
                "bonds": 0.10,
                "cash": 0.00,
                "alternatives": 0.05
            }
        }
        
        return models.get(portfolio_type, models["balanced"])
    
    def calculate_portfolio_metrics(self, allocations: Dict[str, float]) -> Dict:
        """Calculate expected return and risk for allocation"""
        if not self.asset_classes:
            return {"error": "No asset classes defined"}
        
        # Expected return
        expected_return = sum(
            allocations.get(name, 0) * asset.expected_return
            for name, asset in self.asset_classes.items()
        )
        
        # Portfolio variance (simplified - assumes correlations)
        variance = 0
        for name1, alloc1 in allocations.items():
            asset1 = self.asset_classes.get(name1)
            if not asset1:
                continue
            
            for name2, alloc2 in allocations.items():
                asset2 = self.asset_classes.get(name2)
                if not asset2:
                    continue
                
                corr = asset1.correlation_with_others.get(name2, 0.5)
                if name1 == name2:
                    corr = 1.0
                
                variance += alloc1 * alloc2 * asset1.volatility * asset2.volatility * corr
        
        volatility = variance ** 0.5
        
        # Sharpe ratio estimate (assuming 3% risk-free rate)
        sharpe = (expected_return - 0.03) / volatility if volatility > 0 else 0
        
        return {
            "expected_return": round(expected_return * 100, 2),
            "expected_volatility": round(volatility * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "risk_adjusted_return": round(expected_return / volatility, 2) if volatility > 0 else 0
        }
    
    def optimize_allocation(self, target_return: float = None, 
                             max_volatility: float = None) -> Dict:
        """Simple allocation optimization"""
        # Start with balanced portfolio
        base_allocation = self.get_model_portfolio("balanced")
        
        metrics = self.calculate_portfolio_metrics(base_allocation)
        
        # Adjust based on constraints
        if target_return and metrics["expected_return"] < target_return * 100:
            # Need more return - shift toward growth
            optimized = self.get_model_portfolio("growth")
        elif max_volatility and metrics["expected_volatility"] > max_volatility * 100:
            # Need less risk - shift toward conservative
            optimized = self.get_model_portfolio("conservative")
        else:
            optimized = base_allocation
        
        opt_metrics = self.calculate_portfolio_metrics(optimized)
        
        return {
            "optimized_allocation": optimized,
            "metrics": opt_metrics,
            "rebalancing_frequency": "QUARTERLY",
            "drift_tolerance": 0.05,
            "strategy": "STRATEGIC_ASSET_ALLOCATION"
        }
    
    def compare_allocations(self, allocations_list: List[Dict[str, float]]) -> List[Dict]:
        """Compare multiple allocation strategies"""
        results = []
        
        for i, alloc in enumerate(allocations_list):
            metrics = self.calculate_portfolio_metrics(alloc)
            results.append({
                "allocation_id": i + 1,
                "allocation": alloc,
                **metrics
            })
        
        # Rank by Sharpe ratio
        results.sort(key=lambda x: x["sharpe_ratio"], reverse=True)
        
        return results
