"""Stress Tester - Portfolio stress testing"""
from typing import Dict

class StressTester:
    """Stress test portfolios under various scenarios"""
    
    SCENARIOS = {
        "market_crash_2008": {"equity": -0.50, "credit": -0.30, "volatility": 4.0},
        "covid_crash": {"equity": -0.35, "credit": -0.20, "volatility": 3.0},
        "rate_shock": {"rates": 0.03, "equity": -0.15, "bonds": -0.10},
        "inflation_spike": {"equity": -0.20, "bonds": -0.25, "commodities": 0.30},
        "liquidity_crisis": {"credit": -0.40, "equity": -0.25, "bid_ask_spread": 3.0}
    }
    
    def run_scenario(self, portfolio_value: float,
                    equity_pct: float,
                    bond_pct: float,
                    credit_pct: float,
                    scenario: str) -> Dict:
        """Run stress scenario on portfolio"""
        params = self.SCENARIOS.get(scenario, self.SCENARIOS["market_crash_2008"])
        
        equity_impact = equity_pct * params.get("equity", 0)
        credit_impact = credit_pct * params.get("credit", 0)
        bond_impact = bond_pct * params.get("bonds", -0.10)  # Default bond impact
        
        total_impact = equity_impact + credit_impact + bond_impact
        portfolio_loss = portfolio_value * total_impact
        
        return {
            "scenario": scenario,
            "portfolio_impact_pct": round(total_impact * 100, 1),
            "estimated_loss": round(portfolio_loss, 0),
            "recovery_time_months": int(abs(total_impact) * 24),  # Rough estimate
            "severity": "extreme" if total_impact < -0.30 else "severe" if total_impact < -0.20 else "moderate"
        }
    
    def reverse_stress_test(self, max_acceptable_loss: float,
                           portfolio_value: float) -> Dict:
        """Find scenarios that would cause unacceptable loss"""
        max_decline = max_acceptable_loss / portfolio_value if portfolio_value > 0 else 0
        
        dangerous = []
        for scenario, params in self.SCENARIOS.items():
            total_impact = params.get("equity", 0) * 0.6 + params.get("credit", 0) * 0.2 + params.get("bonds", -0.10) * 0.2
            if abs(total_impact) > max_decline:
                dangerous.append(scenario)
        
        return {
            "max_acceptable_decline": round(max_decline * 100, 1),
            "dangerous_scenarios": dangerous,
            "hedge_recommended": len(dangerous) > 2
        }
    
    def correlation_breakdown(self, normal_corr: float,
                             stress_corr: float,
                             assets: int) -> Dict:
        """Analyze correlation breakdown in stress"""
        corr_increase = stress_corr - normal_corr
        diversification_loss = corr_increase * (assets - 1) / assets if assets > 0 else 0
        
        return {
            "normal_correlation": normal_corr,
            "stress_correlation": stress_corr,
            "correlation_spike": round(corr_increase, 2),
            "diversification_effectiveness": round((1 - diversification_loss) * 100, 1),
            "warning": corr_increase > 0.3
        }
