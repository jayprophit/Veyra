"""Chaos Theory Analyzer - Butterfly effect, strange attractors in markets"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math
import statistics

@dataclass
class AttractorPoint:
    x: float  # Price
    y: float  # Volume
    z: float  # Volatility
    timestamp: int

class ChaosTheoryAnalyzer:
    """Apply chaos theory principles to market analysis"""
    
    def __init__(self):
        self.attractor_points: List[AttractorPoint] = []
        self.lyapunov_exponents: Dict[str, float] = {}
        
    def calculate_lyapunov_exponent(self, price_series: List[float], 
                                    time_delay: int = 1) -> Dict:
        """Calculate Lyapunov exponent to measure market chaos"""
        if len(price_series) < 50:
            return {"error": "Insufficient data (min 50 points)"}
        
        # Reconstruct phase space using time delay embedding
        embedded = self._time_delay_embedding(price_series, time_delay)
        
        # Calculate divergence of nearby trajectories
        divergence_rates = []
        
        for i in range(len(embedded) - 10):
            point = embedded[i]
            # Find nearest neighbor
            nearest, dist = self._find_nearest_neighbor(point, embedded[:i] + embedded[i+1:])
            
            if nearest and dist > 0:
                # Track divergence over time
                for j in range(1, min(10, len(embedded) - i)):
                    new_dist = self._euclidean_distance(embedded[i+j], embedded[nearest+j])
                    if new_dist > 0:
                        rate = math.log(new_dist / dist) / j
                        divergence_rates.append(rate)
        
        if divergence_rates:
            lyapunov = statistics.mean(divergence_rates)
        else:
            lyapunov = 0
        
        # Interpretation
        if lyapunov > 0.1:
            market_regime = "chaotic"  # Predictable short-term only
            predictability = "low"
        elif lyapunov > 0.01:
            market_regime = "weakly_chaotic"  # Some structure
            predictability = "moderate"
        else:
            market_regime = "stable"  # Trend-following works
            predictability = "high"
        
        return {
            "lyapunov_exponent": lyapunov,
            "market_regime": market_regime,
            "predictability": predictability,
            "interpretation": self._interpret_lyapunov(lyapunov),
            "trading_implication": self._trading_strategy_for_regime(market_regime)
        }
    
    def _time_delay_embedding(self, series: List[float], delay: int, 
                             dimension: int = 3) -> List[Tuple]:
        """Create phase space embedding using time delay method"""
        embedded = []
        for i in range(len(series) - (dimension - 1) * delay):
            point = tuple(series[i + j * delay] for j in range(dimension))
            embedded.append(point)
        return embedded
    
    def _find_nearest_neighbor(self, point: Tuple, candidates: List[Tuple]) -> Tuple[int, float]:
        """Find nearest neighbor in phase space"""
        min_dist = float('inf')
        nearest_idx = -1
        
        for i, candidate in enumerate(candidates):
            if len(candidate) == len(point):
                dist = self._euclidean_distance(point, candidate)
                if 0 < dist < min_dist:
                    min_dist = dist
                    nearest_idx = i
        
        return nearest_idx, min_dist
    
    def _euclidean_distance(self, p1: Tuple, p2: Tuple) -> float:
        """Calculate Euclidean distance"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))
    
    def _interpret_lyapunov(self, exponent: float) -> str:
        if exponent > 0.1:
            return "Small changes lead to large outcomes - butterfly effect active"
        elif exponent > 0:
            return "System is chaotic but with some structure"
        else:
            return "System converges to stable patterns"
    
    def _trading_strategy_for_regime(self, regime: str) -> str:
        strategies = {
            "chaotic": "Use tight stops, mean reversion, short holding periods",
            "weakly_chaotic": "Combine trend and counter-trend strategies",
            "stable": "Trend following, longer holding periods"
        }
        return strategies.get(regime, "Unknown regime")
    
    def detect_strange_attractor(self, price: List[float], 
                                volume: List[float],
                                volatility: List[float]) -> Dict:
        """Detect if market is orbiting a strange attractor"""
        if len(price) < 30:
            return {"error": "Insufficient data"}
        
        points = [AttractorPoint(p, v, vol, i) 
                 for i, (p, v, vol) in enumerate(zip(price, volume, volatility))]
        
        # Calculate center of mass
        center_x = statistics.mean(price)
        center_y = statistics.mean(volume)
        center_z = statistics.mean(volatility)
        
        # Calculate distances from center
        distances = [math.sqrt((p.x - center_x)**2 + (p.y - center_y)**2 + (p.z - center_z)**2) 
                    for p in points]
        
        # Strange attractor: points don't settle, keep orbiting
        variance = statistics.variance(distances) if len(distances) > 1 else 0
        mean_dist = statistics.mean(distances)
        
        # High variance/mean ratio indicates strange attractor
        is_strange = (variance / mean_dist) > 0.5 if mean_dist > 0 else False
        
        return {
            "strange_attractor_detected": is_strange,
            "center_of_mass": (center_x, center_y, center_z),
            "orbit_variance": variance,
            "prediction": "Market will continue complex patterns" if is_strange else "Market may stabilize",
            "trading_strategy": "Counter-trend at extremes" if is_strange else "Trend following"
        }
    
    def butterfly_effect_sensitivity(self, 
                                    initial_conditions: Dict,
                                    perturbation: float = 0.001) -> Dict:
        """Measure how sensitive market is to small changes"""
        # Simulate slight changes in initial conditions
        base_price = initial_conditions.get("price", 100)
        base_vol = initial_conditions.get("volatility", 0.2)
        
        # Small perturbation
        perturbed_price = base_price * (1 + perturbation)
        perturbed_vol = base_vol * (1 + perturbation)
        
        # Simulate outcomes (simplified)
        def simulate_outcome(price, vol, days=30):
            # Random walk with drift
            import random
            outcome = price
            for _ in range(days):
                drift = random.gauss(0, vol / math.sqrt(252))
                outcome *= (1 + drift)
            return outcome
        
        # Run multiple simulations
        base_outcomes = [simulate_outcome(base_price, base_vol) for _ in range(100)]
        perturbed_outcomes = [simulate_outcome(perturbed_price, perturbed_vol) for _ in range(100)]
        
        # Measure divergence
        divergence = abs(statistics.mean(perturbed_outcomes) - statistics.mean(base_outcomes))
        divergence_pct = divergence / base_price
        
        return {
            "initial_price": base_price,
            "perturbation": perturbation,
            "average_divergence": divergence,
            "divergence_pct": divergence_pct * 100,
            "sensitivity": "high" if divergence_pct > 0.05 else "medium" if divergence_pct > 0.02 else "low",
            "implication": "Small events can have large consequences" if divergence_pct > 0.05 else "Market is relatively stable"
        }
    
    def fractal_dimension(self, price_series: List[float]) -> Dict:
        """Calculate fractal dimension of price series"""
        # Box counting method (simplified)
        n = len(price_series)
        if n < 10:
            return {"error": "Need at least 10 data points"}
        
        max_price = max(price_series)
        min_price = min(price_series)
        price_range = max_price - min_price if max_price != min_price else 1
        
        # Count boxes at different scales
        scales = [2, 4, 8, 16]
        box_counts = []
        
        for scale in scales:
            if scale > n:
                continue
            box_size = price_range / scale
            boxes = set()
            
            for i, price in enumerate(price_series):
                x_box = i // (n // scale) if n // scale > 0 else 0
                y_box = int((price - min_price) / box_size) if box_size > 0 else 0
                boxes.add((x_box, y_box))
            
            box_counts.append((scale, len(boxes)))
        
        # Calculate dimension from slope
        if len(box_counts) >= 2:
            log_scales = [math.log(1/bc[0]) for bc in box_counts]
            log_counts = [math.log(bc[1]) for bc in box_counts]
            
            # Simple slope calculation
            if len(log_scales) > 1:
                dimension = (log_counts[-1] - log_counts[0]) / (log_scales[-1] - log_scales[0])
            else:
                dimension = 1.0
        else:
            dimension = 1.0
        
        return {
            "fractal_dimension": dimension,
            "interpretation": "random walk" if dimension > 1.4 else "trending" if dimension < 1.2 else "mixed",
            "market_structure": "efficient" if dimension > 1.5 else "predictable patterns exist"
        }
