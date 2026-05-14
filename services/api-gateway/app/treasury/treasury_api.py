"""
Treasury Management API Routes
FastAPI endpoints for treasury operations
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from .treasury_manager import TreasuryManager

router = APIRouter(prefix="/treasury", tags=["Treasury Management"])

# Initialize treasury
treasury = TreasuryManager()


class RevenueRequest(BaseModel):
    amount: float
    currency: str
    source: str
    description: str = ""
    reference_id: Optional[str] = None


class ExpenseRequest(BaseModel):
    amount: float
    currency: str
    category: str
    description: str = ""
    budget_id: Optional[str] = None


class AssetRequest(BaseModel):
    asset_type: str
    symbol: str
    name: str
    quantity: float
    purchase_price: float
    current_price: float
    storage: str = ""


class BudgetRequest(BaseModel):
    category: str
    name: str
    amount: float
    period_months: int = 1


@router.post("/revenue")
async def record_revenue(request: RevenueRequest):
    """Record revenue transaction"""
    tx = treasury.record_revenue(
        amount=request.amount,
        currency=request.currency,
        source=request.source,
        description=request.description,
        reference_id=request.reference_id
    )
    return tx.to_dict()


@router.post("/expense")
async def record_expense(request: ExpenseRequest):
    """Record expense transaction"""
    tx = treasury.record_expense(
        amount=request.amount,
        currency=request.currency,
        category=request.category,
        description=request.description,
        budget_id=request.budget_id
    )
    return tx.to_dict()


@router.post("/assets")
async def add_asset(request: AssetRequest):
    """Add treasury asset"""
    asset = treasury.add_asset(
        asset_type=request.asset_type,
        symbol=request.symbol,
        name=request.name,
        quantity=request.quantity,
        purchase_price=request.purchase_price,
        current_price=request.current_price,
        storage=request.storage
    )
    return asset.to_dict()


@router.put("/assets/{asset_id}/price")
async def update_asset_price(asset_id: str, current_price: float):
    """Update asset price"""
    treasury.update_asset_price(asset_id, current_price)
    return {'success': True}


@router.get("/assets")
async def list_assets():
    """List all treasury assets"""
    return {'assets': [a.to_dict() for a in treasury.assets.values()]}


@router.post("/budgets")
async def create_budget(request: BudgetRequest):
    """Create budget allocation"""
    budget = treasury.create_budget(
        category=request.category,
        name=request.name,
        amount=request.amount,
        period_months=request.period_months
    )
    return budget.to_dict()


@router.get("/budgets")
async def list_budgets():
    """List all budgets"""
    return {'budgets': [b.to_dict() for b in treasury.budgets.values()]}


@router.get("/budgets/{budget_id}/vs-actual")
async def get_budget_vs_actual(budget_id: str):
    """Compare budget vs actual spending"""
    result = treasury.get_budget_vs_actual(budget_id)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    return result


@router.get("/reports/balance-sheet")
async def get_balance_sheet():
    """Generate balance sheet"""
    return treasury.get_balance_sheet()


@router.get("/reports/income-statement")
async def get_income_statement(days: int = 30):
    """Generate income statement"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return treasury.get_income_statement(start_date, end_date)


@router.get("/reports/cash-flow")
async def get_cash_flow(days: int = 30):
    """Generate cash flow statement"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return treasury.get_cash_flow(start_date, end_date)


@router.get("/reports/revenue")
async def get_revenue_report(days: int = 30):
    """Get revenue report"""
    return treasury.get_revenue_report(days)


@router.get("/reports/forecast")
async def get_cash_flow_forecast(days: int = 90):
    """Get cash flow forecast"""
    forecast = treasury.forecast_cash_flow(days)
    return {
        'period': forecast.period,
        'start_date': forecast.start_date.isoformat(),
        'end_date': forecast.end_date.isoformat(),
        'projected_revenue': forecast.projected_revenue,
        'projected_expenses': forecast.projected_expenses,
        'net_cash_flow': forecast.net_cash_flow,
        'opening_balance': forecast.opening_balance,
        'closing_balance': forecast.closing_balance
    }


@router.get("/dashboard")
async def get_treasury_dashboard():
    """Get treasury dashboard summary"""
    return treasury.get_dashboard()


@router.get("/transactions")
async def list_transactions(limit: int = 100):
    """List recent transactions"""
    txs = sorted(
        [tx.to_dict() for tx in treasury.transactions.values()],
        key=lambda x: x['timestamps']['created'],
        reverse=True
    )[:limit]
    return {'transactions': txs}
