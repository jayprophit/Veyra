"""Exotic Options - Non-standard options structures"""
from typing import Dict

class ExoticOptions:
    """Price and analyze exotic option structures"""
    
    def barrier_option(self, spot: float,
                      strike: float,
                      barrier: float,
                      barrier_type: str,  # 'knock_in', 'knock_out'
                      option_type: str,  # 'call', 'put'
                      rebate: float = 0) -> Dict:
        """Barrier option with trigger levels"""
        vanilla_premium = max(spot - strike, 0) if option_type == "call" else max(strike - spot, 0)
        
        # Barrier adjustment
        if barrier_type == "knock_out":
            probability = 0.7 if abs(spot - barrier) / spot < 0.1 else 0.9
            adjusted = vanilla_premium * probability
        else:  # knock_in
            probability = 0.3 if abs(spot - barrier) / spot < 0.1 else 0.1
            adjusted = vanilla_premium * probability
        
        return {
            "barrier_type": barrier_type,
            "barrier_level": barrier,
            "vanilla_premium": round(vanilla_premium, 2),
            "exotic_premium": round(adjusted, 2),
            "rebate": rebate,
            "use_case": "cheaper_hedge_with_trigger_risk"
        }
    
    def asian_option(self, avg_spot: float,
                    strike: float,
                    averaging_periods: int,
                    option_type: str = "call") -> Dict:
        """Asian option - payoff on average price"""
        payoff = max(avg_spot - strike, 0) if option_type == "call" else max(strike - avg_spot, 0)
        volatility_reduction = 1 / (averaging_periods ** 0.5)
        adjusted_payoff = payoff * (0.8 + 0.2 * volatility_reduction)
        
        return {
            "averaging_periods": averaging_periods,
            "avg_spot": avg_spot,
            "strike": strike,
            "vanilla_payoff": round(payoff, 2),
            "asian_adjusted": round(adjusted_payoff, 2),
            "volatility_reduction": round(volatility_reduction, 2),
            "use_case": "reduce_volatility_exposure"
        }
    
    def binary_option(self, spot: float,
                     strike: float,
                     payout: float,
                     option_type: str = "call") -> Dict:
        """Binary/digital option - all or nothing payoff"""
        # Probability approximation
        distance = abs(spot - strike) / spot
        if option_type == "call":
            prob_itm = 0.5 - distance if spot < strike else 0.5 + min(0.4, 1 - distance)
        else:
            prob_itm = 0.5 + distance if spot < strike else 0.5 - min(0.4, 1 - distance)
        
        fair_value = payout * max(0.1, prob_itm)
        
        return {
            "payout": payout,
            "probability_itm": round(max(0.1, prob_itm), 2),
            "fair_value": round(fair_value, 2),
            "risk": "all_or_nothing",
            "use_case": "event_betting_or_hedging"
        }
    
    def lookback_option(self, spot_history: list,
                       strike_type: str,  # 'fixed', 'floating'
                       option_type: str = "call") -> Dict:
        """Lookback option - best price in hindsight"""
        min_price = min(spot_history)
        max_price = max(spot_history)
        current = spot_history[-1]
        
        if strike_type == "floating":
            payoff = max_price - current if option_type == "call" else current - min_price
        else:
            payoff = max(0, max_price - current) if option_type == "put" else max(0, current - min_price)
        
        return {
            "min_observed": min_price,
            "max_observed": max_price,
            "payoff": round(payoff, 2),
            "strike_type": strike_type,
            "premium_uplift": "50-100%_above_vanilla",
            "use_case": "capture_extreme_moves"
        }
