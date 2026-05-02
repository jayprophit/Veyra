"""Adaptive Threshold Allocator"""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class Threshold(Enum):
    MICRO = (0, 25, ['savings', 'premium_bonds'])
    SMALL = (25, 100, ['savings', 'bonds', 'gold_micro', 'crypto_stake'])
    MEDIUM = (100, 500, ['savings', 'gold', 'p2p', 'index', 'grid_bot'])
    GROWTH = (500, 2000, ['savings', 'gold', 'p2p', 'index', 'grid', 'arb'])
    SCALE = (2000, 10000, ['savings', 'gold', 'p2p', 'index', 'grid', 'arb', 'options'])
    WEALTH = (10000, float('inf'), ['savings', 'gold', 'p2p', 'index', 'grid', 'arb', 'options', 'wine', 'art'])

class AdaptiveAllocator:
    """Allocates based on capital thresholds, handles random contributions"""
    
    def __init__(self, capital: float = 0):
        self.capital = capital
        self.threshold = self._get_threshold()
        
    def _get_threshold(self) -> Threshold:
        for t in Threshold:
            min_c, max_c, _ = t.value
            if min_c <= self.capital < max_c:
                return t
        return Threshold.WEALTH
    
    def process_contribution(self, amount: float, source: str = 'regular') -> Dict:
        """Process any contribution amount"""
        old_capital = self.capital
        self.capital += amount
        old_thresh = self._get_threshold_from_capital(old_capital)
        new_thresh = self._get_threshold()
        
        crossed = old_thresh != new_thresh
        allocation = self._allocate(amount, new_thresh, source)
        
        return {
            'amount': amount,
            'source': source,
            'old_capital': old_capital,
            'new_capital': self.capital,
            'threshold_crossed': crossed,
            'allocation': allocation,
            'strategies': new_thresh.value[2]
        }
    
    def _get_threshold_from_capital(self, capital: float) -> Threshold:
        for t in Threshold:
            min_c, max_c, _ = t.value
            if min_c <= capital < max_c:
                return t
        return Threshold.WEALTH
    
    def _allocate(self, amount: float, threshold: Threshold, source: str) -> Dict:
        """Smart allocation based on threshold"""
        _, _, strategies = threshold.value
        
        # Source-based adjustments
        if source == 'windfall':
            safe, mod, agg = 0.3, 0.4, 0.3
        elif source == 'micro':
            safe, mod, agg = 0.7, 0.3, 0.0
        else:
            safe, mod, agg = 0.4, 0.4, 0.2
        
        return {
            'safe': self._alloc_safe(amount * safe, strategies),
            'moderate': self._alloc_moderate(amount * mod, strategies),
            'aggressive': self._alloc_agg(amount * agg, strategies) if agg > 0 else []
        }
    
    def _alloc_safe(self, amount: float, strategies: List[str]) -> List[Dict]:
        alloc = []
        if 'savings' in strategies:
            alloc.append({'type': 'savings', 'amount': amount * 0.5, 'apy': 0.046})
        if 'premium_bonds' in strategies and amount >= 12.5:
            alloc.append({'type': 'premium_bonds', 'amount': amount * 0.3, 'return': 0.04})
        if 'bonds' in strategies and amount >= 50:
            alloc.append({'type': 'bonds', 'amount': amount * 0.2, 'yield': 0.035})
        return alloc
    
    def _alloc_moderate(self, amount: float, strategies: List[str]) -> List[Dict]:
        alloc = []
        if 'gold' in strategies or 'gold_micro' in strategies:
            alloc.append({'type': 'gold_etf', 'amount': amount * 0.4, 'ticker': 'SGLN'})
        if 'p2p' in strategies and amount >= 10:
            alloc.append({'type': 'p2p', 'amount': amount * 0.3, 'apy': 0.055})
        if 'index' in strategies and amount >= 25:
            alloc.append({'type': 'index', 'amount': amount * 0.3, 'fund': 'VWRL'})
        return alloc
    
    def _alloc_agg(self, amount: float, strategies: List[str]) -> List[Dict]:
        alloc = []
        if 'crypto_stake' in strategies and amount >= 5:
            alloc.append({'type': 'staking', 'amount': amount * 0.5, 'apy': 0.04})
        if 'grid_bot' in strategies and amount >= 50:
            alloc.append({'type': 'grid', 'amount': amount * 0.3, 'platform': 'pionex'})
        if 'arb' in strategies and amount >= 100:
            alloc.append({'type': 'arbitrage', 'amount': amount * 0.2, 'min_spread': 0.005})
        return alloc
    
    def get_random_contribution_schedule(self, base_amount: float, 
                                         variance: float = 0.3,
                                         frequency: str = 'weekly') -> List[Dict]:
        """Generate random contribution pattern"""
        import random
        from datetime import datetime, timedelta
        
        schedule = []
        current_date = datetime.now()
        
        for i in range(52):  # 1 year
            # Random amount: base ± variance
            random_factor = 1.0 + random.uniform(-variance, variance * 2)
            amount = base_amount * random_factor
            
            # Random timing: ±3 days
            days_offset = random.randint(-3, 3)
            contrib_date = current_date + timedelta(weeks=i, days=days_offset)
            
            schedule.append({
                'date': contrib_date,
                'amount': round(amount, 2),
                'source': 'random_variation'
            })
        
        return schedule

# Example usage
if __name__ == "__main__":
    allocator = AdaptiveAllocator(capital=45)
    
    # Regular contribution
    result = allocator.process_contribution(20, 'regular')
    print(f"Capital: £{result['old_capital']} → £{result['new_capital']}")
    print(f"Threshold crossed: {result['threshold_crossed']}")
    
    # Random schedule
    schedule = allocator.get_random_contribution_schedule(base_amount=15, variance=0.5)
    print(f"\nRandom schedule (first 4 weeks):")
    for week in schedule[:4]:
        print(f"  {week['date'].strftime('%Y-%m-%d')}: £{week['amount']}")
