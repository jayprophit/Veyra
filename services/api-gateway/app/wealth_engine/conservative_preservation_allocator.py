"""Conservative Preservation Allocator - Capital protection focus"""
from typing import Dict
from .base_allocator import BaseAllocator, AllocationDecision, AllocationStrategy
from datetime import datetime

class ConservativePreservationAllocator(BaseAllocator):
    """Preserve capital, steady income. Minimal risk. Works with £1+"""
    
    STRATEGIES = [
        ('high_yield_savings', 0.30, 0.046, 0.02),
        ('premium_bonds', 0.25, 0.04, 0.01),
        ('government_bonds', 0.20, 0.035, 0.05),
        ('gold_etf', 0.15, 0.03, 0.15),
        ('dividend_aristocrats', 0.10, 0.045, 0.20)
    ]
    
    def can_allocate(self, amount: float) -> bool:
        return amount >= 1
    
    def get_recommended_capital_range(self) -> tuple:
        return (1, 10000)
    
    def get_name(self) -> str:
        return "Conservative Preservation"
    
    def get_description(self) -> str:
        return "Capital preservation with steady income. Minimal risk. Works from £1."
    
    def allocate(self, amount: float, context: Dict) -> AllocationDecision:
        allocs = []
        
        for name, pct, ret, risk in self.STRATEGIES:
            min_amt = 25 if name == 'premium_bonds' else 10 if name == 'gold_etf' else 1
            if amount * pct >= min_amt:
                allocs.append({
                    'module': name,
                    'amount': amount * pct,
                    'expected_return': ret,
                    'risk_score': risk,
                    'platform': self._platform(name)
                })
        
        return AllocationDecision(
            timestamp=datetime.now(),
            amount=amount,
            source=context.get('source', 'regular'),
            strategy=AllocationStrategy.CONSERVATIVE_PRESERVATION,
            allocations=allocs,
            expected_return_annual=0.04,
            risk_score=0.1,
            liquidity_score=0.9,
            confidence=0.9,
            reasoning="Capital preservation with inflation-beating returns"
        )
    
    def _platform(self, name: str) -> str:
        return {'high_yield_savings': 'chip', 'premium_bonds': 'nsi', 'government_bonds': 'hl',
                'gold_etf': 'trading212', 'dividend_aristocrats': 'vanguard'}.get(name, 'generic')
