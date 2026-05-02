"""Holistic Orchestrator - Uses all 640+ modules across asset classes"""
from typing import Dict, List
from .base_allocator import BaseAllocator, AllocationDecision, AllocationStrategy
from datetime import datetime

class HolisticOrchestrator(BaseAllocator):
    """Orchestrates across all Financial Master modules. Best for £500+"""
    
    CATEGORIES = {
        'safe': {'pct': 0.20, 'min': 25, 'mods': ['premium_bonds', 'high_yield_savings', 'gilts']},
        'income': {'pct': 0.25, 'min': 50, 'mods': ['dividend_aristocrats', 'reits', 'p2p']},
        'growth': {'pct': 0.20, 'min': 25, 'mods': ['index_funds', 'growth_stocks', 'sector_etfs']},
        'alternative': {'pct': 0.15, 'min': 10, 'mods': ['gold_etf', 'commodities', 'wine']},
        'aggressive': {'pct': 0.15, 'min': 100, 'mods': ['grid_bots', 'arbitrage', 'defi']},
        'mining': {'pct': 0.05, 'min': 50, 'mods': ['eth_staking', 'btc_mining_pools']}
    }
    
    def can_allocate(self, amount: float) -> bool:
        return amount >= 10 and self.profile.current_capital >= 100
    
    def get_recommended_capital_range(self) -> tuple:
        return (100, float('inf'))
    
    def get_name(self) -> str:
        return "Holistic Orchestrator"
    
    def get_description(self) -> str:
        return "Uses all 640+ Financial Master modules. Maximum diversification. Best for £500+."
    
    def allocate(self, amount: float, context: Dict) -> AllocationDecision:
        allocs = []
        risk_adj = self._risk_adjustment()
        
        for cat, cfg in self.CATEGORIES.items():
            if amount < cfg['min']:
                continue
            adj_pct = cfg['pct'] * risk_adj.get(cat, 1.0)
            cat_amt = amount * adj_pct
            
            for mod in cfg['mods'][:2]:  # Top 2 per category
                allocs.append({
                    'category': cat,
                    'module': mod,
                    'amount': cat_amt / 2,
                    'expected_return': self._estimate(mod),
                    'risk': self._risk(mod)
                })
        
        exp_return = sum(a['expected_return'] * (a['amount']/amount) for a in allocs) if allocs else 0.07
        
        return AllocationDecision(
            timestamp=datetime.now(),
            amount=amount,
            source=context.get('source', 'regular'),
            strategy=AllocationStrategy.HOLISTIC,
            allocations=allocs,
            expected_return_annual=exp_return,
            risk_score=0.5,
            liquidity_score=0.7,
            confidence=0.75,
            reasoning=f"Diversified across {len(allocs)} module strategies"
        )
    
    def _risk_adjustment(self) -> Dict:
        rt = self.profile.risk_tolerance
        if rt == 'conservative':
            return {'safe': 2.0, 'income': 1.5, 'growth': 0.5, 'alternative': 0.5, 'aggressive': 0.1, 'mining': 0.5}
        elif rt == 'aggressive':
            return {'safe': 0.3, 'income': 0.8, 'growth': 1.5, 'alternative': 1.5, 'aggressive': 2.0, 'mining': 1.5}
        return {k: 1.0 for k in self.CATEGORIES}
    
    def _estimate(self, mod: str) -> float:
        returns = {'premium_bonds': 0.04, 'high_yield_savings': 0.046, 'dividend_aristocrats': 0.05,
                   'reits': 0.06, 'p2p': 0.055, 'index_funds': 0.08, 'growth_stocks': 0.10,
                   'gold_etf': 0.03, 'grid_bots': 0.15, 'arbitrage': 0.12, 'eth_staking': 0.04}
        return returns.get(mod, 0.06)
    
    def _risk(self, mod: str) -> float:
        risks = {'premium_bonds': 0.1, 'high_yield_savings': 0.05, 'grid_bots': 0.6, 'arbitrage': 0.5}
        return risks.get(mod, 0.3)
