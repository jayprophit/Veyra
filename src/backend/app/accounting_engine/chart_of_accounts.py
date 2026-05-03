"""
Chart of Accounts Management System
Inspired by Bigcapital - MIT License

Standard Accounting Structure:
1 - Assets (1000-1999)
2 - Liabilities (2000-2999)
3 - Equity (3000-3999)
4 - Revenue (4000-4999)
5 - Expenses (5000-5999)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json
from datetime import datetime

class AccountType(Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

class AccountNormalBalance(Enum):
    DEBIT = "debit"
    CREDIT = "credit"

@dataclass
class Account:
    code: str
    name: str
    type: AccountType
    normal_balance: AccountNormalBalance
    parent_code: Optional[str] = None
    description: str = ""
    is_active: bool = True
    is_bank_account: bool = False
    currency: str = "USD"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "type": self.type.value,
            "normal_balance": self.normal_balance.value,
            "parent_code": self.parent_code,
            "description": self.description,
            "is_active": self.is_active,
            "is_bank_account": self.is_bank_account,
            "currency": self.currency,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class ChartOfAccounts:
    """
    Manages the Chart of Accounts for double-entry bookkeeping.
    Supports multi-currency, hierarchical accounts, and AI categorization.
    """
    
    # Standard account ranges
    ACCOUNT_RANGES = {
        AccountType.ASSET: (1000, 1999),
        AccountType.LIABILITY: (2000, 2999),
        AccountType.EQUITY: (3000, 3999),
        AccountType.REVENUE: (4000, 4999),
        AccountType.EXPENSE: (5000, 5999),
    }
    
    # Default accounts for new companies
    DEFAULT_ACCOUNTS = [
        # Assets (1000-1999)
        Account("1000", "Cash", AccountType.ASSET, AccountNormalBalance.DEBIT, is_bank_account=True),
        Account("1010", "Checking Account", AccountType.ASSET, AccountNormalBalance.DEBIT, is_bank_account=True),
        Account("1020", "Savings Account", AccountType.ASSET, AccountNormalBalance.DEBIT, is_bank_account=True),
        Account("1100", "Accounts Receivable", AccountType.ASSET, AccountNormalBalance.DEBIT),
        Account("1200", "Inventory", AccountType.ASSET, AccountNormalBalance.DEBIT),
        Account("1500", "Equipment", AccountType.ASSET, AccountNormalBalance.DEBIT),
        Account("1600", "Accumulated Depreciation", AccountType.ASSET, AccountNormalBalance.CREDIT, parent_code="1500"),
        Account("1700", "Investments", AccountType.ASSET, AccountNormalBalance.DEBIT),
        Account("1800", "Cryptocurrency", AccountType.ASSET, AccountNormalBalance.DEBIT),
        
        # Liabilities (2000-2999)
        Account("2000", "Accounts Payable", AccountType.LIABILITY, AccountNormalBalance.CREDIT),
        Account("2100", "Credit Cards", AccountType.LIABILITY, AccountNormalBalance.CREDIT),
        Account("2200", "Loans Payable", AccountType.LIABILITY, AccountNormalBalance.CREDIT),
        Account("2300", "Taxes Payable", AccountType.LIABILITY, AccountNormalBalance.CREDIT),
        Account("2400", "Payroll Liabilities", AccountType.LIABILITY, AccountNormalBalance.CREDIT),
        
        # Equity (3000-3999)
        Account("3000", "Owner's Equity", AccountType.EQUITY, AccountNormalBalance.CREDIT),
        Account("3100", "Retained Earnings", AccountType.EQUITY, AccountNormalBalance.CREDIT),
        Account("3200", "Common Stock", AccountType.EQUITY, AccountNormalBalance.CREDIT),
        Account("3900", "Dividends", AccountType.EQUITY, AccountNormalBalance.DEBIT),
        
        # Revenue (4000-4999)
        Account("4000", "Sales Revenue", AccountType.REVENUE, AccountNormalBalance.CREDIT),
        Account("4100", "Service Revenue", AccountType.REVENUE, AccountNormalBalance.CREDIT),
        Account("4200", "Investment Income", AccountType.REVENUE, AccountNormalBalance.CREDIT),
        Account("4300", "Trading Gains", AccountType.REVENUE, AccountNormalBalance.CREDIT),
        Account("4400", "Dividend Income", AccountType.REVENUE, AccountNormalBalance.CREDIT),
        Account("4500", "Interest Income", AccountType.REVENUE, AccountNormalBalance.CREDIT),
        
        # Expenses (5000-5999)
        Account("5000", "Cost of Goods Sold", AccountType.EXPENSE, AccountNormalBalance.DEBIT),
        Account("5100", "Rent Expense", AccountType.EXPENSE, AccountNormalBalance.DEBIT),
        Account("5200", "Salaries & Wages", AccountType.EXPENSE, AccountNormalBalance.DEBIT),
        Account("5300", "Utilities", AccountType.EXPENSE, AccountNormalBalance.DEBIT),
        Account("5400", "Office Supplies", AccountType.EXPENSE, AccountNormalBalance.DEBIT),
        Account("5500", "Marketing", AccountType.EXPENSE, AccountNormalBalance.DEBIT),
        Account("5600", "Professional Fees", AccountType.EXPENSE, AccountNormalBalance.DEBIT),
        Account("5700", "Software & Subscriptions", AccountType.EXPENSE, AccountNormalBalance.DEBIT),
        Account("5800", "Trading Fees", AccountType.EXPENSE, AccountNormalBalance.DEBIT),
        Account("5900", "Investment Expenses", AccountType.EXPENSE, AccountNormalBalance.DEBIT),
    ]
    
    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._type_index: Dict[AccountType, List[str]] = {
            t: [] for t in AccountType
        }
        self._initialize_default_accounts()
    
    def _initialize_default_accounts(self):
        """Initialize with default accounts"""
        for account in self.DEFAULT_ACCOUNTS:
            self._accounts[account.code] = account
            self._type_index[account.type].append(account.code)
    
    def create_account(self, code: str, name: str, account_type: AccountType,
                       description: str = "", parent_code: Optional[str] = None,
                       is_bank_account: bool = False, currency: str = "USD") -> Account:
        """Create a new account"""
        if code in self._accounts:
            raise ValueError(f"Account code {code} already exists")
        
        # Validate code range
        code_int = int(code)
        min_code, max_code = self.ACCOUNT_RANGES[account_type]
        if not (min_code <= code_int <= max_code):
            raise ValueError(f"Account code {code} not in valid range for {account_type.value}")
        
        normal_balance = AccountNormalBalance.DEBIT if account_type in [
            AccountType.ASSET, AccountType.EXPENSE
        ] else AccountNormalBalance.CREDIT
        
        account = Account(
            code=code,
            name=name,
            type=account_type,
            normal_balance=normal_balance,
            parent_code=parent_code,
            description=description,
            is_bank_account=is_bank_account,
            currency=currency
        )
        
        self._accounts[code] = account
        self._type_index[account_type].append(code)
        
        return account
    
    def get_account(self, code: str) -> Optional[Account]:
        """Get account by code"""
        return self._accounts.get(code)
    
    def get_accounts_by_type(self, account_type: AccountType) -> List[Account]:
        """Get all accounts of a specific type"""
        return [self._accounts[code] for code in self._type_index[account_type]]
    
    def update_account(self, code: str, **kwargs) -> Account:
        """Update account properties"""
        account = self._accounts.get(code)
        if not account:
            raise ValueError(f"Account {code} not found")
        
        for key, value in kwargs.items():
            if hasattr(account, key):
                setattr(account, key, value)
        
        account.updated_at = datetime.now()
        return account
    
    def deactivate_account(self, code: str) -> Account:
        """Deactivate an account (soft delete)"""
        return self.update_account(code, is_active=False)
    
    def get_all_accounts(self, active_only: bool = True) -> List[Account]:
        """Get all accounts"""
        accounts = list(self._accounts.values())
        if active_only:
            accounts = [a for a in accounts if a.is_active]
        return sorted(accounts, key=lambda a: a.code)
    
    def get_bank_accounts(self) -> List[Account]:
        """Get all bank accounts"""
        return [a for a in self._accounts.values() if a.is_bank_account and a.is_active]
    
    def get_account_tree(self) -> Dict[str, Any]:
        """Get hierarchical account structure"""
        tree = {t.value: [] for t in AccountType}
        
        for account in self.get_all_accounts():
            account_dict = account.to_dict()
            if account.parent_code:
                account_dict["parent"] = self._accounts.get(account.parent_code, {}).to_dict() if account.parent_code in self._accounts else None
            tree[account.type.value].append(account_dict)
        
        return tree
    
    def export_to_json(self) -> str:
        """Export chart of accounts to JSON"""
        accounts = [a.to_dict() for a in self.get_all_accounts()]
        return json.dumps(accounts, indent=2)
    
    def import_from_json(self, json_data: str):
        """Import chart of accounts from JSON"""
        accounts_data = json.loads(json_data)
        for data in accounts_data:
            account_type = AccountType(data["type"])
            normal_balance = AccountNormalBalance(data["normal_balance"])
            
            account = Account(
                code=data["code"],
                name=data["name"],
                type=account_type,
                normal_balance=normal_balance,
                parent_code=data.get("parent_code"),
                description=data.get("description", ""),
                is_active=data.get("is_active", True),
                is_bank_account=data.get("is_bank_account", False),
                currency=data.get("currency", "USD"),
                metadata=data.get("metadata", {})
            )
            
            self._accounts[account.code] = account
            self._type_index[account.type].append(account.code)
    
    def get_next_available_code(self, account_type: AccountType) -> str:
        """Get next available account code for a type"""
        min_code, max_code = self.ACCOUNT_RANGES[account_type]
        existing_codes = [int(c) for c in self._type_index[account_type]]
        
        for code in range(min_code, max_code + 1):
            if code not in existing_codes:
                return str(code)
        
        raise ValueError(f"No available codes for {account_type.value}")

# Singleton instance
_chart_of_accounts: Optional[ChartOfAccounts] = None

def get_chart_of_accounts() -> ChartOfAccounts:
    """Get or create singleton Chart of Accounts instance"""
    global _chart_of_accounts
    if _chart_of_accounts is None:
        _chart_of_accounts = ChartOfAccounts()
    return _chart_of_accounts
