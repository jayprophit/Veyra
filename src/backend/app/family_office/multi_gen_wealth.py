"""Multi-Generational Wealth"""
from typing import Dict

class MultiGenWealth:
    def generation_wealth(self, current_wealth: float, generations: int, growth_rate: float) -> Dict:
        future_wealth = current_wealth * ((1 + growth_rate) ** generations)
        return {"current": current_wealth, "future": round(future_wealth, 0), "generations": generations}
    
    def family_bank(self, loans_outstanding: float, interest_rate: float) -> Dict:
        annual_interest = loans_outstanding * interest_rate
        return {"portfolio": loans_outstanding, "annual_income": annual_interest, "rate": interest_rate}
    
    def dynasty_trust(self, seed_capital: float, years: int) -> Dict:
        # No estate tax, only generation-skipping
        growth = seed_capital * (1.06 ** years)
        return {"seed": seed_capital, "value": round(growth, 0), "years": years}
