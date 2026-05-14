"""Capital Adequacy - Stress testing and capital planning"""
from typing import Dict

class CapitalAdequacy:
    """Assess capital adequacy under stress"""
    
    def stress_test(self, baseline_cet1: float, rwa: float, 
                   scenarios: Dict[str, float]) -> Dict:
        """Run stress tests on capital ratios"""
        results = {}
        for scenario, rwa_shock in scenarios.items():
            stressed_rwa = rwa * (1 + rwa_shock)
            stressed_cet1 = baseline_cet1 * 0.95  # Capital impairment
            ratio = stressed_cet1 / stressed_rwa * 100
            results[scenario] = {
                "stressed_cet1_ratio": round(ratio, 2),
                "pass": ratio >= 4.5
            }
        return results
    
    def capital_planning(self, target_ratio: float, current_rwa: float,
                        projected_growth: float) -> Dict:
        """Plan capital requirements"""
        future_rwa = current_rwa * (1 + projected_growth)
        required_cet1 = future_rwa * target_ratio
        return {
            "future_rwa": future_rwa,
            "required_cet1": required_cet1,
            "capital_gap": max(0, required_cet1 - current_rwa * 0.07)
        }
