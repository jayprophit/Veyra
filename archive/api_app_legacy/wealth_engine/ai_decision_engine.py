"""AI Decision Engine - ML-powered strategy selection"""
from typing import Dict, List, Optional
import random

class AIDecisionEngine:
    """Selects optimal allocator based on ML analysis"""
    
    ALLOCATORS = {
        'conservative': 'ConservativePreservationAllocator',
        'adaptive': 'AdaptiveAllocator',
        'multi_pot': 'MultiPotAllocator',
        'holistic': 'HolisticOrchestrator',
        'aggressive': 'AggressiveGrowthAllocator'
    }
    
    def __init__(self):
        self.market_data = {}
        self.user_history = {}
    
    def select_allocator(self, profile, amount: float, market_conditions: Dict) -> str:
        """ML-based allocator selection"""
        scores = {}
        
        # Score each allocator based on fit
        for name, allocator_class in self.ALLOCATORS.items():
            score = self._calculate_fit(name, profile, amount, market_conditions)
            scores[name] = score
        
        # Select best or blend
        best = max(scores, key=scores.get)
        
        # If scores close, suggest blend
        top_two = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
        if top_two[0][1] - top_two[1][1] < 0.1:
            return f"blend:{top_two[0][0]},{top_two[1][1]}"
        
        return best
    
    def _calculate_fit(self, name: str, profile, amount: float, conditions: Dict) -> float:
        """Calculate how well allocator fits situation"""
        score = 0.5
        
        # Capital fit
        ranges = {
            'conservative': (1, 10000),
            'adaptive': (10, float('inf')),
            'multi_pot': (500, float('inf')),
            'holistic': (100, float('inf')),
            'aggressive': (200, float('inf'))
        }
        min_c, max_c = ranges[name]
        if min_c <= profile.current_capital < max_c if max_c != float('inf') else min_c <= profile.current_capital:
            score += 0.2
        
        # Risk tolerance fit
        if name == 'conservative' and profile.risk_tolerance == 'conservative':
            score += 0.3
        elif name == 'aggressive' and profile.risk_tolerance == 'aggressive':
            score += 0.3
        elif name in ['adaptive', 'holistic'] and profile.risk_tolerance == 'moderate':
            score += 0.3
        
        # Market conditions
        volatility = conditions.get('volatility', 0.5)
        if name == 'conservative' and volatility > 0.7:
            score += 0.2
        elif name == 'aggressive' and volatility < 0.3:
            score += 0.2
        
        return min(1.0, score)
    
    def blend_allocations(self, alloc1: Dict, alloc2: Dict, weights: List[float]) -> Dict:
        """Blend two allocator outputs"""
        w1, w2 = weights
        
        blended = {
            'strategy': f"blend:{alloc1['strategy']},{alloc2['strategy']}",
            'allocations': [],
            'expected_return_annual': alloc1['expected_return_annual'] * w1 + alloc2['expected_return_annual'] * w2,
            'risk_score': alloc1['risk_score'] * w1 + alloc2['risk_score'] * w2,
            'confidence': min(alloc1['confidence'], alloc2['confidence'])
        }
        
        return blended
