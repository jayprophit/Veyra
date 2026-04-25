"""RL Optimizer"""
import numpy as np

class RLOptimizer:
    """RL portfolio optimizer"""
    
    def __init__(self, n_assets: int):
        self.n = n_assets
        self.weights = np.ones(n_assets) / n_assets
    
    def optimize(self, returns: np.ndarray) -> dict:
        """Train and optimize"""
        # Simplified RL: momentum-based allocation
        momentum = returns.mean(axis=0) / (returns.std(axis=0) + 1e-8)
        weights = np.exp(momentum)
        weights = weights / weights.sum()
        return {
            "weights": weights.tolist(),
            "expected_return": float(returns.mean() @ weights),
            "sharpe": float((returns.mean() @ weights) / (returns.std() + 1e-8))
        }
