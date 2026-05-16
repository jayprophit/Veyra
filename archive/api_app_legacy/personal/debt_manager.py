"""
Debt Management Module
Tracks debts, calculates payoff strategies, monitors progress
Supports Snowball and Avalanche methods
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime, date
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class DebtType(Enum):
    CREDIT_CARD = "credit_card"
    PERSONAL_LOAN = "personal_loan"
    STUDENT_LOAN = "student_loan"
    CAR_LOAN = "car_loan"
    MORTGAGE = "mortgage"
    OVERDRAFT = "overdraft"
    BUY_NOW_PAY_LATER = "buy_now_pay_later"
    OTHER = "other"


class PayoffStrategy(Enum):
    SNOWBALL = "snowball"  # Lowest balance first
    AVALANCHE = "avalanche"  # Highest interest first
    HYBRID = "hybrid"  # Balanced approach
    CUSTOM = "custom"  # User-defined priority


@dataclass
class Debt:
    id: str
    name: str
    creditor: str
    debt_type: DebtType
    original_balance: Decimal
    current_balance: Decimal
    interest_rate_annual: Decimal
    min_monthly_payment: Decimal
    custom_monthly_payment: Optional[Decimal] = None
    priority: int = 0
    date_added: datetime = field(default_factory=datetime.now)
    target_payoff_date: Optional[date] = None
    notes: str = ""
    is_cleared: bool = False
    cleared_date: Optional[datetime] = None
    
    @property
    def monthly_payment(self) -> Decimal:
        return self.custom_monthly_payment or self.min_monthly_payment
    
    @property
    def interest_per_month(self) -> Decimal:
        return self.current_balance * (self.interest_rate_annual / 12 / 100)
    
    @property
    def principal_per_month(self) -> Decimal:
        return self.monthly_payment - self.interest_per_month


@dataclass
class PayoffPlan:
    strategy: PayoffStrategy
    debts_order: List[str]  # Debt IDs in payoff order
    total_monthly_payment: Decimal
    months_to_debt_free: int
    total_interest_paid: Decimal
    payoff_schedule: Dict[str, List[Dict[str, Any]]]  # Monthly breakdown per debt
    completion_date: date


@dataclass
class DebtPayment:
    debt_id: str
    amount: Decimal
    principal_paid: Decimal
    interest_paid: Decimal
    payment_date: datetime
    new_balance: Decimal
    notes: str = ""


class DebtManager:
    """Personal debt management and payoff planning"""
    
    def __init__(self):
        self.debts: Dict[str, Debt] = {}
        self.payment_history: List[DebtPayment] = []
        self.payoff_plan: Optional[PayoffPlan] = None
        self.monthly_budget: Decimal = Decimal("0")
        self.extra_payment_amount: Decimal = Decimal("0")
        
    def add_debt(
        self,
        name: str,
        creditor: str,
        debt_type: DebtType,
        original_balance: Decimal,
        current_balance: Decimal,
        interest_rate_annual: Decimal,
        min_monthly_payment: Decimal,
        custom_payment: Optional[Decimal] = None,
        priority: int = 0
    ) -> Debt:
        """Add a new debt to track"""
        debt_id = f"debt_{len(self.debts) + 1}_{datetime.now().timestamp()}"
        
        debt = Debt(
            id=debt_id,
            name=name,
            creditor=creditor,
            debt_type=debt_type,
            original_balance=original_balance,
            current_balance=current_balance,
            interest_rate_annual=interest_rate_annual,
            min_monthly_payment=min_monthly_payment,
            custom_monthly_payment=custom_payment,
            priority=priority
        )
        
        self.debts[debt_id] = debt
        logger.info(f"Added debt: {name} ({creditor}) - £{current_balance} at {interest_rate_annual}%")
        return debt
    
    def update_debt_balance(self, debt_id: str, new_balance: Decimal) -> bool:
        """Update current balance of a debt"""
        if debt_id not in self.debts:
            return False
        
        debt = self.debts[debt_id]
        debt.current_balance = new_balance
        
        if new_balance <= 0 and not debt.is_cleared:
            debt.is_cleared = True
            debt.cleared_date = datetime.now()
            logger.info(f"Debt cleared: {debt.name}")
        
        return True
    
    def record_payment(
        self,
        debt_id: str,
        amount: Decimal,
        payment_date: Optional[datetime] = None
    ) -> Optional[DebtPayment]:
        """Record a payment made toward a debt"""
        if debt_id not in self.debts:
            return None
        
        debt = self.debts[debt_id]
        interest = debt.interest_per_month if debt.current_balance > 0 else Decimal("0")
        principal = min(amount, debt.current_balance + interest)
        
        new_balance = max(Decimal("0"), debt.current_balance - (principal - interest))
        
        payment = DebtPayment(
            debt_id=debt_id,
            amount=amount,
            principal_paid=principal - interest,
            interest_paid=interest if principal > interest else amount,
            payment_date=payment_date or datetime.now(),
            new_balance=new_balance
        )
        
        self.payment_history.append(payment)
        self.update_debt_balance(debt_id, new_balance)
        
        logger.info(f"Payment recorded: {debt.name} - £{amount} (New balance: £{new_balance})")
        return payment
    
    def calculate_snowball_plan(
        self,
        extra_payment: Decimal = Decimal("0")
    ) -> PayoffPlan:
        """Calculate debt payoff using snowball method (lowest balance first)"""
        active_debts = [d for d in self.debts.values() if not d.is_cleared and d.current_balance > 0]
        sorted_debts = sorted(active_debts, key=lambda d: d.current_balance)
        
        return self._calculate_payoff_schedule(sorted_debts, extra_payment, PayoffStrategy.SNOWBALL)
    
    def calculate_avalanche_plan(
        self,
        extra_payment: Decimal = Decimal("0")
    ) -> PayoffPlan:
        """Calculate debt payoff using avalanche method (highest interest first)"""
        active_debts = [d for d in self.debts.values() if not d.is_cleared and d.current_balance > 0]
        sorted_debts = sorted(active_debts, key=lambda d: d.interest_rate_annual, reverse=True)
        
        return self._calculate_payoff_schedule(sorted_debts, extra_payment, PayoffStrategy.AVALANCHE)
    
    def _calculate_payoff_schedule(
        self,
        debts: List[Debt],
        extra_payment: Decimal,
        strategy: PayoffStrategy
    ) -> PayoffPlan:
        """Calculate detailed payoff schedule"""
        if not debts:
            return PayoffPlan(
                strategy=strategy,
                debts_order=[],
                total_monthly_payment=Decimal("0"),
                months_to_debt_free=0,
                total_interest_paid=Decimal("0"),
                payoff_schedule={},
                completion_date=date.today()
            )
        
        monthly_budget = sum(d.monthly_payment for d in debts) + extra_payment
        
        # Simulation
        balances = {d.id: d.current_balance for d in debts}
        rates = {d.id: d.interest_rate_annual for d in debts}
        mins = {d.id: d.min_monthly_payment for d in debts}
        
        schedule = defaultdict(list)
        month = 0
        total_interest = Decimal("0")
        
        while any(b > 0 for b in balances.values()) and month < 1200:  # Max 100 years
            month += 1
            available = monthly_budget
            
            for debt_id in [d.id for d in debts]:
                if balances[debt_id] <= 0:
                    continue
                
                # Calculate interest for this month
                monthly_rate = rates[debt_id] / 12 / 100
                interest = balances[debt_id] * monthly_rate
                total_interest += interest
                balances[debt_id] += interest
                
                # Determine payment
                min_pay = mins[debt_id]
                payment = min(min_pay, balances[debt_id] + interest)
                
                # Add extra to first non-zero debt (snowball/avalanche ordering)
                if available > min_pay and debt_id == next((d for d in debts if balances[d.id] > 0), None).id:
                    extra = min(available - sum(mins[d.id] for d in debts if balances[d.id] > 0), balances[debt_id])
                    payment += extra
                
                payment = min(payment, balances[debt_id])
                balances[debt_id] -= payment
                available -= payment
                
                schedule[debt_id].append({
                    "month": month,
                    "payment": float(payment),
                    "interest": float(interest),
                    "principal": float(payment - interest),
                    "balance": float(max(Decimal("0"), balances[debt_id]))
                })
        
        completion = date.today()
        if month > 0:
            completion = date(
                completion.year + month // 12,
                completion.month + month % 12,
                completion.day
            )
        
        return PayoffPlan(
            strategy=strategy,
            debts_order=[d.id for d in debts],
            total_monthly_payment=monthly_budget,
            months_to_debt_free=month,
            total_interest_paid=total_interest,
            payoff_schedule=dict(schedule),
            completion_date=completion
        )
    
    def compare_strategies(self, extra_payment: Decimal = Decimal("0")) -> Dict[str, Any]:
        """Compare snowball vs avalanche strategies"""
        snowball = self.calculate_snowball_plan(extra_payment)
        avalanche = self.calculate_avalanche_plan(extra_payment)
        
        return {
            "snowball": {
                "months": snowball.months_to_debt_free,
                "total_interest": float(snowball.total_interest_paid),
                "monthly_payment": float(snowball.total_monthly_payment),
                "payoff_order": [self.debts[did].name for did in snowball.debts_order],
                "completion_date": snowball.completion_date.isoformat()
            },
            "avalanche": {
                "months": avalanche.months_to_debt_free,
                "total_interest": float(avalanche.total_interest_paid),
                "monthly_payment": float(avalanche.total_monthly_payment),
                "payoff_order": [self.debts[did].name for did in avalanche.debts_order],
                "completion_date": avalanche.completion_date.isoformat()
            },
            "savings_with_avalanche": float(snowball.total_interest_paid - avalanche.total_interest_paid),
            "recommendation": "avalanche" if avalanche.total_interest_paid < snowball.total_interest_paid else "snowball"
        }
    
    def get_debt_summary(self) -> Dict[str, Any]:
        """Get summary of all debts"""
        total_balance = sum(d.current_balance for d in self.debts.values())
        total_original = sum(d.original_balance for d in self.debts.values())
        total_min_payments = sum(d.min_monthly_payment for d in self.debts.values() if not d.is_cleared)
        
        active_debts = [d for d in self.debts.values() if not d.is_cleared]
        cleared_debts = [d for d in self.debts.values() if d.is_cleared]
        
        weighted_rate = Decimal("0")
        if total_balance > 0:
            weighted_rate = sum(d.current_balance * d.interest_rate_annual for d in active_debts) / total_balance
        
        return {
            "total_debts": len(self.debts),
            "active_debts": len(active_debts),
            "cleared_debts": len(cleared_debts),
            "total_balance": float(total_balance),
            "total_original": float(total_original),
            "total_paid_off": float(total_original - total_balance),
            "percent_paid": float((total_original - total_balance) / total_original * 100) if total_original > 0 else 0,
            "weighted_avg_rate": float(weighted_rate),
            "total_min_monthly_payment": float(total_min_payments),
            "monthly_interest_cost": float(sum(d.interest_per_month for d in active_debts)),
            "by_type": self._group_by_type(),
            "cleared": [
                {"name": d.name, "date": d.cleared_date.isoformat() if d.cleared_date else None}
                for d in cleared_debts
            ]
        }
    
    def _group_by_type(self) -> Dict[str, Any]:
        """Group debts by type"""
        by_type = defaultdict(lambda: {"count": 0, "balance": Decimal("0"), "monthly_payment": Decimal("0")})
        
        for debt in self.debts.values():
            if not debt.is_cleared:
                by_type[debt.debt_type.value]["count"] += 1
                by_type[debt.debt_type.value]["balance"] += debt.current_balance
                by_type[debt.debt_type.value]["monthly_payment"] += debt.monthly_payment
        
        return {k: {**v, "balance": float(v["balance"]), "monthly_payment": float(v["monthly_payment"])} 
                for k, v in by_type.items()}
    
    def get_payment_progress(self, months: int = 12) -> List[Dict[str, Any]]:
        """Get payment progress over time"""
        # Group payments by month
        monthly_totals = defaultdict(lambda: {"principal": Decimal("0"), "interest": Decimal("0")})
        
        for payment in self.payment_history[-months * 30:]:  # Approximate
            month_key = payment.payment_date.strftime("%Y-%m")
            monthly_totals[month_key]["principal"] += payment.principal_paid
            monthly_totals[month_key]["interest"] += payment.interest_paid
        
        return [
            {
                "month": month,
                "principal": float(data["principal"]),
                "interest": float(data["interest"]),
                "total": float(data["principal"] + data["interest"])
            }
            for month, data in sorted(monthly_totals.items())
        ]
    
    def set_monthly_budget(self, amount: Decimal, extra_to_debt: bool = True):
        """Set monthly debt payment budget"""
        self.monthly_budget = amount
        min_required = sum(d.min_monthly_payment for d in self.debts.values() if not d.is_cleared)
        
        if extra_to_debt and amount > min_required:
            self.extra_payment_amount = amount - min_required
        else:
            self.extra_payment_amount = Decimal("0")
        
        logger.info(f"Monthly budget set: £{amount} (Extra: £{self.extra_payment_amount})")


# Global debt manager instance
_debt_manager: Optional[DebtManager] = None


def get_debt_manager() -> DebtManager:
    """Get or create global debt manager"""
    global _debt_manager
    if _debt_manager is None:
        _debt_manager = DebtManager()
    return _debt_manager
