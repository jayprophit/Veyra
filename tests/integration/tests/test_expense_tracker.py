"""
Unit Tests for Expense Tracker Module
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from src.backend.app.personal.expense_tracker import (
    ExpenseTracker, ExpenseCategory, IncomeCategory, TransactionType, get_expense_tracker
)


class TestExpenseTracker:
    """Test expense tracking functionality"""
    
    @pytest.fixture
    def tracker(self):
        return get_expense_tracker()
    
    def test_add_income_transaction(self, tracker):
        """Test adding income transaction"""
        txn = tracker.add_transaction(
            date=date.today(),
            amount=Decimal("2500"),
            transaction_type=TransactionType.INCOME,
            category=IncomeCategory.SALARY.value,
            description="Monthly salary",
            account="main"
        )
        
        assert txn.id is not None
        assert txn.amount == Decimal("2500")
        assert txn.transaction_type == TransactionType.INCOME
        assert tracker.accounts["main"] == Decimal("2500")
    
    def test_add_expense_transaction(self, tracker):
        """Test adding expense transaction"""
        # First add income
        tracker.add_transaction(
            date=date.today(),
            amount=Decimal("2500"),
            transaction_type=TransactionType.INCOME,
            category=IncomeCategory.SALARY.value,
            description="Salary",
            account="main"
        )
        
        # Then add expense
        txn = tracker.add_transaction(
            date=date.today(),
            amount=Decimal("50"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.FOOD.value,
            description="Groceries",
            merchant="Tesco",
            account="main"
        )
        
        assert txn.merchant == "Tesco"
        assert tracker.accounts["main"] == Decimal("2450")  # 2500 - 50
    
    def test_set_budget(self, tracker):
        """Test setting budget for category"""
        budget = tracker.set_budget(
            category=ExpenseCategory.FOOD.value,
            amount=Decimal("300"),
            period="monthly"
        )
        
        assert budget.category == ExpenseCategory.FOOD.value
        assert budget.amount == Decimal("300")
        assert budget.period == "monthly"
        assert budget.is_essential == True
    
    def test_monthly_summary_calculation(self, tracker):
        """Test monthly summary calculation"""
        today = date.today()
        
        # Add income
        tracker.add_transaction(
            date=today,
            amount=Decimal("2500"),
            transaction_type=TransactionType.INCOME,
            category=IncomeCategory.SALARY.value,
            description="Salary",
            account="main"
        )
        
        # Add expenses
        tracker.add_transaction(
            date=today,
            amount=Decimal("800"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.HOUSING.value,
            description="Rent",
            account="main"
        )
        
        tracker.add_transaction(
            date=today,
            amount=Decimal("200"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.FOOD.value,
            description="Groceries",
            account="main"
        )
        
        summary = tracker.get_monthly_summary(today.year, today.month)
        
        assert summary["income"]["total"] == 2500.0
        assert summary["expenses"]["total"] == 1000.0  # 800 + 200
        assert summary["cash_flow"]["net"] == 1500.0
        assert summary["cash_flow"]["savings_rate"] == 60.0  # 1500/2500
    
    def test_essential_vs_discretionary_breakdown(self, tracker):
        """Test essential vs discretionary breakdown"""
        today = date.today()
        
        # Essential expenses
        tracker.add_transaction(
            date=today,
            amount=Decimal("800"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.HOUSING.value,
            description="Rent"
        )
        
        tracker.add_transaction(
            date=today,
            amount=Decimal("200"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.FOOD.value,
            description="Groceries"
        )
        
        # Discretionary expenses
        tracker.add_transaction(
            date=today,
            amount=Decimal("100"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.DINING_OUT.value,
            description="Restaurant"
        )
        
        tracker.add_transaction(
            date=today,
            amount=Decimal("50"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.ENTERTAINMENT.value,
            description="Cinema"
        )
        
        breakdown = tracker.get_essential_vs_discretionary(today.year, today.month)
        
        assert breakdown["essential"] == 1000.0  # 800 + 200
        assert breakdown["discretionary"] == 150.0  # 100 + 50
    
    def test_budget_vs_actual_analysis(self, tracker):
        """Test budget vs actual analysis"""
        today = date.today()
        
        # Set budget
        tracker.set_budget(
            category=ExpenseCategory.FOOD.value,
            amount=Decimal("200"),
            period="monthly"
        )
        
        # Add income
        tracker.add_transaction(
            date=today,
            amount=Decimal("2500"),
            transaction_type=TransactionType.INCOME,
            category=IncomeCategory.SALARY.value,
            description="Salary"
        )
        
        # Add expense under budget
        tracker.add_transaction(
            date=today,
            amount=Decimal("150"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.FOOD.value,
            description="Groceries"
        )
        
        summary = tracker.get_monthly_summary(today.year, today.month)
        food_budget = [b for b in summary["budget_analysis"] if b["category"] == ExpenseCategory.FOOD.value][0]
        
        assert food_budget["budget"] == 200.0
        assert food_budget["actual"] == 150.0
        assert food_budget["remaining"] == 50.0
        assert food_budget["percent_used"] == 75.0
        assert food_budget["overspent"] == False
    
    def test_detect_unusual_spending(self, tracker):
        """Test unusual spending detection"""
        today = date.today()
        last_month = today - timedelta(days=30)
        
        # Last month spending
        tracker.add_transaction(
            date=last_month,
            amount=Decimal("200"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.FOOD.value,
            description="Last month groceries"
        )
        
        # This month - much higher
        tracker.add_transaction(
            date=today,
            amount=Decimal("400"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.FOOD.value,
            description="This month groceries"
        )
        
        alerts = tracker.detect_unusual_spending(threshold_percent=20.0)
        
        # Should detect 100% increase
        assert len(alerts) >= 1
        food_alert = [a for a in alerts if a["category"] == ExpenseCategory.FOOD.value]
        assert len(food_alert) == 1
        assert food_alert[0]["change_percent"] == 100.0
    
    def test_spending_insights(self, tracker):
        """Test spending insights generation"""
        today = date.today()
        
        # Add multiple transactions
        for i in range(5):
            tracker.add_transaction(
                date=today - timedelta(days=i*2),
                amount=Decimal("40"),
                transaction_type=TransactionType.EXPENSE,
                category=ExpenseCategory.FOOD.value,
                description=f"Shop {i}",
                merchant="Tesco"
            )
        
        tracker.set_budget(
            category=ExpenseCategory.FOOD.value,
            amount=Decimal("200"),
            period="monthly"
        )
        
        insight = tracker.get_spending_insights(ExpenseCategory.FOOD.value, months=1)
        
        assert insight is not None
        assert insight.category == ExpenseCategory.FOOD.value
        assert insight.total_spent == Decimal("200")  # 5 * 40
        assert insight.frequency == 5
        assert insight.average_transaction == Decimal("40")
    
    def test_cash_flow_forecast(self, tracker):
        """Test cash flow forecasting"""
        today = date.today()
        
        # Add recurring income
        for i in range(3):
            tracker.add_transaction(
                date=today - timedelta(days=30*i),
                amount=Decimal("2500"),
                transaction_type=TransactionType.INCOME,
                category=IncomeCategory.SALARY.value,
                description=f"Salary {i}",
                is_recurring=True
            )
            tracker.recurring_transactions.append(tracker.transactions[-1])
        
        forecast = tracker.get_cash_flow_forecast(months=3)
        
        assert len(forecast) == 3
        assert forecast[0]["expected_income"] == 2500.0
        assert forecast[0]["confidence"] in ["high", "medium", "low"]
    
    def test_multiple_accounts(self, tracker):
        """Test tracking multiple accounts"""
        today = date.today()
        
        # Add to different accounts
        tracker.add_transaction(
            date=today,
            amount=Decimal("1000"),
            transaction_type=TransactionType.INCOME,
            category=IncomeCategory.SALARY.value,
            description="Main salary",
            account="main"
        )
        
        tracker.add_transaction(
            date=today,
            amount=Decimal("500"),
            transaction_type=TransactionType.INCOME,
            category=IncomeCategory.FREELANCE.value,
            description="Side income",
            account="side"
        )
        
        assert tracker.accounts["main"] == Decimal("1000")
        assert tracker.accounts["side"] == Decimal("500")
        assert sum(tracker.accounts.values()) == Decimal("1500")
    
    def test_transaction_with_tags(self, tracker):
        """Test transaction with tags"""
        txn = tracker.add_transaction(
            date=date.today(),
            amount=Decimal("100"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.FOOD.value,
            description="Weekly shop",
            tags=["weekly", "essentials", "tesco"]
        )
        
        assert len(txn.tags) == 3
        assert "weekly" in txn.tags
        assert "tesco" in txn.tags
    
    def test_tax_deductible_expense(self, tracker):
        """Test marking expense as tax deductible"""
        txn = tracker.add_transaction(
            date=date.today(),
            amount=Decimal("50"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.BUSINESS_EXPENSES.value,
            description="Work travel",
            is_tax_deductible=True
        )
        
        assert txn.is_tax_deductible == True
    
    def test_refund_transaction(self, tracker):
        """Test refund transaction"""
        today = date.today()
        
        # Original purchase
        tracker.add_transaction(
            date=today,
            amount=Decimal("100"),
            transaction_type=TransactionType.EXPENSE,
            category=ExpenseCategory.SHOPPING.value,
            description="Purchase",
            account="main"
        )
        
        # Refund
        tracker.add_transaction(
            date=today,
            amount=Decimal("100"),
            transaction_type=TransactionType.REFUND,
            category=ExpenseCategory.SHOPPING.value,
            description="Return",
            account="main"
        )
        
        # Account should be back to 0
        assert tracker.accounts["main"] == Decimal("0")


class TestExpenseCategories:
    """Test expense category definitions"""
    
    def test_essential_categories(self):
        """Test essential categories are marked correctly"""
        essential = [
            ExpenseCategory.HOUSING,
            ExpenseCategory.UTILITIES,
            ExpenseCategory.FOOD,
            ExpenseCategory.TRANSPORT,
            ExpenseCategory.INSURANCE,
            ExpenseCategory.HEALTH,
            ExpenseCategory.DEBT_PAYMENTS
        ]
        
        for cat in essential:
            assert cat in ExpenseCategory
    
    def test_discretionary_categories(self):
        """Test discretionary categories"""
        discretionary = [
            ExpenseCategory.DINING_OUT,
            ExpenseCategory.ENTERTAINMENT,
            ExpenseCategory.SHOPPING,
            ExpenseCategory.TRAVEL
        ]
        
        for cat in discretionary:
            assert cat in ExpenseCategory
    
    def test_all_categories_have_values(self):
        """Test all categories have string values"""
        for cat in ExpenseCategory:
            assert isinstance(cat.value, str)
            assert len(cat.value) > 0


class TestIncomeCategories:
    """Test income category definitions"""
    
    def test_salary_income(self):
        """Test salary income category"""
        assert IncomeCategory.SALARY.value == "salary"
    
    def test_self_employment_income(self):
        """Test self-employment category"""
        assert IncomeCategory.SELF_EMPLOYMENT.value == "self_employment"
    
    def test_benefits_income(self):
        """Test benefits category"""
        assert IncomeCategory.BENEFITS.value == "benefits"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
