"""
Treasury Management System for Veyra
Handles platform revenue, expenses, investments, and financial operations

Features:
- Revenue tracking and distribution
- Expense management
- Investment portfolio
- Cash flow forecasting
- Financial reporting
- Multi-sig wallet support
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Treasury transaction types"""
    REVENUE = "revenue"
    EXPENSE = "expense"
    INVESTMENT = "investment"
    TRANSFER = "transfer"
    RESERVE = "reserve"
    DISTRIBUTION = "distribution"


class RevenueSource(Enum):
    """Revenue sources"""
    TRADING_FEES = "trading_fees"
    SUBSCRIPTION = "subscription"
    MARKETPLACE = "marketplace"
    COPY_TRADING = "copy_trading"
    STRATEGY_SALES = "strategy_sales"
    STAKING_FEES = "staking_fees"
    WITHDRAWAL_FEES = "withdrawal_fees"
    PREMIUM_FEATURES = "premium_features"
    API_ACCESS = "api_access"


class ExpenseCategory(Enum):
    """Expense categories"""
    SALARIES = "salaries"
    INFRASTRUCTURE = "infrastructure"
    MARKETING = "marketing"
    DEVELOPMENT = "development"
    LEGAL = "legal"
    AUDIT = "audit"
    INSURANCE = "insurance"
    RESEARCH = "research"
    GRANTS = "grants"
    OPERATIONS = "operations"


class AssetType(Enum):
    """Treasury asset types"""
    STABLECOIN = "stablecoin"
    CRYPTO = "crypto"
    FIAT = "fiat"
    EQUITY = "equity"
    BOND = "bond"
    COMMODITY = "commodity"
    OTHER = "other"


@dataclass
class TreasuryTransaction:
    """Treasury transaction record"""
    id: str
    transaction_type: TransactionType
    amount: float
    currency: str
    
    # Source/Destination
    source: Optional[str] = None  # RevenueSource for revenue
    destination: Optional[str] = None  # ExpenseCategory for expenses
    
    # Details
    description: str = ""
    reference_id: Optional[str] = None  # Link to user transaction
    wallet_address: Optional[str] = None
    
    # Status
    status: str = "completed"  # pending, completed, failed, reversed
    
    # Metadata
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    created_by: str = ""
    approved_by: Optional[str] = None  # For multi-sig
    
    # Blockchain
    tx_hash: Optional[str] = None
    block_number: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.transaction_type.value,
            'amount': self.amount,
            'currency': self.currency,
            'source': self.source,
            'destination': self.destination,
            'description': self.description,
            'status': self.status,
            'timestamps': {
                'created': self.created_at.isoformat() if self.created_at else None,
                'completed': self.completed_at.isoformat() if self.completed_at else None
            },
            'blockchain': {
                'tx_hash': self.tx_hash,
                'block_number': self.block_number
            } if self.tx_hash else None
        }


@dataclass
class TreasuryAsset:
    """Treasury asset holding"""
    id: str
    asset_type: AssetType
    symbol: str
    name: str
    
    # Holdings
    quantity: float
    avg_purchase_price: float
    current_price: float
    current_value: float = 0.0
    
    # Details
    purchase_date: Optional[datetime] = None
    purchase_tx_id: Optional[str] = None
    storage_location: str = ""  # wallet, exchange, bank, etc.
    
    # Performance
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    
    def __post_init__(self):
        self.current_value = self.quantity * self.current_price
        if self.avg_purchase_price > 0:
            self.unrealized_pnl = (self.current_price - self.avg_purchase_price) * self.quantity
            self.unrealized_pnl_pct = ((self.current_price / self.avg_purchase_price) - 1) * 100
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'asset_type': self.asset_type.value,
            'symbol': self.symbol,
            'name': self.name,
            'holdings': {
                'quantity': self.quantity,
                'avg_price': self.avg_purchase_price,
                'current_price': self.current_price,
                'current_value': self.current_value
            },
            'performance': {
                'unrealized_pnl': self.unrealized_pnl,
                'unrealized_pnl_pct': self.unrealized_pnl_pct
            },
            'storage': self.storage_location
        }


@dataclass
class BudgetItem:
    """Budget allocation item"""
    id: str
    category: ExpenseCategory
    name: str
    
    # Budget amounts
    allocated_amount: float
    spent_amount: float = 0.0
    remaining_amount: float = 0.0
    
    # Period
    period_start: datetime = None
    period_end: datetime = None
    
    # Status
    status: str = "active"
    
    def __post_init__(self):
        if self.period_start is None:
            self.period_start = datetime.now()
        if self.period_end is None:
            self.period_end = self.period_start + timedelta(days=30)
        self.remaining_amount = self.allocated_amount - self.spent_amount
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'category': self.category.value,
            'name': self.name,
            'budget': {
                'allocated': self.allocated_amount,
                'spent': self.spent_amount,
                'remaining': self.remaining_amount,
                'utilization_pct': (self.spent_amount / self.allocated_amount * 100) 
                                  if self.allocated_amount > 0 else 0
            },
            'period': {
                'start': self.period_start.isoformat() if self.period_start else None,
                'end': self.period_end.isoformat() if self.period_end else None
            },
            'status': self.status
        }


@dataclass
class CashFlowForecast:
    """Cash flow forecast"""
    period: str  # daily, weekly, monthly, quarterly, yearly
    start_date: datetime
    end_date: datetime
    
    # Forecast amounts
    projected_revenue: float = 0.0
    projected_expenses: float = 0.0
    net_cash_flow: float = 0.0
    
    # Breakdown
    revenue_breakdown: Dict[str, float] = field(default_factory=dict)
    expense_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Running balance
    opening_balance: float = 0.0
    closing_balance: float = 0.0
    
    def calculate_net_flow(self):
        self.net_cash_flow = self.projected_revenue - self.projected_expenses
        self.closing_balance = self.opening_balance + self.net_cash_flow


class TreasuryManager:
    """
    Treasury Management System
    """
    
    def __init__(self):
        # Transactions
        self.transactions: Dict[str, TreasuryTransaction] = {}
        self.revenue_transactions: List[str] = []
        self.expense_transactions: List[str] = []
        
        # Assets
        self.assets: Dict[str, TreasuryAsset] = {}
        
        # Budgets
        self.budgets: Dict[str, BudgetItem] = {}
        
        # Multi-sig settings
        self.required_signatures = 2
        self.approvers: List[str] = []
        self.pending_approvals: Dict[str, List[str]] = {}  # tx_id -> list of approvers
        
        # Historical data
        self.daily_revenue: Dict[str, float] = {}  # date -> amount
        self.monthly_expenses: Dict[str, float] = {}  # month -> amount
    
    def record_revenue(self, amount: float, currency: str, source: str,
                      description: str = "", reference_id: str = None,
                      metadata: Dict = None) -> TreasuryTransaction:
        """Record revenue transaction"""
        
        tx = TreasuryTransaction(
            id=str(uuid.uuid4()),
            transaction_type=TransactionType.REVENUE,
            amount=amount,
            currency=currency,
            source=source,
            description=description,
            reference_id=reference_id
        )
        
        self.transactions[tx.id] = tx
        self.revenue_transactions.append(tx.id)
        
        # Update daily revenue tracking
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.daily_revenue:
            self.daily_revenue[today] = 0
        self.daily_revenue[today] += amount
        
        logger.info(f"Recorded revenue: {amount} {currency} from {source}")
        return tx
    
    def record_expense(self, amount: float, currency: str, category: str,
                      description: str = "", budget_id: str = None) -> TreasuryTransaction:
        """Record expense transaction"""
        
        tx = TreasuryTransaction(
            id=str(uuid.uuid4()),
            transaction_type=TransactionType.EXPENSE,
            amount=abs(amount),
            currency=currency,
            destination=category,
            description=description
        )
        
        self.transactions[tx.id] = tx
        self.expense_transactions.append(tx.id)
        
        # Update budget if specified
        if budget_id and budget_id in self.budgets:
            budget = self.budgets[budget_id]
            budget.spent_amount += abs(amount)
            budget.remaining_amount = budget.allocated_amount - budget.spent_amount
        
        # Update monthly expense tracking
        month = datetime.now().strftime('%Y-%m')
        if month not in self.monthly_expenses:
            self.monthly_expenses[month] = 0
        self.monthly_expenses[month] += abs(amount)
        
        logger.info(f"Recorded expense: {amount} {currency} for {category}")
        return tx
    
    def add_asset(self, asset_type: str, symbol: str, name: str,
                  quantity: float, purchase_price: float, current_price: float,
                  storage: str = "") -> TreasuryAsset:
        """Add treasury asset"""
        
        asset = TreasuryAsset(
            id=str(uuid.uuid4()),
            asset_type=AssetType(asset_type),
            symbol=symbol,
            name=name,
            quantity=quantity,
            avg_purchase_price=purchase_price,
            current_price=current_price,
            storage_location=storage,
            purchase_date=datetime.now()
        )
        
        self.assets[asset.id] = asset
        
        logger.info(f"Added treasury asset: {symbol} - {quantity} units")
        return asset
    
    def update_asset_price(self, asset_id: str, current_price: float):
        """Update current price of an asset"""
        asset = self.assets.get(asset_id)
        if asset:
            asset.current_price = current_price
            # Recalculate derived values
            asset.current_value = asset.quantity * current_price
            if asset.avg_purchase_price > 0:
                asset.unrealized_pnl = (current_price - asset.avg_purchase_price) * asset.quantity
                asset.unrealized_pnl_pct = ((current_price / asset.avg_purchase_price) - 1) * 100
    
    def create_budget(self, category: str, name: str, amount: float,
                     period_months: int = 1) -> BudgetItem:
        """Create budget allocation"""
        
        budget = BudgetItem(
            id=str(uuid.uuid4()),
            category=ExpenseCategory(category),
            name=name,
            allocated_amount=amount,
            period_start=datetime.now(),
            period_end=datetime.now() + timedelta(days=30*period_months)
        )
        
        self.budgets[budget.id] = budget
        
        logger.info(f"Created budget: {name} - {amount}")
        return budget
    
    def get_balance_sheet(self) -> Dict:
        """Generate balance sheet"""
        # Assets
        assets_by_type = {}
        total_assets = 0.0
        
        for asset in self.assets.values():
            asset_type = asset.asset_type.value
            if asset_type not in assets_by_type:
                assets_by_type[asset_type] = {'value': 0.0, 'items': []}
            
            assets_by_type[asset_type]['value'] += asset.current_value
            assets_by_type[asset_type]['items'].append(asset.to_dict())
            total_assets += asset.current_value
        
        # Calculate total revenue and expenses
        total_revenue = sum(
            self.transactions[tx_id].amount 
            for tx_id in self.revenue_transactions
            if self.transactions[tx_id].status == 'completed'
        )
        
        total_expenses = sum(
            self.transactions[tx_id].amount 
            for tx_id in self.expense_transactions
            if self.transactions[tx_id].status == 'completed'
        )
        
        return {
            'assets': {
                'by_type': assets_by_type,
                'total_value': total_assets
            },
            'liabilities': {
                'total': 0.0,  # No debt in this implementation
                'breakdown': {}
            },
            'equity': {
                'retained_earnings': total_revenue - total_expenses,
                'total': total_revenue - total_expenses
            },
            'totals': {
                'assets': total_assets,
                'liabilities': 0.0,
                'equity': total_revenue - total_expenses
            }
        }
    
    def get_income_statement(self, start_date: datetime = None, 
                             end_date: datetime = None) -> Dict:
        """Generate income statement (P&L)"""
        
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        # Revenue by source
        revenue_by_source = {}
        total_revenue = 0.0
        
        for tx_id in self.revenue_transactions:
            tx = self.transactions[tx_id]
            if start_date <= tx.created_at <= end_date and tx.status == 'completed':
                source = tx.source or 'other'
                if source not in revenue_by_source:
                    revenue_by_source[source] = 0.0
                revenue_by_source[source] += tx.amount
                total_revenue += tx.amount
        
        # Expenses by category
        expenses_by_category = {}
        total_expenses = 0.0
        
        for tx_id in self.expense_transactions:
            tx = self.transactions[tx_id]
            if start_date <= tx.created_at <= end_date and tx.status == 'completed':
                category = tx.destination or 'other'
                if category not in expenses_by_category:
                    expenses_by_category[category] = 0.0
                expenses_by_category[category] += tx.amount
                total_expenses += tx.amount
        
        net_income = total_revenue - total_expenses
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'revenue': {
                'by_source': revenue_by_source,
                'total': total_revenue
            },
            'expenses': {
                'by_category': expenses_by_category,
                'total': total_expenses
            },
            'net_income': net_income,
            'margin_pct': (net_income / total_revenue * 100) if total_revenue > 0 else 0
        }
    
    def get_cash_flow(self, start_date: datetime = None, 
                      end_date: datetime = None) -> Dict:
        """Generate cash flow statement"""
        
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        # Operating activities
        operating_inflows = 0.0
        operating_outflows = 0.0
        
        # Investing activities
        investing_inflows = 0.0
        investing_outflows = 0.0
        
        # Financing activities
        financing_inflows = 0.0
        financing_outflows = 0.0
        
        for tx in self.transactions.values():
            if not (start_date <= tx.created_at <= end_date):
                continue
            
            if tx.transaction_type == TransactionType.REVENUE:
                operating_inflows += tx.amount
            elif tx.transaction_type == TransactionType.EXPENSE:
                operating_outflows += tx.amount
            elif tx.transaction_type == TransactionType.INVESTMENT:
                if tx.amount > 0:
                    investing_inflows += tx.amount
                else:
                    investing_outflows += abs(tx.amount)
            elif tx.transaction_type == TransactionType.DISTRIBUTION:
                financing_outflows += tx.amount
        
        net_operating = operating_inflows - operating_outflows
        net_investing = investing_inflows - investing_outflows
        net_financing = financing_inflows - financing_outflows
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'operating_activities': {
                'inflows': operating_inflows,
                'outflows': operating_outflows,
                'net': net_operating
            },
            'investing_activities': {
                'inflows': investing_inflows,
                'outflows': investing_outflows,
                'net': net_investing
            },
            'financing_activities': {
                'inflows': financing_inflows,
                'outflows': financing_outflows,
                'net': net_financing
            },
            'net_cash_change': net_operating + net_investing + net_financing
        }
    
    def get_revenue_report(self, days: int = 30) -> Dict:
        """Get revenue report for specified period"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        daily_revenue_list = []
        total_revenue = 0.0
        
        for i in range(days):
            date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
            amount = self.daily_revenue.get(date, 0.0)
            daily_revenue_list.append({'date': date, 'amount': amount})
            total_revenue += amount
        
        # Revenue by source
        revenue_by_source = {}
        for tx_id in self.revenue_transactions:
            tx = self.transactions[tx_id]
            if start_date <= tx.created_at <= end_date:
                source = tx.source or 'other'
                if source not in revenue_by_source:
                    revenue_by_source[source] = 0.0
                revenue_by_source[source] += tx.amount
        
        return {
            'period_days': days,
            'total_revenue': total_revenue,
            'daily_average': total_revenue / days if days > 0 else 0,
            'by_source': revenue_by_source,
            'daily_breakdown': daily_revenue_list
        }
    
    def forecast_cash_flow(self, days: int = 90) -> CashFlowForecast:
        """Forecast future cash flow"""
        
        # Calculate average daily revenue
        avg_daily_revenue = sum(self.daily_revenue.values()) / len(self.daily_revenue) \
                          if self.daily_revenue else 1000
        
        # Calculate average daily expenses
        total_monthly_expenses = sum(self.monthly_expenses.values()) / len(self.monthly_expenses) \
                                if self.monthly_expenses else 5000
        avg_daily_expenses = total_monthly_expenses / 30
        
        forecast = CashFlowForecast(
            period=f"{days}d",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=days),
            projected_revenue=avg_daily_revenue * days,
            projected_expenses=avg_daily_expenses * days
        )
        
        # Calculate opening balance (sum of all assets)
        forecast.opening_balance = sum(a.current_value for a in self.assets.values())
        forecast.calculate_net_flow()
        
        return forecast
    
    def get_budget_vs_actual(self, budget_id: str) -> Dict:
        """Compare budget vs actual spending"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return {'error': 'Budget not found'}
        
        # Get actual spending for this category
        actual_spending = 0.0
        for tx_id in self.expense_transactions:
            tx = self.transactions[tx_id]
            if tx.destination == budget.category.value and tx.status == 'completed':
                if budget.period_start <= tx.created_at <= budget.period_end:
                    actual_spending += tx.amount
        
        variance = budget.allocated_amount - actual_spending
        
        return {
            'budget': budget.to_dict(),
            'actual': {
                'spent': actual_spending,
                'remaining': budget.allocated_amount - actual_spending
            },
            'variance': {
                'amount': variance,
                'pct': (variance / budget.allocated_amount * 100) 
                      if budget.allocated_amount > 0 else 0
            },
            'status': 'under_budget' if variance > 0 else 'over_budget'
        }
    
    def get_dashboard(self) -> Dict:
        """Get treasury dashboard summary"""
        
        # Calculate totals
        total_revenue_today = self.daily_revenue.get(datetime.now().strftime('%Y-%m-%d'), 0)
        total_revenue_month = sum(
            v for k, v in self.daily_revenue.items() 
            if k.startswith(datetime.now().strftime('%Y-%m'))
        )
        
        total_assets = sum(a.current_value for a in self.assets.values())
        unrealized_pnl = sum(a.unrealized_pnl for a in self.assets.values())
        
        # Active budgets
        active_budgets = [b.to_dict() for b in self.budgets.values() 
                         if b.status == 'active' and datetime.now() <= b.period_end]
        
        # Recent transactions
        recent_tx = sorted(
            [tx.to_dict() for tx in self.transactions.values()],
            key=lambda x: x['timestamps']['created'],
            reverse=True
        )[:10]
        
        return {
            'overview': {
                'total_assets': total_assets,
                'unrealized_pnl': unrealized_pnl,
                'revenue_today': total_revenue_today,
                'revenue_this_month': total_revenue_month,
                'active_budgets': len(active_budgets)
            },
            'assets_by_type': self._get_assets_by_type(),
            'budgets': active_budgets,
            'recent_transactions': recent_tx,
            'cash_forecast': {
                'next_30_days': self.forecast_cash_flow(30).__dict__,
                'next_90_days': self.forecast_cash_flow(90).__dict__
            }
        }
    
    def _get_assets_by_type(self) -> Dict:
        """Group assets by type"""
        by_type = {}
        for asset in self.assets.values():
            asset_type = asset.asset_type.value
            if asset_type not in by_type:
                by_type[asset_type] = {'count': 0, 'value': 0.0}
            by_type[asset_type]['count'] += 1
            by_type[asset_type]['value'] += asset.current_value
        return by_type
