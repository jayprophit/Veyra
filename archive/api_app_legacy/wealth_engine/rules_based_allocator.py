"""Rules-Based Allocator - Classic allocation models"""
from typing import Dict, List
from .base_allocator import BaseAllocator, AllocationDecision, AllocationStrategy
from datetime import datetime
from enum import Enum

class AllocationRule(Enum):
    # Simple rules
    TEN_NINETY = "10_90"                    # 10% safe, 90% growth
    NINETY_TEN = "90_10"                    # 90% safe, 10% growth
    
    # Three-way splits
    FIFTY_THIRTY_TWENTY = "50_30_20"        # 50% stocks, 30% bonds, 20% alternatives
    SIXTY_FORTY = "60_40"                   # Classic balanced
    
    # Debt-first rules
    DEBT_FIRST_70_30 = "debt_first_70_30"   # 70% to debt until cleared, then invest
    
    # Income-based
    INCOME_SPLIT_EQUAL = "equal_thirds"     # 33/33/33 across 3 categories
    
    # Aggressive growth
    ALL_IN_GROWTH = "all_growth"            # 100% growth assets
    
    # Conservative
    ALL_IN_SAFE = "all_safe"                # 100% safe assets
    
    # Custom
    CUSTOM = "custom"                       # User-defined percentages

class RulesBasedAllocator(BaseAllocator):
    """
    Classic allocation rules. Simple, proven strategies.
    Best for: Users who want set-it-and-forget-it based on known models.
    """
    
    RULES = {
        AllocationRule.TEN_NINETY: {
            'name': '10/90 Growth',
            'description': '10% safety buffer, 90% aggressive growth. High volatility.',
            'allocation': {
                'safe': 0.10,
                'growth': 0.90,
                'income': 0.00,
                'alternative': 0.00
            },
            'min_capital': 100,
            'risk_level': 'aggressive'
        },
        AllocationRule.NINETY_TEN: {
            'name': '90/10 Conservative',
            'description': '90% safe, 10% growth. Capital preservation with slight upside.',
            'allocation': {
                'safe': 0.90,
                'growth': 0.10,
                'income': 0.00,
                'alternative': 0.00
            },
            'min_capital': 10,
            'risk_level': 'conservative'
        },
        AllocationRule.FIFTY_THIRTY_TWENTY: {
            'name': '50/30/20 Balanced',
            'description': '50% growth stocks, 30% income/bonds, 20% alternatives. Classic balance.',
            'allocation': {
                'safe': 0.00,
                'growth': 0.50,
                'income': 0.30,
                'alternative': 0.20
            },
            'min_capital': 100,
            'risk_level': 'moderate'
        },
        AllocationRule.SIXTY_FORTY: {
            'name': '60/40 Classic',
            'description': '60% stocks, 40% bonds. The pension fund standard.',
            'allocation': {
                'safe': 0.00,
                'growth': 0.60,
                'income': 0.40,
                'alternative': 0.00
            },
            'min_capital': 50,
            'risk_level': 'moderate'
        },
        AllocationRule.DEBT_FIRST_70_30: {
            'name': 'Debt First 70/30',
            'description': '70% to debt payoff until cleared, 30% to emergency/investing.',
            'allocation': {
                'debt_payoff': 0.70,
                'safe': 0.20,
                'growth': 0.10
            },
            'min_capital': 1,
            'risk_level': 'conservative',
            'condition': 'has_high_interest_debt'
        },
        AllocationRule.INCOME_SPLIT_EQUAL: {
            'name': 'Equal Thirds',
            'description': '33% safe, 33% growth, 33% income. Maximum diversification.',
            'allocation': {
                'safe': 0.33,
                'growth': 0.33,
                'income': 0.34,
                'alternative': 0.00
            },
            'min_capital': 30,
            'risk_level': 'moderate'
        },
        AllocationRule.ALL_IN_GROWTH: {
            'name': 'All Growth',
            'description': '100% growth assets. Maximum volatility, maximum long-term return potential.',
            'allocation': {
                'safe': 0.00,
                'growth': 1.00,
                'income': 0.00,
                'alternative': 0.00
            },
            'min_capital': 50,
            'risk_level': 'aggressive'
        },
        AllocationRule.ALL_IN_SAFE: {
            'name': 'All Safe',
            'description': '100% safe assets. No volatility, inflation-beating focus.',
            'allocation': {
                'safe': 1.00,
                'growth': 0.00,
                'income': 0.00,
                'alternative': 0.00
            },
            'min_capital': 1,
            'risk_level': 'conservative'
        }
    }
    
    def __init__(self, profile, rule: AllocationRule = None):
        super().__init__(profile)
        self.selected_rule = rule or self._suggest_rule()
        self.custom_allocation = None
    
    def can_allocate(self, amount: float) -> bool:
        if not self.selected_rule:
            return False
        rule_config = self.RULES.get(self.selected_rule)
        if not rule_config:
            return False
        return amount >= rule_config['min_capital']
    
    def get_recommended_capital_range(self) -> tuple:
        return (1, float('inf'))
    
    def get_name(self) -> str:
        if self.selected_rule:
            return self.RULES[self.selected_rule]['name']
        return "Rules-Based Allocator"
    
    def get_description(self) -> str:
        if self.selected_rule:
            return self.RULES[self.selected_rule]['description']
        return "Classic allocation models: 10/90, 50/30/20, 60/40, and more."
    
    def set_rule(self, rule: AllocationRule):
        """Change allocation rule"""
        self.selected_rule = rule
    
    def set_custom_rule(self, allocation_dict: Dict):
        """Set custom percentages"""
        self.selected_rule = AllocationRule.CUSTOM
        self.custom_allocation = allocation_dict
    
    def allocate(self, amount: float, context: Dict) -> AllocationDecision:
        """Apply selected rule"""
        if not self.selected_rule:
            raise ValueError("No allocation rule selected")
        
        rule_config = self.RULES.get(self.selected_rule)
        if not rule_config and self.selected_rule != AllocationRule.CUSTOM:
            raise ValueError(f"Unknown rule: {self.selected_rule}")
        
        # Get allocation percentages
        if self.selected_rule == AllocationRule.CUSTOM and self.custom_allocation:
            allocation_pcts = self.custom_allocation
        else:
            allocation_pcts = rule_config['allocation']
        
        # Build allocations
        allocations = []
        
        for category, pct in allocation_pcts.items():
            if pct == 0:
                continue
            
            cat_amount = amount * pct
            
            # Map to specific strategies
            if category == 'safe':
                allocations.extend(self._allocate_safe(cat_amount))
            elif category == 'growth':
                allocations.extend(self._allocate_growth(cat_amount))
            elif category == 'income':
                allocations.extend(self._allocate_income(cat_amount))
            elif category == 'alternative':
                allocations.extend(self._allocate_alternative(cat_amount))
            elif category == 'debt_payoff':
                allocations.append({
                    'category': 'debt',
                    'type': 'extra_payment',
                    'amount': cat_amount,
                    'target': 'highest_apr_debt'
                })
        
        # Calculate expected metrics
        total_return = self._estimate_portfolio_return(allocations, amount)
        risk_score = self._estimate_portfolio_risk(rule_config)
        
        return AllocationDecision(
            timestamp=datetime.now(),
            amount=amount,
            source=context.get('source', 'regular'),
            strategy=AllocationStrategy.AI_OPTIMIZED,  # Using AI_OPT for rules
            allocations=allocations,
            expected_return_annual=total_return,
            risk_score=risk_score,
            liquidity_score=0.7,
            confidence=0.85,
            reasoning=f"Applied {self.selected_rule.value} allocation rule"
        )
    
    def _allocate_safe(self, amount: float) -> List[Dict]:
        """Allocate to safe assets"""
        return [
            {'category': 'safe', 'type': 'high_yield_savings', 'amount': amount * 0.5, 'apy': 0.046},
            {'category': 'safe', 'type': 'premium_bonds', 'amount': amount * 0.3, 'return': 0.04},
            {'category': 'safe', 'type': 'government_bonds', 'amount': amount * 0.2, 'yield': 0.035}
        ]
    
    def _allocate_growth(self, amount: float) -> List[Dict]:
        """Allocate to growth assets"""
        return [
            {'category': 'growth', 'type': 'index_funds', 'amount': amount * 0.5, 'expected': 0.08},
            {'category': 'growth', 'type': 'growth_stocks', 'amount': amount * 0.3, 'expected': 0.10},
            {'category': 'growth', 'type': 'crypto', 'amount': amount * 0.2, 'expected': 0.15}
        ]
    
    def _allocate_income(self, amount: float) -> List[Dict]:
        """Allocate to income assets"""
        return [
            {'category': 'income', 'type': 'dividend_stocks', 'amount': amount * 0.4, 'yield': 0.04},
            {'category': 'income', 'type': 'reits', 'amount': amount * 0.3, 'yield': 0.06},
            {'category': 'income', 'type': 'p2p_lending', 'amount': amount * 0.3, 'yield': 0.055}
        ]
    
    def _allocate_alternative(self, amount: float) -> List[Dict]:
        """Allocate to alternatives"""
        return [
            {'category': 'alternative', 'type': 'gold_etf', 'amount': amount * 0.4, 'expected': 0.03},
            {'category': 'alternative', 'type': 'commodities', 'amount': amount * 0.3, 'expected': 0.04},
            {'category': 'alternative', 'type': 'wine', 'amount': amount * 0.3, 'expected': 0.06}
        ]
    
    def _estimate_portfolio_return(self, allocations: List[Dict], total: float) -> float:
        """Weighted average return"""
        if total == 0:
            return 0.0
        
        total_return = 0.0
        for alloc in allocations:
            ret = alloc.get('expected', alloc.get('return', alloc.get('yield', alloc.get('apy', 0.05))))
            weight = alloc['amount'] / total
            total_return += ret * weight
        
        return total_return
    
    def _estimate_portfolio_risk(self, rule_config: Dict) -> float:
        """Map rule risk level to score"""
        risk_map = {
            'conservative': 0.15,
            'moderate': 0.45,
            'aggressive': 0.75
        }
        return risk_map.get(rule_config.get('risk_level', 'moderate'), 0.45)
    
    def _suggest_rule(self) -> AllocationRule:
        """Suggest rule based on profile"""
        # Conservative preference
        if self.profile.risk_tolerance == 'conservative':
            if self._has_high_interest_debt():
                return AllocationRule.DEBT_FIRST_70_30
            return AllocationRule.NINETY_TEN
        
        # Aggressive preference
        if self.profile.risk_tolerance == 'aggressive':
            return AllocationRule.TEN_NINETY
        
        # Moderate default
        return AllocationRule.FIFTY_THIRTY_TWENTY
    
    def _has_high_interest_debt(self) -> bool:
        """Check if user has high-interest debt"""
        debts = self.profile.preferences.get('debts', [])
        return any(d.get('apr', 0) > 10 for d in debts)
    
    def get_all_rules(self) -> Dict:
        """Get all available rules with descriptions"""
        return {
            rule.value: {
                'name': config['name'],
                'description': config['description'],
                'allocation': config['allocation'],
                'min_capital': config['min_capital'],
                'risk_level': config['risk_level']
            }
            for rule, config in self.RULES.items()
        }

# Example usage
if __name__ == "__main__":
    from .base_allocator import UserProfile
    
    profile = UserProfile(
        user_id='test',
        employment_type='stable',
        monthly_income_avg=2000,
        monthly_income_min=1800,
        monthly_income_max=2200,
        risk_tolerance='moderate',
        time_horizon_years=10,
        current_capital=500,
        target_capital=50000,
        preferences={},
        constraints={}
    )
    
    # Use 50/30/20 rule
    allocator = RulesBasedAllocator(profile, AllocationRule.FIFTY_THIRTY_TWENTY)
    decision = allocator.allocate(100, {})
    
    print(f"Rule: {allocator.get_name()}")
    print(f"Expected return: {decision.expected_return_annual:.1%}")
    print(f"Risk: {decision.risk_score:.2f}")
    print(f"Allocations: {len(decision.allocations)}")
