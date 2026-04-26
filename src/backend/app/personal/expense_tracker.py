"""
Expense & Income Tracker
Comprehensive incoming/outgoing tracking with categories
Budget vs actual analysis, spending insights
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime, date, timedelta
from collections import defaultdict
import calendar
import logging

logger = logging.getLogger(__name__)


class ExpenseCategory(Enum):
    # Essential
    HOUSING = "housing"  # Rent, mortgage, council tax
    UTILITIES = "utilities"  # Gas, electric, water
    FOOD = "food"  # Groceries, essentials
    TRANSPORT = "transport"  # Fuel, public transport, car maintenance
    INSURANCE = "insurance"  # Car, home, life, health
    HEALTH = "health"  # NHS, dental, prescriptions, gym
    DEBT_PAYMENTS = "debt_payments"  # Credit cards, loans
    
    # Subscriptions & Services
    SUBSCRIPTIONS = "subscriptions"  # Netflix, Spotify, gym, software
    PHONE_INTERNET = "phone_internet"  # Mobile, broadband
    
    # Discretionary
    DINING_OUT = "dining_out"  # Restaurants, takeaways
    ENTERTAINMENT = "entertainment"  # Events, cinema, hobbies
    SHOPPING = "shopping"  # Clothes, electronics, non-essentials
    TRAVEL = "travel"  # Holidays, hotels, flights
    PERSONAL_CARE = "personal_care"  # Hair, beauty, toiletries
    GIFTS_DONATIONS = "gifts_donations"  # Presents, charity
    EDUCATION = "education"  # Courses, books, training
    
    # Financial
    INVESTMENTS = "investments"  # Stocks, crypto, ISA contributions
    SAVINGS = "savings"  # Emergency fund, savings accounts
    TAX_PAYMENTS = "tax_payments"  # Self assessment, payments on account
    
    # Business (if applicable)
    BUSINESS_EXPENSES = "business_expenses"  # Tools, software, travel
    
    # Other
    OTHER = "other"  # Uncategorized
    FEES = "fees"  # Bank fees, late fees, charges


class IncomeCategory(Enum):
    SALARY = "salary"  # Primary employment
    BONUS = "bonus"  # Performance bonuses
    OVERTIME = "overtime"  # Extra hours
    SELF_EMPLOYMENT = "self_employment"  # Side hustle, freelance
    BENEFITS = "benefits"  # Universal Credit, tax credits, JSA
    PENSION = "pension"  # State pension, private pension
    INVESTMENT_INCOME = "investment_income"  # Dividends, interest
    RENTAL_INCOME = "rental_income"  # Property rental
    GIFTS = "gifts"  # Money received as gifts
    REFUNDS = "refunds"  # Tax refunds, cashback
    SOLD_ITEMS = "sold_items"  # Selling personal items
    OTHER = "other"


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"  # Between own accounts
    REFUND = "refund"  # Expense returned


@dataclass
class Transaction:
    id: str
    date: date
    amount: Decimal
    transaction_type: TransactionType
    category: str  # ExpenseCategory or IncomeCategory value
    subcategory: Optional[str] = None
    description: str = ""
    merchant: Optional[str] = None
    payment_method: str = ""  # card, cash, bank_transfer, direct_debit
    account: str = "default"  # Which account/card
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None  # weekly, monthly, yearly
    receipt_image: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    is_tax_deductible: bool = False
    split_with: Optional[str] = None  # Shared expenses
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Budget:
    category: str
    amount: Decimal
    period: str  # weekly, monthly, yearly
    start_date: date
    rollover: bool = False  # Unused amount rolls to next period
    alert_threshold: float = 0.8  # Alert at 80% spent
    is_essential: bool = True


@dataclass
class SpendingInsight:
    category: str
    period: str
    total_spent: Decimal
    budget_amount: Optional[Decimal]
    percent_of_budget: Optional[float]
    vs_last_month: Optional[float]  # Percentage change
    vs_average: Optional[float]
    trend: str  # increasing, stable, decreasing
    top_merchants: List[Dict[str, Any]]
    frequency: int  # Number of transactions
    average_transaction: Decimal
    largest_transaction: Decimal
    recommendations: List[str]


@dataclass
class CashFlow:
    period: str
    start_date: date
    end_date: date
    total_income: Decimal
    total_expenses: Decimal
    net_flow: Decimal
    by_category_income: Dict[str, Decimal]
    by_category_expenses: Dict[str, Decimal]
    essential_expenses: Decimal
    discretionary_expenses: Decimal
    savings_rate: float


class ExpenseTracker:
    """Comprehensive income and expense tracking"""
    
    # 50/30/20 Rule Guidelines
    ESSENTIAL_CATEGORIES = {
        ExpenseCategory.HOUSING, ExpenseCategory.UTILITIES, ExpenseCategory.FOOD,
        ExpenseCategory.TRANSPORT, ExpenseCategory.INSURANCE, ExpenseCategory.HEALTH,
        ExpenseCategory.DEBT_PAYMENTS, ExpenseCategory.SUBSCRIPTIONS, ExpenseCategory.PHONE_INTERNET
    }
    
    DISCRETIONARY_CATEGORIES = {
        ExpenseCategory.DINING_OUT, ExpenseCategory.ENTERTAINMENT, ExpenseCategory.SHOPPING,
        ExpenseCategory.TRAVEL, ExpenseCategory.PERSONAL_CARE, ExpenseCategory.GIFTS_DONATIONS,
        ExpenseCategory.EDUCATION
    }
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.budgets: Dict[str, Budget] = {}  # category -> Budget
        self.accounts: Dict[str, Decimal] = {}  # account_name -> current_balance
        self.recurring_transactions: List[Transaction] = []
        self.cashback_earned: Decimal = Decimal("0")
        
    def add_transaction(
        self,
        date: date,
        amount: Decimal,
        transaction_type: TransactionType,
        category: str,
        description: str,
        subcategory: Optional[str] = None,
        merchant: Optional[str] = None,
        payment_method: str = "",
        account: str = "default",
        is_recurring: bool = False,
        tags: Optional[List[str]] = None,
        notes: str = "",
        is_tax_deductible: bool = False
    ) -> Transaction:
        """Add new transaction"""
        txn_id = f"txn_{len(self.transactions) + 1}_{datetime.now().timestamp()}"
        
        txn = Transaction(
            id=txn_id,
            date=date,
            amount=amount,
            transaction_type=transaction_type,
            category=category,
            subcategory=subcategory,
            description=description,
            merchant=merchant,
            payment_method=payment_method,
            account=account,
            is_recurring=is_recurring,
            tags=tags or [],
            notes=notes,
            is_tax_deductible=is_tax_deductible
        )
        
        self.transactions.append(txn)
        
        # Update account balance
        if account not in self.accounts:
            self.accounts[account] = Decimal("0")
        
        if transaction_type == TransactionType.INCOME:
            self.accounts[account] += amount
        elif transaction_type == TransactionType.EXPENSE:
            self.accounts[account] -= amount
        elif transaction_type == TransactionType.REFUND:
            self.accounts[account] += amount
        
        logger.info(f"Transaction added: {description} - £{amount} ({category})")
        return txn
    
    def set_budget(
        self,
        category: str,
        amount: Decimal,
        period: str = "monthly",
        rollover: bool = False,
        alert_threshold: float = 0.8
    ) -> Budget:
        """Set budget for category"""
        budget = Budget(
            category=category,
            amount=amount,
            period=period,
            start_date=date.today(),
            rollover=rollover,
            alert_threshold=alert_threshold,
            is_essential=category in [c.value for c in self.ESSENTIAL_CATEGORIES]
        )
        
        self.budgets[category] = budget
        logger.info(f"Budget set: {category} = £{amount} ({period})")
        return budget
    
    def get_spending_by_category(
        self,
        start_date: date,
        end_date: date,
        transaction_type: TransactionType = TransactionType.EXPENSE
    ) -> Dict[str, Decimal]:
        """Get spending grouped by category for period"""
        spending = defaultdict(Decimal)
        
        for txn in self.transactions:
            if start_date <= txn.date <= end_date and txn.transaction_type == transaction_type:
                spending[txn.category] += txn.amount
        
        return dict(spending)
    
    def get_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Get complete monthly financial summary"""
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        # Income
        income_by_category = defaultdict(Decimal)
        total_income = Decimal("0")
        
        # Expenses
        expenses_by_category = defaultdict(Decimal)
        total_expenses = Decimal("0")
        essential_expenses = Decimal("0")
        discretionary_expenses = Decimal("0")
        
        for txn in self.transactions:
            if start_date <= txn.date <= end_date:
                if txn.transaction_type == TransactionType.INCOME:
                    income_by_category[txn.category] += txn.amount
                    total_income += txn.amount
                elif txn.transaction_type == TransactionType.EXPENSE:
                    expenses_by_category[txn.category] += txn.amount
                    total_expenses += txn.amount
                    
                    # Classify essential vs discretionary
                    try:
                        cat_enum = ExpenseCategory(txn.category)
                        if cat_enum in self.ESSENTIAL_CATEGORIES:
                            essential_expenses += txn.amount
                        elif cat_enum in self.DISCRETIONARY_CATEGORIES:
                            discretionary_expenses += txn.amount
                    except ValueError:
                        # Unknown category, treat as essential
                        essential_expenses += txn.amount
        
        # Budget vs actual
        budget_analysis = []
        for category, budget in self.budgets.items():
            actual = expenses_by_category.get(category, Decimal("0"))
            percent_used = float(actual / budget.amount * 100) if budget.amount > 0 else 0
            
            budget_analysis.append({
                "category": category,
                "budget": float(budget.amount),
                "actual": float(actual),
                "remaining": float(budget.amount - actual),
                "percent_used": round(percent_used, 1),
                "alert": percent_used >= budget.alert_threshold * 100,
                "overspent": actual > budget.amount
            })
        
        # 50/30/20 Analysis
        essential_percent = float(essential_expenses / total_income * 100) if total_income > 0 else 0
        discretionary_percent = float(discretionary_expenses / total_income * 100) if total_income > 0 else 0
        savings = total_income - total_expenses
        savings_rate = float(savings / total_income * 100) if total_income > 0 else 0
        
        return {
            "period": f"{year}-{month:02d}",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "income": {
                "total": float(total_income),
                "by_category": {k: float(v) for k, v in income_by_category.items()}
            },
            "expenses": {
                "total": float(total_expenses),
                "by_category": {k: float(v) for k, v in expenses_by_category.items()},
                "essential": float(essential_expenses),
                "discretionary": float(discretionary_expenses),
                "essential_percent": round(essential_percent, 1),
                "discretionary_percent": round(discretionary_percent, 1)
            },
            "cash_flow": {
                "net": float(savings),
                "savings_rate": round(savings_rate, 1),
                "target_savings_rate": 20,
                "on_target": savings_rate >= 20
            },
            "budget_analysis": sorted(budget_analysis, key=lambda x: x["percent_used"], reverse=True),
            "rule_50_30_20": {
                "needs_target": 50,
                "wants_target": 30,
                "savings_target": 20,
                "needs_actual": round(essential_percent, 1),
                "wants_actual": round(discretionary_percent, 1),
                "savings_actual": round(savings_rate, 1),
                "assessment": self._assess_50_30_20(essential_percent, discretionary_percent, savings_rate)
            }
        }
    
    def _assess_50_30_20(self, needs: float, wants: float, savings: float) -> str:
        """Assess 50/30/20 rule adherence"""
        if needs <= 55 and savings >= 15:
            return "Excellent - Well within guidelines"
        elif needs <= 60 and savings >= 10:
            return "Good - Minor adjustments needed"
        elif needs <= 70:
            return "Fair - Consider reducing essential expenses"
        else:
            return "Needs attention - Essential expenses too high"
    
    def get_spending_insights(
        self,
        category: str,
        months: int = 3
    ) -> Optional[SpendingInsight]:
        """Generate insights for specific spending category"""
        end_date = date.today()
        start_date = end_date - timedelta(days=30*months)
        
        # Get transactions for this category
        category_txns = [
            txn for txn in self.transactions
            if txn.category == category
            and txn.transaction_type == TransactionType.EXPENSE
            and start_date <= txn.date <= end_date
        ]
        
        if not category_txns:
            return None
        
        total = sum(txn.amount for txn in category_txns)
        avg_transaction = total / len(category_txns)
        largest = max(txn.amount for txn in category_txns)
        
        # Top merchants
        merchant_totals = defaultdict(Decimal)
        for txn in category_txns:
            if txn.merchant:
                merchant_totals[txn.merchant] += txn.amount
        
        top_merchants = [
            {"name": name, "amount": float(amount), "percent": float(amount/total*100)}
            for name, amount in sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Compare to budget
        budget = self.budgets.get(category)
        budget_percent = None
        if budget:
            monthly_avg = total / months
            budget_percent = float(monthly_avg / budget.amount * 100)
        
        # Generate recommendations
        recommendations = []
        if budget_percent and budget_percent > 100:
            recommendations.append(f"Over budget by {budget_percent-100:.0f}%. Consider reducing spending.")
        if len(category_txns) > 20:  # More than 20 transactions in 3 months
            recommendations.append("High frequency of transactions. Consider consolidating purchases.")
        if float(avg_transaction) > 50:
            recommendations.append("Large average transaction size. Look for bulk discounts or alternatives.")
        
        return SpendingInsight(
            category=category,
            period=f"Last {months} months",
            total_spent=total,
            budget_amount=budget.amount if budget else None,
            percent_of_budget=budget_percent,
            vs_last_month=None,  # Would need previous period
            vs_average=None,
            trend="stable",  # Simplified
            top_merchants=top_merchants,
            frequency=len(category_txns),
            average_transaction=avg_transaction,
            largest_transaction=largest,
            recommendations=recommendations
        )
    
    def get_cash_flow_forecast(self, months: int = 3) -> List[Dict[str, Any]]:
        """Forecast future cash flow based on recurring transactions"""
        forecast = []
        today = date.today()
        
        for i in range(months):
            forecast_month = today + timedelta(days=30*i)
            month_start = date(forecast_month.year, forecast_month.month, 1)
            month_end = date(forecast_month.year, forecast_month.month, 
                           calendar.monthrange(forecast_month.year, forecast_month.month)[1])
            
            # Calculate expected income from recurring
            expected_income = Decimal("0")
            expected_expenses = Decimal("0")
            
            for txn in self.recurring_transactions:
                if txn.recurring_frequency == "monthly":
                    if txn.transaction_type == TransactionType.INCOME:
                        expected_income += txn.amount
                    else:
                        expected_expenses += txn.amount
            
            # Add historical average for non-recurring
            historical = self.get_monthly_summary(month_start.year, month_start.month)
            if historical:
                non_recurring_income = Decimal(str(historical["income"]["total"])) - expected_income
                non_recurring_expenses = Decimal(str(historical["expenses"]["total"])) - expected_expenses
                
                expected_income += max(Decimal("0"), non_recurring_income * Decimal("0.8"))
                expected_expenses += max(Decimal("0"), non_recurring_expenses * Decimal("0.9"))
            
            forecast.append({
                "month": month_start.strftime("%Y-%m"),
                "expected_income": float(expected_income),
                "expected_expenses": float(expected_expenses),
                "expected_net": float(expected_income - expected_expenses),
                "confidence": "high" if len(self.recurring_transactions) > 5 else "medium"
            })
        
        return forecast
    
    def detect_unusual_spending(self, threshold_percent: float = 20.0) -> List[Dict[str, Any]]:
        """Detect unusual spending patterns"""
        alerts = []
        
        # Compare this month vs last month
        today = date.today()
        this_month = self.get_monthly_summary(today.year, today.month)
        
        last_month = today - timedelta(days=30)
        last_month_data = self.get_monthly_summary(last_month.year, last_month.month)
        
        for category, amount in this_month["expenses"]["by_category"].items():
            last_amount = last_month_data["expenses"]["by_category"].get(category, 0)
            if last_amount > 0:
                change = (amount - last_amount) / last_amount * 100
                if abs(change) > threshold_percent:
                    alerts.append({
                        "category": category,
                        "change_percent": round(change, 1),
                        "direction": "increase" if change > 0 else "decrease",
                        "this_month": amount,
                        "last_month": last_amount,
                        "severity": "high" if abs(change) > 50 else "medium"
                    })
        
        return sorted(alerts, key=lambda x: abs(x["change_percent"]), reverse=True)
    
    def get_essential_vs_discretionary(self, year: int, month: int) -> Dict[str, Any]:
        """Break down spending by essential vs discretionary"""
        summary = self.get_monthly_summary(year, month)
        
        essential = summary["expenses"]["essential"]
        discretionary = summary["expenses"]["discretionary"]
        total = essential + discretionary
        income = summary["income"]["total"]
        
        return {
            "period": summary["period"],
            "essential": {
                "amount": essential,
                "percent_of_income": round(float(essential / income * 100), 1) if income > 0 else 0,
                "categories": [c.value for c in self.ESSENTIAL_CATEGORIES]
            },
            "discretionary": {
                "amount": discretionary,
                "percent_of_income": round(float(discretionary / income * 100), 1) if income > 0 else 0,
                "categories": [c.value for c in self.DISCRETIONARY_CATEGORIES]
            },
            "total_spending": total,
            "remaining": float(income - total),
            "recommendation": self._get_spending_recommendation(
                float(essential / income * 100) if income > 0 else 0,
                float(discretionary / income * 100) if income > 0 else 0
            )
        }
    
    def _get_spending_recommendation(self, essential_pct: float, discretionary_pct: float) -> str:
        """Generate spending recommendation"""
        if essential_pct > 70:
            return "Essential expenses are high. Focus on reducing housing, transport, or debt costs."
        elif discretionary_pct > 40:
            return "Discretionary spending is high. Look for areas to cut back on wants vs needs."
        elif essential_pct + discretionary_pct > 90:
            return "Low savings rate. Aim to save at least 10% of income."
        else:
            return "Healthy spending balance. Keep maintaining your budget!"


# Global tracker
_expense_tracker: Optional[ExpenseTracker] = None


def get_expense_tracker() -> ExpenseTracker:
    """Get or create global expense tracker"""
    global _expense_tracker
    if _expense_tracker is None:
        _expense_tracker = ExpenseTracker()
    return _expense_tracker
