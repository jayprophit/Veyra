"""UK ISA Tracker - Tax-free wrapper support"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

@dataclass
class ISAHolding:
    symbol: str
    name: str
    quantity: Decimal
    avg_price: Decimal
    current_price: Decimal
    value: Decimal
    gain: Decimal

@dataclass
class ISAAccount:
    """UK Individual Savings Account (ISA)"""
    account_id: str
    owner: str
    tax_year: int
    allowance: Decimal = Decimal("20000")
    deposited: Decimal = Decimal("0")
    holdings: Dict[str, ISAHolding] = field(default_factory=dict)
    cash_balance: Decimal = Decimal("0")
    
    def deposit(self, amount: Decimal) -> bool:
        if self.deposited + amount > self.allowance:
            return False
        self.deposited += amount
        self.cash_balance += amount
        return True
    
    def buy(self, symbol: str, name: str, qty: Decimal, price: Decimal):
        cost = qty * price
        if cost > self.cash_balance:
            return False
        
        holding = ISAHolding(
            symbol=symbol,
            name=name,
            quantity=qty,
            avg_price=price,
            current_price=price,
            value=qty * price,
            gain=Decimal("0")
        )
        self.holdings[symbol] = holding
        self.cash_balance -= cost
        return True
    
    def get_summary(self) -> Dict:
        total_value = sum(h.value for h in self.holdings.values()) + self.cash_balance
        total_gain = sum(h.gain for h in self.holdings.values())
        
        return {
            "account_id": self.account_id,
            "tax_year": self.tax_year,
            "allowance": float(self.allowance),
            "deposited": float(self.deposited),
            "remaining_allowance": float(self.allowance - self.deposited),
            "cash": float(self.cash_balance),
            "holdings_value": sum(float(h.value) for h in self.holdings.values()),
            "total_value": float(total_value),
            "total_gain_tax_free": float(total_gain),
            "num_holdings": len(self.holdings)
        }

class ISAManager:
    """Manages multiple ISA accounts across tax years"""
    
    def __init__(self):
        self.accounts: Dict[str, ISAAccount] = {}
        current_year = datetime.now().year
        # Support last 3 tax years
        for year in range(current_year - 2, current_year + 1):
            account_id = f"ISA_{year}_{datetime.now().timestamp()}"
            self.accounts[str(year)] = ISAAccount(
                account_id=account_id,
                owner="user",
                tax_year=year
            )
    
    def get_current_year_account(self) -> ISAAccount:
        current_year = datetime.now().year
        return self.accounts.get(str(current_year))
    
    def get_all_summary(self) -> Dict:
        total_value = sum(
            acc.get_summary()["total_value"] 
            for acc in self.accounts.values()
        )
        return {
            "accounts": [acc.get_summary() for acc in self.accounts.values()],
            "total_isa_value": total_value,
            "num_accounts": len(self.accounts)
        }
