"""Aggressive Growth Allocator - High risk, high return focus"""
from typing import Dict
from .base_allocator import BaseAllocator, AllocationDecision, AllocationStrategy
from datetime import datetime

class AggressiveGrowthAllocator(BaseAllocator):
    """Maximize growth. High volatility tolerance required. Best for £200+"""
    
    STRATEGIES = [
        ('crypto_trading', 0.25, 0.20, 0.8),
        ('grid_bots', 0.20, 0.15, 0.7),
        ('arbitrage', 0.15, 0.12, 0.6),
        ('growth_stocks', 0.15, 0.12, 0.6),
        ('defi_yield', 0.15, 0.15, 0.8),
        ('options_leaps', 0.10, 0.18, 0.9)
    ]
    
    def can_allocate(self, amount: float) -> bool:
        return amount >= 50 and self.profile.current_capital >= 200
    
    def get_recommended_capital_range(self) -> tuple:
        return (200, float('inf'))
    
    def get_name(self) -> str:
        return "Aggressive Growth"
    
    def get_description(self) -> str:
        return "High risk, high return. Crypto, trading, leverage. Best for £200+ with high risk tolerance."
    
    def allocate(self, amount: float, context: Dict) -> AllocationDecision:
        allocs = []
        
        for name, pct, ret, risk in self.STRATEGIES:
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
            strategy=AllocationStrategy.AGGRESSIVE_GROWTH,
            allocations=allocs,
            expected_return_annual=0.15,
            risk_score=0.75,
            liquidity_score=0.6,
            confidence=0.65,
            reasoning="Aggressive growth focus - high volatility expected"
        )
    
    def _platform(self, name: str) -> str:
        return {'crypto_trading': 'binance', 'grid_bots': 'pionex', 'arbitrage': 'multi_exchange',
                'growth_stocks': 'trading212', 'defi_yield': 'metamask', 'options_leaps': 'ibkr'}.get(name, 'generic')
