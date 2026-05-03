"""
Bank Reconciliation System
Matches bank transactions with journal entries
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class MatchStatus(Enum):
    MATCHED = "matched"
    UNMATCHED = "unmatched"
    PARTIAL = "partial"
    DISCREPANCY = "discrepancy"

@dataclass
class BankTransaction:
    id: str
    date: date
    description: str
    amount: float
    reference: str
    is_debit: bool
    
@dataclass
class ReconciliationMatch:
    bank_txn: BankTransaction
    journal_entry_id: Optional[str]
    status: MatchStatus
    confidence: float
    match_reason: str

class BankReconciliation:
    """Reconciles bank statements with accounting records"""
    
    def __init__(self):
        self._bank_transactions: List[BankTransaction] = []
        self._matches: List[ReconciliationMatch] = []
    
    def import_bank_transactions(self, transactions: List[Dict]) -> List[BankTransaction]:
        """Import transactions from bank feed"""
        bank_txns = []
        for txn in transactions:
            bt = BankTransaction(
                id=txn.get('id', f"bt_{datetime.now().timestamp()}"),
                date=datetime.strptime(txn['date'], '%Y-%m-%d').date(),
                description=txn['description'],
                amount=abs(float(txn['amount'])),
                reference=txn.get('reference', ''),
                is_debit=float(txn['amount']) < 0
            )
            bank_txns.append(bt)
        
        self._bank_transactions = bank_txns
        return bank_txns
    
    def find_matches(
        self,
        journal_entries: List[Dict],
        amount_tolerance: float = 0.01,
        date_tolerance_days: int = 2
    ) -> List[ReconciliationMatch]:
        """Find matches between bank transactions and journal entries"""
        
        matches = []
        
        for bank_txn in self._bank_transactions:
            best_match = None
            best_confidence = 0.0
            
            for entry in journal_entries:
                confidence = self._calculate_match_confidence(
                    bank_txn, entry, amount_tolerance, date_tolerance_days
                )
                
                if confidence > best_confidence and confidence > 0.5:
                    best_confidence = confidence
                    best_match = entry
            
            if best_match and best_confidence >= 0.8:
                status = MatchStatus.MATCHED
            elif best_match:
                status = MatchStatus.PARTIAL
            else:
                status = MatchStatus.UNMATCHED
            
            matches.append(ReconciliationMatch(
                bank_txn=bank_txn,
                journal_entry_id=best_match.get('id') if best_match else None,
                status=status,
                confidence=best_confidence,
                match_reason=self._get_match_reason(best_confidence)
            ))
        
        self._matches = matches
        return matches
    
    def _calculate_match_confidence(
        self,
        bank_txn: BankTransaction,
        journal_entry: Dict,
        amount_tolerance: float,
        date_tolerance_days: int
    ) -> float:
        """Calculate confidence score for a potential match"""
        
        scores = []
        
        # Amount match (weight: 0.4)
        entry_amount = abs(journal_entry.get('amount', 0))
        amount_diff = abs(bank_txn.amount - entry_amount)
        if amount_diff <= amount_tolerance:
            scores.append(0.4)
        elif amount_diff <= amount_tolerance * 2:
            scores.append(0.2)
        else:
            scores.append(0)
        
        # Date match (weight: 0.3)
        entry_date = journal_entry.get('date')
        if entry_date:
            if isinstance(entry_date, str):
                entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            date_diff = abs((bank_txn.date - entry_date).days)
            if date_diff == 0:
                scores.append(0.3)
            elif date_diff <= date_tolerance_days:
                scores.append(0.15)
            else:
                scores.append(0)
        
        # Description similarity (weight: 0.2)
        entry_desc = journal_entry.get('description', '').lower()
        bank_desc = bank_txn.description.lower()
        if entry_desc and bank_desc:
            # Simple word overlap
            entry_words = set(entry_desc.split())
            bank_words = set(bank_desc.split())
            overlap = len(entry_words & bank_words) / max(len(entry_words), len(bank_words))
            scores.append(overlap * 0.2)
        
        # Reference match (weight: 0.1)
        if bank_txn.reference and bank_txn.reference in str(journal_entry.get('reference', '')):
            scores.append(0.1)
        
        return sum(scores)
    
    def _get_match_reason(self, confidence: float) -> str:
        """Get reason for match status"""
        if confidence >= 0.9:
            return "Exact match on amount and date"
        elif confidence >= 0.8:
            return "Strong match on amount and date"
        elif confidence >= 0.5:
            return "Partial match, review recommended"
        else:
            return "No matching entry found"
    
    def get_reconciliation_summary(self) -> Dict:
        """Get summary of reconciliation status"""
        
        if not self._matches:
            return {"status": "no_data"}
        
        total = len(self._matches)
        matched = sum(1 for m in self._matches if m.status == MatchStatus.MATCHED)
        partial = sum(1 for m in self._matches if m.status == MatchStatus.PARTIAL)
        unmatched = sum(1 for m in self._matches if m.status == MatchStatus.UNMATCHED)
        
        total_amount = sum(m.bank_txn.amount for m in self._matches)
        matched_amount = sum(m.bank_txn.amount for m in self._matches if m.status == MatchStatus.MATCHED)
        
        return {
            "total_transactions": total,
            "matched": matched,
            "partial": partial,
            "unmatched": unmatched,
            "match_rate": round((matched / total * 100), 1) if total > 0 else 0,
            "total_amount": round(total_amount, 2),
            "matched_amount": round(matched_amount, 2),
            "unmatched_amount": round(total_amount - matched_amount, 2),
            "status": "complete" if unmatched == 0 else "pending"
        }
    
    def get_unmatched_transactions(self) -> List[BankTransaction]:
        """Get unmatched bank transactions"""
        return [
            m.bank_txn for m in self._matches
            if m.status == MatchStatus.UNMATCHED
        ]
    
    def create_journal_entry_for_unmatched(
        self,
        bank_txn: BankTransaction,
        account_code: str
    ) -> Dict:
        """Create journal entry for an unmatched transaction"""
        
        from .double_entry import EntryType
        
        return {
            "description": f"Bank transaction: {bank_txn.description}",
            "date": bank_txn.date.isoformat(),
            "reference": bank_txn.reference,
            "lines": [
                {
                    "account_code": "1000",  # Cash/Bank
                    "entry_type": EntryType.DEBIT.value if bank_txn.is_debit else EntryType.CREDIT.value,
                    "amount": bank_txn.amount,
                    "description": bank_txn.description
                },
                {
                    "account_code": account_code,
                    "entry_type": EntryType.CREDIT.value if bank_txn.is_debit else EntryType.DEBIT.value,
                    "amount": bank_txn.amount,
                    "description": f"Reconciliation for {bank_txn.id}"
                }
            ]
        }
    
    def reconcile_period(self, start_date: date, end_date: date) -> Dict:
        """Full reconciliation for a period"""
        
        # Filter transactions by date
        period_txns = [
            bt for bt in self._bank_transactions
            if start_date <= bt.date <= end_date
        ]
        
        # Calculate totals
        total_debits = sum(bt.amount for bt in period_txns if bt.is_debit)
        total_credits = sum(bt.amount for bt in period_txns if not bt.is_debit)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "transaction_count": len(period_txns),
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "net_change": round(total_credits - total_debits, 2)
        }
