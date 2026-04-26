"""
Expense & Income Tracker API Endpoints
Comprehensive transaction tracking with categories and budgets
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import date

from ..personal.expense_tracker import (
    get_expense_tracker, 
    ExpenseCategory, 
    IncomeCategory, 
    TransactionType
)
from ..personal.budget_rules import get_budget_engine, BudgetRuleType
from ..personal.employment_income_tracker import (
    get_employment_tracker, 
    EmploymentType, 
    PayFrequency, 
    TaxStatus
)

router = APIRouter(prefix="/expenses", tags=["Expense & Income Tracker"])


# ==================== TRANSACTION ENDPOINTS ====================

class AddTransactionRequest(BaseModel):
    date: date
    amount: Decimal = Field(..., gt=0)
    transaction_type: str  # income, expense, transfer, refund
    category: str
    description: str
    subcategory: Optional[str] = None
    merchant: Optional[str] = None
    payment_method: str = "card"  # card, cash, bank_transfer, direct_debit
    account: str = "default"
    is_recurring: bool = False
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    is_tax_deductible: bool = False


@router.post("/transaction")
async def add_transaction(req: AddTransactionRequest):
    """Add new income or expense transaction"""
    tracker = get_expense_tracker()
    
    try:
        txn_type = TransactionType(req.transaction_type.lower())
    except ValueError:
        raise HTTPException(400, f"Invalid type. Options: income, expense, transfer, refund")
    
    txn = tracker.add_transaction(
        date=req.date,
        amount=req.amount,
        transaction_type=txn_type,
        category=req.category,
        description=req.description,
        subcategory=req.subcategory,
        merchant=req.merchant,
        payment_method=req.payment_method,
        account=req.account,
        is_recurring=req.is_recurring,
        tags=req.tags,
        notes=req.notes or "",
        is_tax_deductible=req.is_tax_deductible
    )
    
    return {
        "transaction_id": txn.id,
        "date": txn.date.isoformat(),
        "amount": float(txn.amount),
        "type": txn.transaction_type.value,
        "category": txn.category,
        "description": txn.description,
        "account_balance": float(tracker.accounts.get(txn.account, 0))
    }


@router.get("/transactions")
async def list_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    account: Optional[str] = None,
    limit: int = 100
):
    """List transactions with filters"""
    tracker = get_expense_tracker()
    
    filtered = tracker.transactions
    
    if start_date:
        filtered = [t for t in filtered if t.date >= start_date]
    if end_date:
        filtered = [t for t in filtered if t.date <= end_date]
    if category:
        filtered = [t for t in filtered if t.category == category]
    if transaction_type:
        filtered = [t for t in filtered if t.transaction_type.value == transaction_type]
    if account:
        filtered = [t for t in filtered if t.account == account]
    
    # Sort by date descending, take limit
    filtered = sorted(filtered, key=lambda x: x.date, reverse=True)[:limit]
    
    return {
        "count": len(filtered),
        "transactions": [
            {
                "id": t.id,
                "date": t.date.isoformat(),
                "amount": float(t.amount),
                "type": t.transaction_type.value,
                "category": t.category,
                "subcategory": t.subcategory,
                "description": t.description,
                "merchant": t.merchant,
                "payment_method": t.payment_method,
                "account": t.account,
                "is_recurring": t.is_recurring,
                "tags": t.tags,
                "is_tax_deductible": t.is_tax_deductible
            }
            for t in filtered
        ]
    }


@router.delete("/transaction/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """Delete a transaction"""
    tracker = get_expense_tracker()
    
    # Find and remove
    for i, txn in enumerate(tracker.transactions):
        if txn.id == transaction_id:
            removed = tracker.transactions.pop(i)
            # Reverse account balance adjustment
            if removed.account in tracker.accounts:
                if removed.transaction_type == TransactionType.INCOME:
                    tracker.accounts[removed.account] -= removed.amount
                elif removed.transaction_type == TransactionType.EXPENSE:
                    tracker.accounts[removed.account] += removed.amount
            return {"deleted": True, "transaction": removed.description}
    
    raise HTTPException(404, "Transaction not found")


# ==================== CATEGORIES ENDPOINTS ====================

@router.get("/categories/expense")
async def expense_categories():
    """Get all expense categories"""
    categories = []
    
    # Group by type
    essential = [
        ExpenseCategory.HOUSING, ExpenseCategory.UTILITIES, ExpenseCategory.FOOD,
        ExpenseCategory.TRANSPORT, ExpenseCategory.INSURANCE, ExpenseCategory.HEALTH,
        ExpenseCategory.DEBT_PAYMENTS
    ]
    subscriptions = [ExpenseCategory.SUBSCRIPTIONS, ExpenseCategory.PHONE_INTERNET]
    discretionary = [
        ExpenseCategory.DINING_OUT, ExpenseCategory.ENTERTAINMENT, ExpenseCategory.SHOPPING,
        ExpenseCategory.TRAVEL, ExpenseCategory.PERSONAL_CARE, ExpenseCategory.GIFTS_DONATIONS,
        ExpenseCategory.EDUCATION
    ]
    financial = [ExpenseCategory.INVESTMENTS, ExpenseCategory.SAVINGS, ExpenseCategory.TAX_PAYMENTS]
    
    return {
        "essential": [{"id": c.value, "name": c.name.replace("_", " ").title(), "priority": "high"} for c in essential],
        "subscriptions": [{"id": c.value, "name": c.name.replace("_", " ").title(), "priority": "medium"} for c in subscriptions],
        "discretionary": [{"id": c.value, "name": c.name.replace("_", " ").title(), "priority": "low"} for c in discretionary],
        "financial": [{"id": c.value, "name": c.name.replace("_", " ").title(), "priority": "savings"} for c in financial],
        "other": [{"id": c.value, "name": c.name.replace("_", " ").title()} for c in [ExpenseCategory.OTHER, ExpenseCategory.FEES, ExpenseCategory.BUSINESS_EXPENSES]]
    }


@router.get("/categories/income")
async def income_categories():
    """Get all income categories"""
    return {
        "categories": [
            {"id": c.value, "name": c.name.replace("_", " ").title()}
            for c in IncomeCategory
        ]
    }


# ==================== BUDGET ENDPOINTS ====================

class SetBudgetRequest(BaseModel):
    category: str
    amount: Decimal = Field(..., gt=0)
    period: str = "monthly"  # weekly, monthly, yearly
    rollover: bool = False
    alert_threshold: float = 0.8


@router.post("/budget")
async def set_budget(req: SetBudgetRequest):
    """Set budget for a category"""
    tracker = get_expense_tracker()
    
    budget = tracker.set_budget(
        category=req.category,
        amount=req.amount,
        period=req.period,
        rollover=req.rollover,
        alert_threshold=req.alert_threshold
    )
    
    return {
        "category": budget.category,
        "amount": float(budget.amount),
        "period": budget.period,
        "is_essential": budget.is_essential,
        "alert_at_percent": budget.alert_threshold * 100
    }


@router.get("/budgets")
async def list_budgets():
    """List all budgets"""
    tracker = get_expense_tracker()
    
    return {
        "budgets": [
            {
                "category": b.category,
                "amount": float(b.amount),
                "period": b.period,
                "is_essential": b.is_essential,
                "rollover": b.rollover
            }
            for b in tracker.budgets.values()
        ],
        "total_budgeted": float(sum(b.amount for b in tracker.budgets.values())),
        "essential_budget": float(sum(b.amount for b in tracker.budgets.values() if b.is_essential)),
        "discretionary_budget": float(sum(b.amount for b in tracker.budgets.values() if not b.is_essential))
    }


@router.delete("/budget/{category}")
async def delete_budget(category: str):
    """Remove a budget"""
    tracker = get_expense_tracker()
    
    if category in tracker.budgets:
        del tracker.budgets[category]
        return {"deleted": True, "category": category}
    
    raise HTTPException(404, "Budget not found")


# ==================== SUMMARY & ANALYSIS ENDPOINTS ====================

@router.get("/summary/monthly/{year}/{month}")
async def monthly_summary(year: int, month: int):
    """Get complete monthly financial summary"""
    tracker = get_expense_tracker()
    return tracker.get_monthly_summary(year, month)


@router.get("/summary/essential-vs-discretionary/{year}/{month}")
async def essential_discretionary_breakdown(year: int, month: int):
    """Break down spending by essential vs discretionary"""
    tracker = get_expense_tracker()
    return tracker.get_essential_vs_discretionary(year, month)


@router.get("/summary/by-category")
async def spending_by_category(
    start_date: date,
    end_date: date,
    transaction_type: str = "expense"
):
    """Get spending grouped by category"""
    tracker = get_expense_tracker()
    
    try:
        txn_type = TransactionType(transaction_type)
    except ValueError:
        raise HTTPException(400, "Invalid transaction type")
    
    spending = tracker.get_spending_by_category(start_date, end_date, txn_type)
    
    total = sum(spending.values())
    
    return {
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "transaction_type": transaction_type,
        "total": float(total),
        "by_category": [
            {
                "category": cat,
                "amount": float(amount),
                "percent": round(float(amount / total * 100), 1) if total > 0 else 0
            }
            for cat, amount in sorted(spending.items(), key=lambda x: x[1], reverse=True)
        ]
    }


# ==================== INSIGHTS & FORECAST ENDPOINTS ====================

@router.get("/insights/{category}")
async def category_insights(category: str, months: int = 3):
    """Get spending insights for a category"""
    tracker = get_expense_tracker()
    
    insight = tracker.get_spending_insights(category, months)
    
    if not insight:
        raise HTTPException(404, f"No data for category '{category}' in last {months} months")
    
    return {
        "category": insight.category,
        "period": insight.period,
        "total_spent": float(insight.total_spent),
        "budget_amount": float(insight.budget_amount) if insight.budget_amount else None,
        "percent_of_budget": round(insight.percent_of_budget, 1) if insight.percent_of_budget else None,
        "frequency": insight.frequency,
        "average_transaction": float(insight.average_transaction),
        "largest_transaction": float(insight.largest_transaction),
        "top_merchants": insight.top_merchants,
        "recommendations": insight.recommendations
    }


@router.get("/forecast")
async def cash_flow_forecast(months: int = 3):
    """Forecast future cash flow based on recurring transactions"""
    tracker = get_expense_tracker()
    return {"forecast": tracker.get_cash_flow_forecast(months)}


@router.get("/alerts/unusual-spending")
async def detect_unusual_spending(threshold_percent: float = 20.0):
    """Detect unusual spending patterns"""
    tracker = get_expense_tracker()
    alerts = tracker.detect_unusual_spending(threshold_percent)
    
    return {
        "alert_count": len(alerts),
        "threshold_percent": threshold_percent,
        "alerts": alerts
    }


# ==================== ACCOUNTS ENDPOINTS ====================

@router.get("/accounts")
async def list_accounts():
    """List all tracked accounts with balances"""
    tracker = get_expense_tracker()
    
    return {
        "accounts": [
            {"name": name, "balance": float(balance)}
            for name, balance in tracker.accounts.items()
        ],
        "total_balance": float(sum(tracker.accounts.values()))
    }


@router.post("/account/{name}/adjust")
async def adjust_account_balance(name: str, new_balance: Decimal):
    """Manually adjust account balance (for reconciliation)"""
    tracker = get_expense_tracker()
    
    old_balance = tracker.accounts.get(name, Decimal("0"))
    tracker.accounts[name] = new_balance
    
    return {
        "account": name,
        "old_balance": float(old_balance),
        "new_balance": float(new_balance),
        "adjustment": float(new_balance - old_balance)
    }


# ==================== DASHBOARD ENDPOINT ====================

@router.get("/dashboard")
async def expense_dashboard():
    """Get expense tracker dashboard summary"""
    tracker = get_expense_tracker()
    
    today = date.today()
    current_month = tracker.get_monthly_summary(today.year, today.month)
    
    # Get last month for comparison
    last_month_date = today.replace(day=1) - timedelta(days=1)
    last_month = tracker.get_monthly_summary(last_month_date.year, last_month_date.month)
    
    # Recent transactions
    recent = sorted(tracker.transactions, key=lambda x: x.date, reverse=True)[:10]
    
    # Budget alerts
    budget_alerts = [
        b for b in current_month.get("budget_analysis", [])
        if b.get("alert") or b.get("overspent")
    ]
    
    return {
        "current_month": {
            "period": current_month["period"],
            "income": current_month["income"]["total"],
            "expenses": current_month["expenses"]["total"],
            "net": current_month["cash_flow"]["net"],
            "savings_rate": current_month["cash_flow"]["savings_rate"]
        },
        "last_month": {
            "period": last_month["period"],
            "income": last_month["income"]["total"],
            "expenses": last_month["expenses"]["total"],
            "net": last_month["cash_flow"]["net"]
        },
        "vs_last_month": {
            "income_change": round(
                (current_month["income"]["total"] - last_month["income"]["total"]) / last_month["income"]["total"] * 100, 1
            ) if last_month["income"]["total"] > 0 else 0,
            "expense_change": round(
                (current_month["expenses"]["total"] - last_month["expenses"]["total"]) / last_month["expenses"]["total"] * 100, 1
            ) if last_month["expenses"]["total"] > 0 else 0
        },
        "budget_status": {
            "total_budgets": len(tracker.budgets),
            "alerts": len(budget_alerts),
            "overspent": len([b for b in budget_alerts if b.get("overspent")])
        },
        "recent_transactions": [
            {
                "date": t.date.isoformat(),
                "description": t.description,
                "amount": float(t.amount),
                "category": t.category,
                "type": t.transaction_type.value
            }
            for t in recent
        ],
        "accounts": {
            "count": len(tracker.accounts),
            "total_balance": float(sum(tracker.accounts.values()))
        }
    }


# ==================== BUDGET RULES ENDPOINTS ====================

class BudgetRecommendationRequest(BaseModel):
    income: Decimal
    age: int
    has_debt: bool = False
    family_size: int = 1
    lifestyle: str = "balanced"  # frugal, balanced, luxury
    discipline_level: str = "medium"  # low, medium, high


class BudgetAnalysisRequest(BaseModel):
    rule_type: str  # 50_30_20, 90_10, 60_20_20, etc.
    income: Decimal
    spending: Dict[str, Decimal]


@router.get("/budget-rules")
async def list_budget_rules():
    """Get all available budget rules"""
    engine = get_budget_engine()
    rules = engine.get_all_rules()
    
    return {
        "rules": [
            {
                "type": r.rule_type.value,
                "name": r.name,
                "description": r.description,
                "allocations": r.allocations,
                "savings_rate": r.savings_rate,
                "difficulty": r.difficulty,
                "flexibility": r.flexibility,
                "ideal_for": r.ideal_for,
                "pros": r.pros,
                "cons": r.cons
            }
            for r in rules.values()
        ]
    }


@router.post("/budget-rules/recommend")
async def recommend_budget_rule(req: BudgetRecommendationRequest):
    """Get personalized budget rule recommendations"""
    engine = get_budget_engine()
    
    recommendations = engine.recommend_rule(
        income=req.income,
        age=req.age,
        has_debt=req.has_debt,
        family_size=req.family_size,
        lifestyle=req.lifestyle,
        discipline_level=req.discipline_level
    )
    
    return {
        "profile": {
            "income": float(req.income),
            "age": req.age,
            "has_debt": req.has_debt,
            "family_size": req.family_size,
            "lifestyle": req.lifestyle,
            "discipline": req.discipline_level
        },
        "recommendations": recommendations,
        "top_pick": recommendations[0] if recommendations else None
    }


@router.post("/budget-rules/analyze")
async def analyze_against_rule(req: BudgetAnalysisRequest):
    """Analyze spending against a specific budget rule"""
    engine = get_budget_engine()
    
    try:
        rule_type = BudgetRuleType(req.rule_type)
    except ValueError:
        valid_types = [t.value for t in BudgetRuleType]
        raise HTTPException(400, f"Invalid rule_type. Options: {valid_types}")
    
    analysis = engine.analyze_against_rule(rule_type, req.income, req.spending)
    
    return {
        "rule": engine.RULES[rule_type].name,
        "income": float(analysis.income),
        "compliance_score": analysis.compliance_score,
        "target_allocation": {k: float(v) for k, v in analysis.target_allocation.items()},
        "actual_spending": {k: float(v) for k, v in analysis.actual_spending.items()},
        "variance": {k: float(v) for k, v in analysis.variance.items()},
        "variance_percent": analysis.variance_percent,
        "on_track_categories": analysis.on_track_categories,
        "off_track_categories": analysis.off_track_categories,
        "recommendations": analysis.recommendations,
        "projected_annual_savings": float(analysis.projected_savings_annual),
        "years_to_financial_independence": analysis.years_to_financial_independence
    }


@router.post("/budget-rules/compare-all")
async def compare_all_rules(
    income: Decimal,
    spending: Dict[str, Decimal]
):
    """Compare spending against all budget rules"""
    engine = get_budget_engine()
    return engine.compare_all_rules(income, spending)


@router.post("/budget-rules/transition-plan")
async def create_transition_plan(
    current_rule: str,
    target_rule: str,
    income: Decimal,
    spending: Dict[str, Decimal]
):
    """Create plan to transition between budget rules"""
    engine = get_budget_engine()
    
    try:
        current = BudgetRuleType(current_rule)
        target = BudgetRuleType(target_rule)
    except ValueError:
        raise HTTPException(400, "Invalid rule type")
    
    plan = engine.create_action_plan(current, target, income, spending)
    return plan


# ==================== EMPLOYMENT & INCOME TRACKING ENDPOINTS ====================

class AddIncomeSourceRequest(BaseModel):
    name: str
    employment_type: str  # full_time, part_time, contract, freelance, etc.
    employer_client: str
    pay_frequency: str  # weekly, monthly, quarterly, irregular, etc.
    tax_status: str  # paye, self_assessment, ir35_inside, ir35_outside
    day_rate: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    annual_salary: Optional[Decimal] = None
    standard_hours_per_week: Optional[Decimal] = None
    typical_days_per_month: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    includes_pension: bool = False
    includes_bonus: bool = False
    is_active: bool = True


class RecordPaymentRequest(BaseModel):
    source_id: str
    date: date
    gross_amount: Decimal
    tax_deducted: Decimal
    ni_deducted: Decimal
    net_amount: Optional[Decimal] = None
    hours_worked: Optional[Decimal] = None
    days_worked: Optional[int] = None
    is_bonus: bool = False
    is_overtime: bool = False
    description: str = ""


@router.post("/income-source")
async def add_income_source(req: AddIncomeSourceRequest):
    """Add a new income source/employment"""
    tracker = get_employment_tracker()
    
    try:
        emp_type = EmploymentType(req.employment_type.lower())
        pay_freq = PayFrequency(req.pay_frequency.lower())
        tax_stat = TaxStatus(req.tax_status.lower())
    except ValueError as e:
        raise HTTPException(400, f"Invalid enum value: {e}")
    
    source = tracker.add_income_source(
        name=req.name,
        employment_type=emp_type,
        employer_client=req.employer_client,
        pay_frequency=pay_freq,
        tax_status=tax_stat,
        day_rate=req.day_rate,
        hourly_rate=req.hourly_rate,
        annual_salary=req.annual_salary,
        standard_hours_per_week=req.standard_hours_per_week,
        typical_days_per_month=req.typical_days_per_month,
        start_date=req.start_date,
        end_date=req.end_date,
        includes_pension=req.includes_pension,
        includes_bonus=req.includes_bonus,
        is_active=req.is_active
    )
    
    return {
        "source_id": source.id,
        "name": source.name,
        "type": source.employment_type.value,
        "employer": source.employer_client,
        "frequency": source.pay_frequency.value,
        "tax_status": source.tax_status.value
    }


@router.post("/income-payment")
async def record_income_payment(req: RecordPaymentRequest):
    """Record an income payment"""
    tracker = get_employment_tracker()
    
    payment = tracker.record_payment(
        source_id=req.source_id,
        date=req.date,
        gross_amount=req.gross_amount,
        tax_deducted=req.tax_deducted,
        ni_deducted=req.ni_deducted,
        net_amount=req.net_amount,
        hours_worked=req.hours_worked,
        days_worked=req.days_worked,
        is_bonus=req.is_bonus,
        is_overtime=req.is_overtime,
        description=req.description
    )
    
    return {
        "payment_id": payment.id,
        "source": tracker.income_sources.get(req.source_id, {}).name if req.source_id in tracker.income_sources else "Unknown",
        "date": payment.date.isoformat(),
        "gross": float(payment.gross_amount),
        "tax": float(payment.tax_deducted),
        "ni": float(payment.ni_deducted),
        "net": float(payment.net_amount)
    }


@router.get("/income-sources")
async def list_income_sources(active_only: bool = True):
    """List all income sources"""
    tracker = get_employment_tracker()
    
    sources = [s for s in tracker.income_sources.values() if not active_only or s.is_active]
    
    return {
        "count": len(sources),
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "type": s.employment_type.value,
                "employer": s.employer_client,
                "frequency": s.pay_frequency.value,
                "tax_status": s.tax_status.value,
                "is_active": s.is_active,
                "annual_estimate": float(
                    (s.annual_salary or 0) or 
                    ((s.day_rate or 0) * (s.typical_days_per_month or 0) * 12) or
                    ((s.hourly_rate or 0) * (s.standard_hours_per_week or 0) * 52)
                )
            }
            for s in sources
        ]
    }


@router.get("/income/summary")
async def income_summary(start_date: date, end_date: date):
    """Get income summary for a period"""
    tracker = get_employment_tracker()
    return tracker.get_income_summary(start_date, end_date)


@router.get("/income/by-employment-type")
async def income_by_employment_type():
    """Get breakdown by employment type"""
    tracker = get_employment_tracker()
    return tracker.get_employment_type_breakdown()


@router.get("/income/tax-summary/{tax_year}")
async def tax_summary(tax_year: int = 2026):
    """Get tax summary for self-assessment"""
    tracker = get_employment_tracker()
    return tracker.get_tax_summary(tax_year)


@router.get("/income/forecast")
async def income_forecast(months: int = 3):
    """Forecast income for next N months"""
    tracker = get_employment_tracker()
    forecasts = tracker.forecast_income(months)
    
    return {
        "forecast_period_months": months,
        "forecasts": [
            {
                "source": tracker.income_sources.get(f.source_id, {}).name if f.source_id in tracker.income_sources else "Unknown",
                "period": f.period_start.strftime("%Y-%m"),
                "predicted_gross": float(f.predicted_gross),
                "predicted_net": float(f.predicted_net),
                "confidence": f.confidence,
                "factors": f.factors
            }
            for f in forecasts
        ],
        "total_predicted_monthly": float(sum(f.predicted_net for f in forecasts)) / months if forecasts else 0
    }


@router.get("/income/employment-types")
async def employment_types_reference():
    """Get reference data for all employment types"""
    return {
        "employment_types": [
            {
                "id": t.value,
                "name": t.name.replace("_", " ").title(),
                "typical_tax_status": "paye" if t in [EmploymentType.FULL_TIME, EmploymentType.PART_TIME, EmploymentType.ZERO_HOURS] else "self_assessment",
                "common_for": "Traditional employment" if t in [EmploymentType.FULL_TIME, EmploymentType.PART_TIME] else "Flexible work"
            }
            for t in EmploymentType
        ],
        "pay_frequencies": [
            {"id": f.value, "name": f.name.replace("_", " ").title()}
            for f in PayFrequency
        ],
        "tax_statuses": [
            {
                "id": s.value,
                "name": s.name.replace("_", " ").title(),
                "description": {
                    TaxStatus.PAYE: "Employer deducts tax automatically",
                    TaxStatus.SELF_ASSESSMENT: "You report and pay tax via Self Assessment",
                    TaxStatus.IR35_INSIDE: "Contractor taxed as employee",
                    TaxStatus.IR35_OUTSIDE: "Genuine contractor status",
                    TaxStatus.MIXED: "Combination of PAYE and Self Assessment"
                }.get(s, "")
            }
            for s in TaxStatus
        ]
    }


@router.get("/income/irregular-buffer/{source_id}")
async def irregular_income_buffer(source_id: str, target_months: int = 3):
    """Calculate buffer needed for irregular income"""
    tracker = get_employment_tracker()
    
    buffer = tracker.calculate_irregular_income_buffer(source_id, target_months)
    
    if not buffer:
        raise HTTPException(404, "Source not found or not irregular income")
    
    return {
        "source_id": source_id,
        "target_months": buffer.target_months,
        "monthly_expenses": float(buffer.monthly_expenses),
        "current_buffer": float(buffer.current_buffer),
        "target_buffer": float(buffer.monthly_expenses * target_months),
        "progress_percent": round(buffer.buffer_progress_percent, 1),
        "monthly_contribution_needed": float(buffer.monthly_contribution_needed),
        "months_until_fully_funded": buffer.months_until_fully_funded,
        "status": "fully_funded" if buffer.buffer_progress_percent >= 100 else "building" if buffer.buffer_progress_percent > 50 else "critical"
    }
