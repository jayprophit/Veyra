"""Direct Lending - Private credit portfolio analysis"""
from typing import Dict

class DirectLending:
    """Analyze direct lending investments"""
    
    def loan_yield(self, interest_rate: float, origination_fee: float, servicing_fee: float) -> Dict:
        gross = interest_rate + origination_fee
        net = gross - servicing_fee
        return {"gross_yield": interest_rate, "origination": origination_fee, "servicing": servicing_fee, "net_yield": round(net, 2)}
    
    def portfolio_metrics(self, total_loans: int, avg_loan_size: float, default_rate: float, recovery_rate: float) -> Dict:
        total_exposure = total_loans * avg_loan_size
        expected_loss = total_exposure * (default_rate/100) * (1 - recovery_rate/100)
        return {"total_exposure": total_exposure, "expected_loss": round(expected_loss, 0), "risk_adjusted_return": round(default_rate * (1 - recovery_rate/100), 2)}
