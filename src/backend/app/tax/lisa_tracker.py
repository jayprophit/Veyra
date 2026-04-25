"""Lifetime ISA (LISA) Tracker"""
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal

@dataclass
class LISAAccount:
    """UK Lifetime ISA - £4,000/year allowance, 25% gov bonus"""
    account_id: str
    owner: str
    provider: str  # Moneybox, Nutmeg, etc.
    
    # Limits
    ANNUAL_ALLOWANCE = Decimal("4000")
    GOV_BONUS_RATE = Decimal("0.25")  # 25%
    
    # Tracking
    deposited_this_year: Decimal = Decimal("0")
    gov_bonus_earned: Decimal = Decimal("0")
    total_value: Decimal = Decimal("0")
    investments: Dict[str, Decimal] = field(default_factory=dict)
    
    def deposit(self, amount: Decimal) -> bool:
        """Deposit into LISA"""
        if self.deposited_this_year + amount > self.ANNUAL_ALLOWANCE:
            return False
        
        bonus = amount * self.GOV_BONUS_RATE
        self.deposited_this_year += amount
        self.gov_bonus_earned += bonus
        self.total_value += amount + bonus
        
        return True
    
    def buy_first_home(self, property_price: Decimal) -> Dict:
        """Calculate first home purchase from LISA"""
        max_price = Decimal("450000")  # LISA limit
        
        can_use = property_price <= max_price and self.total_value > 0
        penalty = Decimal("0")
        
        if not can_use and self.total_value > 0:
            # 25% penalty for non-qualifying withdrawal
            penalty = self.total_value * Decimal("0.25")
        
        return {
            "available": self.total_value,
            "property_limit": max_price,
            "can_use_lisa": can_use,
            "penalty_if_not": penalty,
            "effective_for_purchase": self.total_value if can_use else self.total_value - penalty
        }
    
    def retirement_withdrawal(self, age: int) -> Dict:
        """Calculate retirement withdrawal (age 60+)"""
        can_access = age >= 60
        penalty = Decimal("0") if can_access else self.total_value * Decimal("0.25")
        
        return {
            "age": age,
            "can_access": can_access,
            "available": self.total_value if can_access else self.total_value - penalty,
            "penalty": penalty if not can_access else 0
        }
    
    def get_summary(self) -> Dict:
        """Get account summary"""
        remaining = self.ANNUAL_ALLOWANCE - self.deposited_this_year
        
        return {
            "account_id": self.account_id,
            "provider": self.provider,
            "annual_allowance": float(self.ANNUAL_ALLOWANCE),
            "deposited_this_year": float(self.deposited_this_year),
            "remaining_allowance": float(remaining),
            "gov_bonus_earned": float(self.gov_bonus_earned),
            "total_value": float(self.total_value),
            "bonus_rate": "25%"
        }

class LISAManager:
    """Manage multiple LISA accounts"""
    
    def __init__(self):
        self.accounts: Dict[str, LISAAccount] = {}
    
    def create_lisa(self, owner: str, provider: str) -> LISAAccount:
        """Create new LISA"""
        account_id = f"LISA_{owner}_{datetime.now().year}"
        lisa = LISAAccount(
            account_id=account_id,
            owner=owner,
            provider=provider
        )
        self.accounts[account_id] = lisa
        return lisa
    
    def get_total_bonus_earned(self) -> float:
        """Total government bonus across all accounts"""
        return sum(float(acc.gov_bonus_earned) for acc in self.accounts.values())
