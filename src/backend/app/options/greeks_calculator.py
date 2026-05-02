"""
Options Greeks Calculator
=========================
Calculate option Greeks: Delta, Gamma, Theta, Vega, Rho
Black-Scholes and Binomial models
Implied volatility surface analysis
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Greeks:
    """Option Greeks container"""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    charm: float  # Delta decay
    vanna: float  # Cross greek
    vomma: float  # Vega convexity


class OptionsGreeksCalculator:
    """
    Professional options Greeks calculator
    
    Features:
    - Black-Scholes pricing and Greeks
    - Implied volatility calculation
    - Greeks sensitivity analysis
    - Multi-leg strategy Greeks
    """
    
    def __init__(self, risk_free_rate: float = 0.05):
        self.r = risk_free_rate
    
    def black_scholes(self, S: float, K: float, T: float, 
                     r: float, sigma: float, option_type: str = 'call') -> float:
        """
        Black-Scholes option pricing
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
        """
        if T <= 0:
            if option_type == 'call':
                return max(S - K, 0)
            else:
                return max(K - S, 0)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'call':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        return price
    
    def calculate_greeks(self, S: float, K: float, T: float,
                        r: float, sigma: float, option_type: str = 'call') -> Greeks:
        """Calculate all Greeks"""
        
        if T <= 0:
            return Greeks(0, 0, 0, 0, 0, 0, 0, 0)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Delta
        if option_type == 'call':
            delta = norm.cdf(d1)
        else:
            delta = norm.cdf(d1) - 1
        
        # Gamma
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        
        # Theta (per day)
        if option_type == 'call':
            theta = -(S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))) - \
                    r * K * np.exp(-r * T) * norm.cdf(d2)
        else:
            theta = -(S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))) + \
                    r * K * np.exp(-r * T) * norm.cdf(-d2)
        theta = theta / 365  # Convert to daily
        
        # Vega (per 1% change in volatility)
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        
        # Rho (per 1% change in rates)
        if option_type == 'call':
            rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
        else:
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
        
        # Higher order Greeks
        # Charm (delta decay)
        charm = -norm.pdf(d1) * (2 * r * T - d2 * sigma * np.sqrt(T)) / \
                (2 * T * sigma * np.sqrt(T))
        
        # Vanna
        vanna = -norm.pdf(d1) * d2 / sigma
        
        # Vomma
        vomma = vega * d1 * d2 / sigma
        
        return Greeks(
            delta=round(delta, 4),
            gamma=round(gamma, 4),
            theta=round(theta, 4),
            vega=round(vega, 4),
            rho=round(rho, 4),
            charm=round(charm, 4),
            vanna=round(vanna, 4),
            vomma=round(vomma, 4)
        )
    
    def implied_volatility(self, S: float, K: float, T: float,
                          r: float, market_price: float,
                          option_type: str = 'call') -> float:
        """
        Calculate implied volatility using Brent's method
        """
        def objective(sigma):
            return self.black_scholes(S, K, T, r, sigma, option_type) - market_price
        
        try:
            iv = brentq(objective, 0.001, 5.0)
            return iv
        except ValueError:
            logger.warning(f"IV calculation failed for {option_type} K={K}")
            return 0.0
    
    def calculate_iv_surface(self, S: float, T: float, r: float,
                            strikes: List[float], 
                            market_prices: List[float],
                            option_type: str = 'call') -> Dict[float, float]:
        """Calculate implied volatility surface"""
        iv_surface = {}
        
        for strike, price in zip(strikes, market_prices):
            if price > 0:
                iv = self.implied_volatility(S, strike, T, r, price, option_type)
                if iv > 0:
                    iv_surface[strike] = iv
        
        return iv_surface
    
    def analyze_skew(self, S: float, iv_surface: Dict[float, float]) -> Dict:
        """Analyze volatility skew/smile"""
        if not iv_surface:
            return {}
        
        strikes = sorted(iv_surface.keys())
        at_the_money_strike = min(strikes, key=lambda x: abs(x - S))
        atm_iv = iv_surface[at_the_money_strike]
        
        # Find put skew (lower strikes)
        put_strikes = [k for k in strikes if k < S]
        if put_strikes:
            lowest_put = min(put_strikes)
            put_skew = iv_surface[lowest_put] - atm_iv
        else:
            put_skew = 0
        
        # Find call skew (higher strikes)
        call_strikes = [k for k in strikes if k > S]
        if call_strikes:
            highest_call = max(call_strikes)
            call_skew = iv_surface[highest_call] - atm_iv
        else:
            call_skew = 0
        
        return {
            'atm_iv': round(atm_iv, 4),
            'atm_strike': at_the_money_strike,
            'put_skew': round(put_skew, 4),
            'call_skew': round(call_skew, 4),
            'skew_shape': 'smirk' if put_skew > call_skew else 'reverse_skew' if call_skew > put_skew else 'symmetric'
        }
    
    def multi_leg_greeks(self, legs: List[Dict]) -> Greeks:
        """
        Calculate Greeks for multi-leg strategies
        
        legs: List of {'position': +/- quantity, 'greeks': Greeks object}
        """
        total_delta = sum(leg['position'] * leg['greeks'].delta for leg in legs)
        total_gamma = sum(leg['position'] * leg['greeks'].gamma for leg in legs)
        total_theta = sum(leg['position'] * leg['greeks'].theta for leg in legs)
        total_vega = sum(leg['position'] * leg['greeks'].vega for leg in legs)
        total_rho = sum(leg['position'] * leg['greeks'].rho for leg in legs)
        
        return Greeks(
            delta=round(total_delta, 4),
            gamma=round(total_gamma, 4),
            theta=round(total_theta, 4),
            vega=round(total_vega, 4),
            rho=round(total_rho, 4),
            charm=0, vanna=0, vomma=0  # Not calculated for multi-leg
        )
    
    def strategy_analysis(self, S: float, legs: List[Dict]) -> Dict:
        """
        Analyze options strategy
        
        legs format:
        [
            {'type': 'call', 'strike': 100, 'premium': 5, 'quantity': 1},
            {'type': 'put', 'strike': 95, 'premium': 3, 'quantity': -1}
        ]
        """
        total_premium = sum(leg['premium'] * leg['quantity'] for leg in legs)
        
        # Calculate max profit/loss
        max_profit = float('inf')
        max_loss = -float('inf')
        
        # Breakeven points
        breakevens = []
        
        # For each leg
        for leg in legs:
            strike = leg['strike']
            premium = leg['premium']
            qty = leg['quantity']
            
            if leg['type'] == 'call':
                if qty > 0:  # Long call
                    be = strike + premium
                    breakevens.append(be)
                else:  # Short call
                    be = strike + premium
                    breakevens.append(be)
            else:
                if qty > 0:  # Long put
                    be = strike - premium
                    breakevens.append(be)
                else:  # Short put
                    be = strike - premium
                    breakevens.append(be)
        
        return {
            'net_premium': round(total_premium, 2),
            'max_profit': 'Unlimited' if max_profit == float('inf') else round(max_profit, 2),
            'max_loss': 'Unlimited' if max_loss == -float('inf') else round(max_loss, 2),
            'breakeven_points': [round(b, 2) for b in breakevens],
            'strategy_type': self._classify_strategy(legs)
        }
    
    def _classify_strategy(self, legs: List[Dict]) -> str:
        """Classify options strategy type"""
        num_calls = sum(1 for leg in legs if leg['type'] == 'call')
        num_puts = sum(1 for leg in legs if leg['type'] == 'put')
        
        if num_calls == 1 and num_puts == 0:
            return 'Long Call' if legs[0]['quantity'] > 0 else 'Short Call'
        elif num_calls == 0 and num_puts == 1:
            return 'Long Put' if legs[0]['quantity'] > 0 else 'Short Put'
        elif num_calls == 1 and num_puts == 1:
            return 'Straddle' if legs[0]['strike'] == legs[1]['strike'] else 'Strangle'
        elif num_calls == 2 or num_puts == 2:
            return 'Spread'
        else:
            return 'Complex Multi-Leg'


# Usage
def quick_greeks(S: float, K: float, T_days: int, 
                sigma: float, option_type: str = 'call') -> Dict:
    """Quick Greeks calculation"""
    calc = OptionsGreeksCalculator()
    T = T_days / 365
    
    greeks = calc.calculate_greeks(S, K, T, 0.05, sigma, option_type)
    
    return {
        'delta': greeks.delta,
        'gamma': greeks.gamma,
        'theta_per_day': greeks.theta,
        'vega_per_1pct': greeks.vega,
        'rho_per_1pct': greeks.rho
    }


def calculate_iv(S: float, K: float, T_days: int, 
                market_price: float, option_type: str = 'call') -> float:
    """Quick implied volatility calculation"""
    calc = OptionsGreeksCalculator()
    T = T_days / 365
    
    return calc.implied_volatility(S, K, T, 0.05, market_price, option_type)
