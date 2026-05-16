"""Bank Stress Tester - Comprehensive stress testing"""
from typing import Dict

class BankStressTester:
    """Comprehensive bank stress testing"""
    
    SCENARIOS = {
        "baseline": {"gdp_growth": 0.02, "unemployment": 0.05, "housing_drop": 0.0},
        "adverse": {"gdp_growth": -0.01, "unemployment": 0.08, "housing_drop": -0.15},
        "severely_adverse": {"gdp_growth": -0.05, "unemployment": 0.12, "housing_drop": -0.30}
    }
    
    def run_ccar(self, bank_assets: float, capital: float) -> Dict:
        """Run CCAR-style stress test"""
        results = {}
        for scenario, params in self.SCENARIOS.items():
            # Calculate losses
            credit_loss = bank_assets * 0.02 * (1 + abs(params["gdp_growth"]) * 5)
            trading_loss = bank_assets * 0.01 * abs(params["housing_drop"])
            total_loss = credit_loss + trading_loss
            
            post_stress_capital = capital - total_loss
            results[scenario] = {
                "total_losses": total_loss,
                "post_stress_capital": post_stress_capital,
                "capital_depletion_pct": round(total_loss / capital * 100, 1),
                "viable": post_stress_capital > bank_assets * 0.04
            }
        return results
