"""
Debt Management API Endpoints
Personal debt tracking, payoff planning, and progress monitoring
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from decimal import Decimal

from ..personal.debt_manager import get_debt_manager, DebtType, PayoffStrategy

router = APIRouter(prefix="/debt", tags=["Debt Management"])


class AddDebtRequest(BaseModel):
    name: str
    creditor: str
    debt_type: str
    original_balance: Decimal = Field(..., gt=0)
    current_balance: Decimal = Field(..., gt=0)
    interest_rate_annual: Decimal = Field(..., ge=0)
    min_monthly_payment: Decimal = Field(..., gt=0)
    custom_monthly_payment: Optional[Decimal] = None


class RecordPaymentRequest(BaseModel):
    debt_id: str
    amount: Decimal = Field(..., gt=0)


class SetBudgetRequest(BaseModel):
    monthly_budget: Decimal = Field(..., gt=0)
    extra_to_debt: bool = True


@router.post("/add")
async def add_debt(req: AddDebtRequest):
    """Add a new debt to track"""
    manager = get_debt_manager()
    
    try:
        debt_type = DebtType(req.debt_type.lower())
    except ValueError:
        raise HTTPException(400, f"Invalid debt type. Options: {[t.value for t in DebtType]}")
    
    debt = manager.add_debt(
        name=req.name,
        creditor=req.creditor,
        debt_type=debt_type,
        original_balance=req.original_balance,
        current_balance=req.current_balance,
        interest_rate_annual=req.interest_rate_annual,
        min_monthly_payment=req.min_monthly_payment,
        custom_payment=req.custom_monthly_payment
    )
    
    return {
        "debt_id": debt.id,
        "name": debt.name,
        "creditor": debt.creditor,
        "current_balance": float(debt.current_balance),
        "monthly_payment": float(debt.monthly_payment),
        "interest_per_month": float(debt.interest_per_month)
    }


@router.get("/list")
async def list_debts():
    """List all tracked debts"""
    manager = get_debt_manager()
    
    return {
        "debts": [
            {
                "id": d.id,
                "name": d.name,
                "creditor": d.creditor,
                "type": d.debt_type.value,
                "original_balance": float(d.original_balance),
                "current_balance": float(d.current_balance),
                "interest_rate": float(d.interest_rate_annual),
                "min_payment": float(d.min_monthly_payment),
                "monthly_payment": float(d.monthly_payment),
                "interest_cost_month": float(d.interest_per_month),
                "is_cleared": d.is_cleared,
                "cleared_date": d.cleared_date.isoformat() if d.cleared_date else None
            }
            for d in manager.debts.values()
        ]
    }


@router.get("/summary")
async def debt_summary():
    """Get debt summary statistics"""
    manager = get_debt_manager()
    return manager.get_debt_summary()


@router.post("/payment")
async def record_payment(req: RecordPaymentRequest):
    """Record a payment toward a debt"""
    manager = get_debt_manager()
    
    payment = manager.record_payment(req.debt_id, req.amount)
    if not payment:
        raise HTTPException(404, "Debt not found")
    
    return {
        "payment_recorded": True,
        "debt_id": payment.debt_id,
        "amount": float(payment.amount),
        "principal_paid": float(payment.principal_paid),
        "interest_paid": float(payment.interest_paid),
        "new_balance": float(payment.new_balance)
    }


@router.get("/payoff-plan/{strategy}")
async def payoff_plan(strategy: str, extra_payment: Decimal = Decimal("0")):
    """Get payoff plan for strategy (snowball or avalanche)"""
    manager = get_debt_manager()
    
    if strategy == "snowball":
        plan = manager.calculate_snowball_plan(extra_payment)
    elif strategy == "avalanche":
        plan = manager.calculate_avalanche_plan(extra_payment)
    else:
        raise HTTPException(400, "Strategy must be 'snowball' or 'avalanche'")
    
    return {
        "strategy": plan.strategy.value,
        "total_monthly_payment": float(plan.total_monthly_payment),
        "months_to_debt_free": plan.months_to_debt_free,
        "total_interest_paid": float(plan.total_interest_paid),
        "completion_date": plan.completion_date.isoformat(),
        "payoff_order": [
            {
                "position": i + 1,
                "debt_id": did,
                "name": manager.debts[did].name if did in manager.debts else "Unknown"
            }
            for i, did in enumerate(plan.debts_order)
        ]
    }


@router.get("/compare-strategies")
async def compare_strategies(extra_payment: Decimal = Decimal("0")):
    """Compare snowball vs avalanche strategies"""
    manager = get_debt_manager()
    return manager.compare_strategies(extra_payment)


@router.post("/set-budget")
async def set_budget(req: SetBudgetRequest):
    """Set monthly debt payment budget"""
    manager = get_debt_manager()
    manager.set_monthly_budget(req.monthly_budget, req.extra_to_debt)
    
    return {
        "monthly_budget": float(req.monthly_budget),
        "extra_payment": float(manager.extra_payment_amount),
        "min_required": float(sum(d.min_monthly_payment for d in manager.debts.values() if not d.is_cleared))
    }


@router.get("/progress")
async def payment_progress(months: int = 12):
    """Get payment progress over time"""
    manager = get_debt_manager()
    return {"progress": manager.get_payment_progress(months)}


@router.delete("/{debt_id}")
async def delete_debt(debt_id: str):
    """Remove a debt from tracking"""
    manager = get_debt_manager()
    
    if debt_id not in manager.debts:
        raise HTTPException(404, "Debt not found")
    
    debt = manager.debts.pop(debt_id)
    return {"deleted": True, "name": debt.name}
