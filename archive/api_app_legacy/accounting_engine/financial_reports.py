"""
Financial Reports Generation
P&L, Balance Sheet, Cash Flow statements
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .chart_of_accounts import AccountType, get_chart_of_accounts
from .double_entry import get_double_entry_system, JournalEntry, EntryType

@dataclass
class ReportPeriod:
    start_date: date
    end_date: date
    name: str

@dataclass
class PnLReport:
    period: ReportPeriod
    revenue: Dict[str, float]
    expenses: Dict[str, float]
    gross_profit: float
    net_income: float
    
class FinancialReports:
    """Generates financial statements"""
    
    def __init__(self):
        self.chart_of_accounts = get_chart_of_accounts()
        self.double_entry = get_double_entry_system()
    
    def generate_pnl(
        self,
        start_date: date,
        end_date: date,
        compare_to_previous: bool = True
    ) -> Dict:
        """Generate Profit & Loss statement"""
        
        # Get revenue accounts
        revenue_accounts = self.chart_of_accounts.get_accounts_by_type(AccountType.REVENUE)
        expense_accounts = self.chart_of_accounts.get_accounts_by_type(AccountType.EXPENSE)
        
        # Calculate revenue
        revenue = {}
        total_revenue = 0.0
        for account in revenue_accounts:
            balance = self.double_entry.get_account_balance(account.code)
            if balance != 0:
                revenue[account.name] = abs(balance)
                total_revenue += abs(balance)
        
        # Calculate expenses
        expenses = {}
        total_expenses = 0.0
        for account in expense_accounts:
            balance = self.double_entry.get_account_balance(account.code)
            if balance != 0:
                expenses[account.name] = abs(balance)
                total_expenses += abs(balance)
        
        gross_profit = total_revenue - total_expenses
        
        # Calculate ratios
        ratios = {}
        if total_revenue > 0:
            ratios["gross_margin"] = round((gross_profit / total_revenue) * 100, 2)
            ratios["expense_ratio"] = round((total_expenses / total_revenue) * 100, 2)
        
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "revenue": {
                "breakdown": revenue,
                "total": round(total_revenue, 2)
            },
            "expenses": {
                "breakdown": expenses,
                "total": round(total_expenses, 2)
            },
            "gross_profit": round(gross_profit, 2),
            "net_income": round(gross_profit, 2),
            "ratios": ratios
        }
        
        # Add comparison if requested
        if compare_to_previous:
            prev_start = start_date - timedelta(days=(end_date - start_date).days)
            prev_end = start_date - timedelta(days=1)
            prev_report = self.generate_pnl(prev_start, prev_end, compare_to_previous=False)
            
            report["comparison"] = {
                "previous_period": prev_report["period"],
                "revenue_change_pct": self._calc_change_pct(total_revenue, prev_report["revenue"]["total"]),
                "expense_change_pct": self._calc_change_pct(total_expenses, prev_report["expenses"]["total"]),
                "net_income_change_pct": self._calc_change_pct(gross_profit, prev_report["net_income"])
            }
        
        return report
    
    def generate_balance_sheet(self, as_of_date: date) -> Dict:
        """Generate Balance Sheet"""
        
        # Get account balances
        assets = self._get_account_balances_by_type(AccountType.ASSET)
        liabilities = self._get_account_balances_by_type(AccountType.LIABILITY)
        equity = self._get_account_balances_by_type(AccountType.EQUITY)
        
        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())
        total_equity = sum(equity.values())
        
        # Verify accounting equation: Assets = Liabilities + Equity
        imbalance = total_assets - (total_liabilities + total_equity)
        
        return {
            "as_of_date": as_of_date.isoformat(),
            "assets": {
                "breakdown": {k: round(v, 2) for k, v in assets.items()},
                "total": round(total_assets, 2)
            },
            "liabilities": {
                "breakdown": {k: round(v, 2) for k, v in liabilities.items()},
                "total": round(total_liabilities, 2)
            },
            "equity": {
                "breakdown": {k: round(v, 2) for k, v in equity.items()},
                "total": round(total_equity, 2)
            },
            "net_worth": round(total_assets - total_liabilities, 2),
            "accounting_equation_check": {
                "left_side": round(total_assets, 2),
                "right_side": round(total_liabilities + total_equity, 2),
                "imbalance": round(imbalance, 2),
                "is_balanced": abs(imbalance) < 0.01
            }
        }
    
    def generate_cash_flow(
        self,
        start_date: date,
        end_date: date
    ) -> Dict:
        """Generate Cash Flow Statement"""
        
        # Simplified cash flow calculation
        # In practice, would analyze journal entries for cash account
        
        cash_account = self.chart_of_accounts.get_account("1000")  # Cash
        if cash_account:
            ending_balance = self.double_entry.get_account_balance("1000")
        else:
            ending_balance = 0.0
        
        # Categorize entries (simplified)
        operating = ending_balance * 0.6  # Estimate
        investing = ending_balance * 0.2 * -1  # Estimate (negative for outflow)
        financing = ending_balance * 0.2  # Estimate
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "operating_activities": round(operating, 2),
            "investing_activities": round(investing, 2),
            "financing_activities": round(financing, 2),
            "net_change": round(operating + investing + financing, 2),
            "ending_cash_balance": round(ending_balance, 2),
            "free_cash_flow": round(operating + investing, 2)
        }
    
    def generate_trial_balance(self, as_of_date: date) -> Dict:
        """Generate Trial Balance"""
        
        trial_balance = self.double_entry.get_trial_balance()
        
        total_debits = sum(item["debit"] for item in trial_balance.values())
        total_credits = sum(item["credit"] for item in trial_balance.values())
        
        return {
            "as_of_date": as_of_date.isoformat(),
            "accounts": trial_balance,
            "totals": {
                "debits": round(total_debits, 2),
                "credits": round(total_credits, 2)
            },
            "is_balanced": abs(total_debits - total_credits) < 0.01,
            "difference": round(abs(total_debits - total_credits), 2)
        }
    
    def _get_account_balances_by_type(self, account_type: AccountType) -> Dict[str, float]:
        """Get balances for all accounts of a type"""
        accounts = self.chart_of_accounts.get_accounts_by_type(account_type)
        balances = {}
        for account in accounts:
            balance = self.double_entry.get_account_balance(account.code)
            if balance != 0:
                balances[account.name] = balance
        return balances
    
    def _calc_change_pct(self, current: float, previous: float) -> Optional[float]:
        """Calculate percentage change"""
        if previous == 0:
            return None if current == 0 else float('inf')
        return round(((current - previous) / abs(previous)) * 100, 2)
    
    def export_to_excel(self, report_type: str, start_date: date, end_date: date) -> bytes:
        """Export report to Excel format"""
        # Would use openpyxl or pandas
        # Returns Excel file bytes
        pass
    
    def export_to_pdf(self, report_type: str, start_date: date, end_date: date) -> bytes:
        """Export report to PDF format"""
        # Would use reportlab or weasyprint
        # Returns PDF file bytes
        pass

# Singleton
_financial_reports: Optional[FinancialReports] = None

def get_financial_reports() -> FinancialReports:
    global _financial_reports
    if _financial_reports is None:
        _financial_reports = FinancialReports()
    return _financial_reports
