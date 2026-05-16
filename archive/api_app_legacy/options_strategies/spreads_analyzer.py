"""Spreads Analyzer - Multi-leg options strategies"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class OptionLeg:
    strike: float
    expiry: str
    option_type: str  # 'call' or 'put'
    position: str  # 'long' or 'short'
    premium: float
    quantity: int = 1

class SpreadsAnalyzer:
    """Analyze multi-leg options strategies"""
    
    def bull_call_spread(self, lower_strike: float,
                        higher_strike: float,
                        lower_premium: float,
                        higher_premium: float,
                        quantity: int = 1) -> Dict:
        """Bull call spread - limited risk/reward bullish strategy"""
        max_profit = (higher_strike - lower_strike - (lower_premium - higher_premium)) * quantity
        max_loss = (lower_premium - higher_premium) * quantity
        breakeven = lower_strike + (lower_premium - higher_premium)
        
        return {
            "strategy": "bull_call_spread",
            "net_debit": (lower_premium - higher_premium) * quantity,
            "max_profit": round(max_profit, 2),
            "max_loss": round(max_loss, 2),
            "breakeven": round(breakeven, 2),
            "risk_reward_ratio": round(abs(max_profit / max_loss), 2) if max_loss != 0 else 0,
            "breakeven_profit": 0,
            "sentiment": "moderately_bullish"
        }
    
    def iron_condor(self, lower_put: float,
                   higher_put: float,
                   lower_call: float,
                   higher_call: float,
                   put_credit: float,
                   call_credit: float,
                   quantity: int = 1) -> Dict:
        """Iron condor - neutral strategy for range-bound markets"""
        net_credit = (put_credit + call_credit) * quantity
        width_puts = higher_put - lower_put
        width_calls = higher_call - lower_call
        max_risk = min(width_puts, width_calls) - net_credit/quantity
        
        return {
            "strategy": "iron_condor",
            "net_credit": round(net_credit, 2),
            "max_profit": round(net_credit, 2),
            "max_risk": round(max_risk * quantity, 2),
            "put_breakeven": higher_put - put_credit,
            "call_breakeven": lower_call + call_credit,
            "profit_zone": f"{higher_put - put_credit} to {lower_call + call_credit}",
            "pop_estimate": "60-70%"  # Probability of profit
        }
    
    def butterfly_spread(self, center_strike: float,
                        wing_width: float,
                        center_premium: float,
                        wing_premium: float,
                        quantity: int = 1) -> Dict:
        """Butterfly spread - low volatility bet"""
        lower_strike = center_strike - wing_width
        higher_strike = center_strike + wing_width
        
        cost = (2 * center_premium - 2 * wing_premium) * quantity
        max_profit = wing_width * quantity - cost
        max_loss = cost
        
        return {
            "strategy": "butterfly",
            "wings": f"{lower_strike} / {center_strike} / {higher_strike}",
            "cost": round(cost, 2),
            "max_profit": round(max_profit, 2),
            "max_loss": round(max_loss, 2),
            "breakevens": [lower_strike + cost/(2*quantity), higher_strike - cost/(2*quantity)],
            "target": center_strike,
            "ideal_scenario": "low_volatility_at_expiration"
        }
    
    def calendar_spread(self, near_premium: float,
                       far_premium: float,
                       near_dte: int,
                       far_dte: int,
                       implied_vol_change: float = 0) -> Dict:
        """Calendar spread - time decay differential play"""
        net_debit = (far_premium - near_premium)
        
        # Time decay theta capture
        theta_near = near_premium * 0.02  # Approx 2% daily decay
        theta_far = far_premium * 0.01
        theta_capture = (theta_near - theta_far) * (far_dte - near_dte)
        
        return {
            "strategy": "calendar_spread",
            "net_debit": round(net_debit, 2),
            "near_dte": near_dte,
            "far_dte": far_dte,
            "theta_capture": round(theta_capture, 2),
            "ideal_for": "low_volatility_sideways_market",
            "max_risk": round(net_debit, 2),
            "vega_exposure": "positive"  # Benefits from vol expansion
        }
    
    def collar_strategy(self, stock_price: float,
                       put_strike: float,
                       call_strike: float,
                       put_cost: float,
                       call_credit: float,
                       shares: int = 100) -> Dict:
        """Collar - protect gains while limiting upside"""
        net_cost = (put_cost - call_credit) * shares
        protected_value = put_strike * shares
        capped_value = call_strike * shares
        current_value = stock_price * shares
        
        return {
            "strategy": "collar",
            "net_cost": round(net_cost, 2),
            "downside_protection": f"{round((1 - put_strike/stock_price)*100, 1)}%",
            "upside_cap": f"{round((call_strike/stock_price - 1)*100, 1)}%",
            "protected_value": round(protected_value, 0),
            "max_value": round(capped_value, 0),
            "use_case": "protect_gains_limit_upside",
            "cost_basis_impact": round(net_cost / shares, 2)
        }
