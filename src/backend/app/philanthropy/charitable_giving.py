"""Charitable Giving"""
from typing import Dict

class CharitableGiving:
    def donor_advised_fund(self, contribution: float, grant_rate: float) -> Dict:
        annual_grants = contribution * grant_rate
        tax_savings = contribution * 0.40
        return {"contribution": contribution, "annual_grants": annual_grants, "tax_savings": tax_savings}
    
    def private_foundation(self, endowment: float, payout_required: float) -> Dict:
        required = endowment * 0.05
        actual = endowment * payout_required
        return {"endowment": endowment, "required_distribution": required, "actual": actual, "compliant": actual >= required}
    
    def charitable_laddering(self, high_income_years: int, total_donation: float) -> Dict:
        annual = total_donation / high_income_years
        annual_savings = annual * 0.37  # At max rate
        return {"annual_donation": annual, "years": high_income_years, "annual_savings": annual_savings}
