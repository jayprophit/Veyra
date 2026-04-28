"""Settlement Analytics"""
from typing import Dict

class SettlementAnalytics:
    """Analyze settlement decisions"""
    
    def settlement_vs_trial(self, settlement_offer: float, 
                         trial_expected: float,
                         trial_cost: float) -> Dict:
        """Compare settlement to trial"""
        trial_net = trial_expected - trial_cost
        
        return {
            "settlement_offer": settlement_offer,
            "trial_expected_net": trial_net,
            "recommendation": "SETTLE" if settlement_offer > trial_net * 0.9 else "TRIAL",
            "certainty_equivalent": settlement_offer / trial_expected if trial_expected > 0 else 0
        }
