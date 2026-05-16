"""
Double-Entry Bookkeeping System
Core accounting engine implementing debit/credit mechanics
Inspired by Bigcapital - MIT License
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum
import uuid

from .chart_of_accounts import Account, AccountType, AccountNormalBalance, get_chart_of_accounts

class EntryType(Enum):
    DEBIT = "debit"
    CREDIT = "credit"

@dataclass
class JournalEntryLine:
    """Single line in a journal entry (debit or credit)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    account_code: str = ""
    entry_type: EntryType = EntryType.DEBIT
    amount: float = 0.0
    currency: str = "USD"
    description: str = ""
    reference: str = ""
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount must be positive, use entry_type to indicate direction")

@dataclass
class JournalEntry:
    """Complete journal entry with debits and credits"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date: datetime = field(default_factory=datetime.now)
    reference_number: str = ""
    description: str = ""
    lines: List[JournalEntryLine] = field(default_factory=list)
    is_posted: bool = False
    is_reversing: bool = False
    reversed_entry_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    posted_at: Optional[datetime] = None
    created_by: str = "system"
    metadata: Dict = field(default_factory=dict)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the journal entry balances"""
        errors = []
        
        if not self.lines:
            errors.append("Journal entry must have at least one line")
        
        total_debits = sum(line.amount for line in self.lines if line.entry_type == EntryType.DEBIT)
        total_credits = sum(line.amount for line in self.lines if line.entry_type == EntryType.CREDIT)
        
        if abs(total_debits - total_credits) > 0.001:  # Allow for floating point precision
            errors.append(f"Journal entry is not balanced: Debits ${total_debits:.2f} != Credits ${total_credits:.2f}")
        
        if total_debits == 0:
            errors.append("Journal entry must have at least one debit")
        
        return len(errors) == 0, errors
    
    def get_total_debits(self) -> float:
        return sum(line.amount for line in self.lines if line.entry_type == EntryType.DEBIT)
    
    def get_total_credits(self) -> float:
        return sum(line.amount for line in self.lines if line.entry_type == EntryType.CREDIT)

class DoubleEntrySystem:
    """
    Core double-entry bookkeeping system
    Ensures every transaction affects at least two accounts (debit = credit)
    """
    
    def __init__(self):
        self._entries: Dict[str, JournalEntry] = {}
        self._unposted_entries: List[str] = []
        self._account_balances: Dict[str, float] = {}
        self.chart_of_accounts = get_chart_of_accounts()
    
    def create_journal_entry(self, description: str, reference_number: str = "",
                            date: Optional[datetime] = None, created_by: str = "system") -> JournalEntry:
        """Create a new journal entry"""
        entry = JournalEntry(
            description=description,
            reference_number=reference_number or self._generate_reference(),
            date=date or datetime.now(),
            created_by=created_by
        )
        self._entries[entry.id] = entry
        self._unposted_entries.append(entry.id)
        return entry
    
    def add_line(self, entry_id: str, account_code: str, entry_type: EntryType,
                 amount: float, description: str = "", currency: str = "USD") -> JournalEntryLine:
        """Add a line to a journal entry"""
        entry = self._entries.get(entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")
        
        if entry.is_posted:
            raise ValueError("Cannot modify posted entry")
        
        # Validate account exists
        account = self.chart_of_accounts.get_account(account_code)
        if not account:
            raise ValueError(f"Account {account_code} not found")
        
        line = JournalEntryLine(
            account_code=account_code,
            entry_type=entry_type,
            amount=amount,
            currency=currency,
            description=description
        )
        
        entry.lines.append(line)
        return line
    
    def post_entry(self, entry_id: str) -> JournalEntry:
        """Post a journal entry to the general ledger"""
        entry = self._entries.get(entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")
        
        if entry.is_posted:
            raise ValueError("Entry already posted")
        
        # Validate entry balances
        is_valid, errors = entry.validate()
        if not is_valid:
            raise ValueError(f"Validation failed: {', '.join(errors)}")
        
        # Update account balances
        for line in entry.lines:
            balance_change = self._calculate_balance_change(line)
            self._account_balances[line.account_code] = self._account_balances.get(line.account_code, 0) + balance_change
        
        entry.is_posted = True
        entry.posted_at = datetime.now()
        
        # Remove from unposted list
        if entry_id in self._unposted_entries:
            self._unposted_entries.remove(entry_id)
        
        return entry
    
    def reverse_entry(self, entry_id: str, reversal_date: Optional[datetime] = None) -> JournalEntry:
        """Create a reversing entry"""
        original = self._entries.get(entry_id)
        if not original:
            raise ValueError(f"Entry {entry_id} not found")
        
        if not original.is_posted:
            raise ValueError("Can only reverse posted entries")
        
        # Create reversing entry
        reversal = JournalEntry(
            description=f"Reversal of {original.reference_number}: {original.description}",
            reference_number=self._generate_reference(),
            date=reversal_date or datetime.now(),
            is_reversing=True,
            reversed_entry_id=original.id
        )
        
        # Swap debits and credits
        for line in original.lines:
            reversed_type = EntryType.CREDIT if line.entry_type == EntryType.DEBIT else EntryType.DEBIT
            self.add_line(
                entry_id=reversal.id,
                account_code=line.account_code,
                entry_type=reversed_type,
                amount=line.amount,
                description=f"Reversal: {line.description}",
                currency=line.currency
            )
        
        self._entries[reversal.id] = reversal
        return reversal
    
    def get_account_balance(self, account_code: str) -> float:
        """Get current balance for an account"""
        return self._account_balances.get(account_code, 0.0)
    
    def get_account_balance_with_type(self, account_code: str) -> Tuple[float, str]:
        """Get balance and indicate if it's debit or credit balance"""
        balance = self.get_account_balance(account_code)
        account = self.chart_of_accounts.get_account(account_code)
        
        if not account:
            return balance, "unknown"
        
        # Determine if balance is normal or abnormal
        is_normal = (balance >= 0 and account.normal_balance == AccountNormalBalance.DEBIT) or \
                    (balance <= 0 and account.normal_balance == AccountNormalBalance.CREDIT)
        
        balance_type = account.normal_balance.value if is_normal else (
            "credit" if account.normal_balance == AccountNormalBalance.DEBIT else "debit"
        )
        
        return abs(balance), balance_type
    
    def get_trial_balance(self) -> Dict[str, Dict]:
        """Generate trial balance (all accounts with balances)"""
        trial_balance = {}
        
        for code in self._account_balances:
            account = self.chart_of_accounts.get_account(code)
            if account:
                balance, balance_type = self.get_account_balance_with_type(code)
                trial_balance[code] = {
                    "account": account.to_dict(),
                    "balance": balance,
                    "balance_type": balance_type,
                    "debit": balance if balance_type == "debit" else 0,
                    "credit": balance if balance_type == "credit" else 0
                }
        
        return trial_balance
    
    def validate_trial_balance(self) -> Tuple[bool, float]:
        """Check if trial balance balances (total debits = total credits)"""
        trial_balance = self.get_trial_balance()
        
        total_debits = sum(item["debit"] for item in trial_balance.values())
        total_credits = sum(item["credit"] for item in trial_balance.values())
        
        difference = abs(total_debits - total_credits)
        is_valid = difference < 0.01
        
        return is_valid, difference
    
    def get_entries_by_account(self, account_code: str, posted_only: bool = True) -> List[JournalEntry]:
        """Get all journal entries affecting an account"""
        entries = []
        
        for entry in self._entries.values():
            if posted_only and not entry.is_posted:
                continue
            
            if any(line.account_code == account_code for line in entry.lines):
                entries.append(entry)
        
        return sorted(entries, key=lambda e: e.date)
    
    def get_unposted_entries(self) -> List[JournalEntry]:
        """Get all unposted entries"""
        return [self._entries[eid] for eid in self._unposted_entries]
    
    def delete_unposted_entry(self, entry_id: str):
        """Delete an unposted entry"""
        entry = self._entries.get(entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")
        
        if entry.is_posted:
            raise ValueError("Cannot delete posted entry - use reversal instead")
        
        del self._entries[entry_id]
        if entry_id in self._unposted_entries:
            self._unposted_entries.remove(entry_id)
    
    def _calculate_balance_change(self, line: JournalEntryLine) -> float:
        """Calculate how a line item affects account balance"""
        account = self.chart_of_accounts.get_account(line.account_code)
        if not account:
            raise ValueError(f"Account {line.account_code} not found")
        
        # Determine if this increases or decreases the account
        if account.normal_balance == AccountNormalBalance.DEBIT:
            # Debit accounts: debits increase, credits decrease
            return line.amount if line.entry_type == EntryType.DEBIT else -line.amount
        else:
            # Credit accounts: credits increase, debits decrease
            return line.amount if line.entry_type == EntryType.CREDIT else -line.amount
    
    def _generate_reference(self) -> str:
        """Generate a unique reference number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique = str(uuid.uuid4())[:8]
        return f"JE-{timestamp}-{unique}"
    
    # Convenience methods for common transactions
    def record_sale(self, amount: float, description: str = "") -> JournalEntry:
        """Record a simple sale transaction"""
        entry = self.create_journal_entry(
            description=description or f"Sale - ${amount:.2f}",
            reference_number=self._generate_reference()
        )
        
        # Debit Cash (increase asset)
        self.add_line(entry.id, "1000", EntryType.DEBIT, amount, "Cash received from sale")
        
        # Credit Revenue (increase revenue)
        self.add_line(entry.id, "4000", EntryType.CREDIT, amount, "Revenue from sale")
        
        self.post_entry(entry.id)
        return entry
    
    def record_expense(self, amount: float, expense_account: str = "5100",
                       payment_account: str = "1000", description: str = "") -> JournalEntry:
        """Record an expense payment"""
        entry = self.create_journal_entry(
            description=description or f"Expense - ${amount:.2f}",
            reference_number=self._generate_reference()
        )
        
        # Debit Expense (increase expense)
        self.add_line(entry.id, expense_account, EntryType.DEBIT, amount, description)
        
        # Credit Cash (decrease asset)
        self.add_line(entry.id, payment_account, EntryType.CREDIT, amount, "Payment for expense")
        
        self.post_entry(entry.id)
        return entry
    
    def record_investment(self, symbol: str, shares: float, price: float,
                          account: str = "1700") -> JournalEntry:
        """Record a stock/investment purchase"""
        total = shares * price
        entry = self.create_journal_entry(
            description=f"Purchase {shares} shares of {symbol} @ ${price:.2f}",
            reference_number=self._generate_reference()
        )
        
        # Debit Investment account
        self.add_line(entry.id, account, EntryType.DEBIT, total, f"{symbol} - {shares} shares")
        
        # Credit Cash
        self.add_line(entry.id, "1000", EntryType.CREDIT, total, f"Payment for {symbol}")
        
        self.post_entry(entry.id)
        return entry

# Singleton instance
_double_entry_system: Optional[DoubleEntrySystem] = None

def get_double_entry_system() -> DoubleEntrySystem:
    """Get or create singleton Double Entry System instance"""
    global _double_entry_system
    if _double_entry_system is None:
        _double_entry_system = DoubleEntrySystem()
    return _double_entry_system
