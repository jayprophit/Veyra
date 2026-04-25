"""Tax Sinking Fund Calculator"""
from typing import Dict
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class SinkingFund:
    """Monthly tax reserve fund"""
    monthly_income: Decimal
    tax_rate: Decimal = Decimal("0.20")  # 20% base
    ni_rate: Decimal = Decimal("0.09")   # 9% NI
    
    def calculate_monthly_reserve(self) -> Dict:
        """Calculate monthly tax reserve"""
        tax = self.monthly_income * self.tax_rate
        ni = self.monthly_income * self.ni_rate
        total = tax + ni
        
        return {
            "gross_income": float(self.monthly_income),
            "income_tax": float(tax),
            "national_insurance": float(ni),
            "total_reserve": float(total),
            "safe_reserve": float(total * Decimal("1.1"))  # 10% buffer
        }
    
    def annual_projection(self) -> Dict:
        """Annual tax projection"""
        monthly = self.calculate_monthly_reserve()
        annual_tax = monthly["total_reserve"] * 12
        
        return {
            "annual_gross": float(self.monthly_income * 12),
            "annual_tax_estimate": annual_tax,
            "payments_on_account": annual_tax / 2,  # 2 installments
            "january_payment": annual_tax / 2,
            "july_payment": annual_tax / 2,
            "buffer_recommended": annual_tax * 0.1
        }

class TaxSinkingFundManager:
    """Manage monthly tax reserves"""
    
    def __init__(self):
        self.funds: Dict[str, SinkingFund] = {}
        self.auto_transfer = True
    
    def setup_fund(self, name: str, monthly_income: float) -> SinkingFund:
        """Setup new sinking fund"""
        fund = SinkingFund(
            monthly_income=Decimal(str(monthly_income))
        )
        self.funds[name] = fund
        return fund
    
    def get_all_reserves(self) -> Dict[str, float]:
        """Get total reserves across all funds"""
        total = 0
        for fund in self.funds.values():
            total += fund.calculate_monthly_reserve()["safe_reserve"]
        return {
            "monthly_total": total,
            "annual_total": total * 12,
            "num_funds": len(self.funds)
        }
