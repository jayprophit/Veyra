"""International Tax"""
from typing import Dict

class InternationalTax:
    def foreign_tax_credit(self, foreign_income: float, foreign_tax_paid: float) -> Dict:
        us_tax = foreign_income * 0.24
        credit = min(foreign_tax_paid, us_tax)
        return {"credit_allowed": credit, "excess": foreign_tax_paid - credit}
    
    def expat_benefits(self, income: float, days_abroad: int) -> Dict:
        qualifies = days_abroad >= 330
        exclusion = min(income, 126500) if qualifies else 0
        return {"qualifies": qualifies, "exclusion": exclusion, "tax_saved": exclusion * 0.24}
    
    def g7_comparison(self, income: float) -> Dict:
        rates = {"us": 0.37, "uk": 0.45, "germany": 0.45, "france": 0.45, "canada": 0.33, "italy": 0.43, "japan": 0.45}
        return {k: round(income * v, 0) for k, v in rates.items()}
