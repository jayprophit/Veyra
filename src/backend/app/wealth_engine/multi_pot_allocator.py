"""Multi-Pot Allocator - Cross-platform wealth coordination"""
from typing import Dict, List
from .base_allocator import BaseAllocator, AllocationDecision, AllocationStrategy
from datetime import datetime

class MultiPotAllocator(BaseAllocator):
    """Coordinates multiple wallets/exchanges/pots. Best for £500+"""
    
    POTS = {
        'coinbase': {'type': 'crypto_base', 'pct': 0.25, 'strategies': ['staking', 'dca']},
        'binance': {'type': 'trading', 'pct': 0.20, 'strategies': ['grid', 'arbitrage']},
        'trading212': {'type': 'equity', 'pct': 0.25, 'strategies': ['gold_etf', 'index']},
        'p2p': {'type': 'fixed_income', 'pct': 0.15, 'strategies': ['auto_lend']},
        'savings': {'type': 'cash', 'pct': 0.15, 'strategies': ['high_yield']}
    }
    
    def can_allocate(self, amount: float) -> bool:
        return amount >= 50 and self.profile.current_capital >= 500
    
    def get_recommended_capital_range(self) -> tuple:
        return (500, float('inf'))
    
    def get_name(self) -> str:
        return "Multi-Pot Coordinator"
    
    def get_description(self) -> str:
        return "Cross-platform coordination. Auto-rebalances between Coinbase, Binance, T212, P2P. Best for £500+."
    
    def allocate(self, amount: float, context: Dict) -> AllocationDecision:
        allocs = []
        
        for pot, cfg in self.POTS.items():
            allocs.append({
                'pot': pot,
                'type': cfg['type'],
                'amount': amount * cfg['pct'],
                'strategies': cfg['strategies'],
                'platform': pot,
                'auto_rebalance': True
            })
        
        return AllocationDecision(
            timestamp=datetime.now(),
            amount=amount,
            source=context.get('source', 'regular'),
            strategy=AllocationStrategy.MULTI_POT,
            allocations=allocs,
            expected_return_annual=0.08,
            risk_score=0.45,
            liquidity_score=0.75,
            confidence=0.7,
            reasoning="Multi-platform diversification with auto-rebalancing"
        )
    
    def get_transfer_plan(self, from_pot: str, to_pot: str, amount: float) -> Dict:
        """Plan cross-platform transfer"""
        return {
            'from': from_pot,
            'to': to_pot,
            'amount': amount,
            'steps': [
                {'action': 'withdraw', 'platform': from_pot, 'estimated_time': '1-24h'},
                {'action': 'wait_confirmation'},
                {'action': 'deposit', 'platform': to_pot, 'estimated_time': 'instant'}
            ]
        }
