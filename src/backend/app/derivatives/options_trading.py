"""Options Trading Module - Calls, Puts, and Strategies."""
import logging
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from scipy.stats import norm

logger = logging.getLogger(__name__)

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

class OptionStrategy(Enum):
    LONG_CALL = "long_call"
    LONG_PUT = "long_put"
    COVERED_CALL = "covered_call"
    PROTECTIVE_PUT = "protective_put"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"
    IRON_CONDOR = "iron_condor"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    BUTTERFLY = "butterfly"

@dataclass
class Option:
    symbol: str
    underlying: str
    option_type: OptionType
    strike: float
    expiry: datetime
    premium: float
    quantity: int
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    iv: float = 0.0

@dataclass
class OptionsPosition:
    position_id: str
    user_id: str
    option: Option
    entry_price: float
    entry_date: datetime
    is_open: bool = True
    exit_price: Optional[float] = None
    pnl: float = 0.0

class OptionsPricing:
    """Black-Scholes option pricing model."""
    
    @staticmethod
    def calculate_price(S: float, K: float, T: float, r: float, 
                       sigma: float, option_type: OptionType) -> Dict[str, float]:
        """
        Calculate option price and Greeks using Black-Scholes.
        
        S: Spot price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate
        sigma: Volatility
        """
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == OptionType.CALL:
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            delta = norm.cdf(d1)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            delta = -norm.cdf(-d1)
        
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        if option_type == OptionType.PUT:
            theta -= r * K * np.exp(-r * T) * norm.cdf(-d2)
        else:
            theta += r * K * np.exp(-r * T) * norm.cdf(d2)
        
        vega = S * norm.pdf(d1) * np.sqrt(T)
        
        return {
            'price': price,
            'delta': delta,
            'gamma': gamma,
            'theta': theta / 365,  # Daily theta
            'vega': vega / 100,  # Per 1% IV change
            'iv': sigma
        }
    
    @staticmethod
    def implied_volatility(S: float, K: float, T: float, r: float,
                          market_price: float, option_type: OptionType,
                          precision: float = 0.0001) -> float:
        """Calculate implied volatility using Newton-Raphson."""
        sigma = 0.5  # Initial guess
        max_iter = 100
        
        for _ in range(max_iter):
            price_data = OptionsPricing.calculate_price(S, K, T, r, sigma, option_type)
            price = price_data['price']
            diff = market_price - price
            
            if abs(diff) < precision:
                return sigma
            
            vega = price_data['vega'] * 100
            if vega < 0.0001:
                break
            
            sigma += diff / vega
            sigma = max(0.01, min(sigma, 2.0))  # Keep reasonable bounds
        
        return sigma

class OptionsTrading:
    """Options trading with strategies and risk management."""
    
    def __init__(self):
        self.positions: Dict[str, OptionsPosition] = {}
        self.position_counter = 0
        self.risk_free_rate = 0.02
    
    def _generate_id(self) -> str:
        self.position_counter += 1
        return f"opt_{self.position_counter}_{datetime.now().strftime('%H%M%S')}"
    
    async def buy_option(self, user_id: str, underlying: str,
                        option_type: str, strike: float,
                        expiry_days: int, quantity: int,
                        current_price: float, volatility: float) -> OptionsPosition:
        """Buy an option contract."""
        opt_type = OptionType(option_type)
        expiry = datetime.now() + timedelta(days=expiry_days)
        T = expiry_days / 365
        
        # Calculate fair price
        pricing = OptionsPricing.calculate_price(
            current_price, strike, T, self.risk_free_rate, volatility, opt_type
        )
        
        option = Option(
            symbol=f"{underlying}_{strike}_{option_type}_{expiry.strftime('%y%m%d')}",
            underlying=underlying,
            option_type=opt_type,
            strike=strike,
            expiry=expiry,
            premium=pricing['price'],
            quantity=quantity,
            delta=pricing['delta'],
            gamma=pricing['gamma'],
            theta=pricing['theta'],
            vega=pricing['vega'],
            iv=volatility
        )
        
        position = OptionsPosition(
            position_id=self._generate_id(),
            user_id=user_id,
            option=option,
            entry_price=pricing['price'],
            entry_date=datetime.now()
        )
        
        self.positions[position.position_id] = position
        
        logger.info(f"Option bought: {option.symbol} qty={quantity}")
        return position
    
    async def calculate_strategy_payoff(self, strategy: str,
                                       legs: List[Dict],
                                       price_range: tuple) -> Dict[str, Any]:
        """Calculate payoff diagram for multi-leg strategies."""
        prices = np.linspace(price_range[0], price_range[1], 100)
        payoffs = []
        
        for price in prices:
            total_payoff = 0
            for leg in legs:
                strike = leg['strike']
                premium = leg['premium']
                qty = leg['quantity']
                opt_type = OptionType(leg['type'])
                
                if opt_type == OptionType.CALL:
                    intrinsic = max(0, price - strike)
                else:
                    intrinsic = max(0, strike - price)
                
                if leg.get('action') == 'sell':
                    total_payoff += qty * (premium - intrinsic)
                else:
                    total_payoff += qty * (intrinsic - premium)
            
            payoffs.append(total_payoff)
        
        max_profit = max(payoffs)
        max_loss = min(payoffs)
        breakevens = [prices[i] for i in range(len(payoffs)-1) 
                      if payoffs[i] * payoffs[i+1] < 0]
        
        return {
            'strategy': strategy,
            'price_range': list(prices),
            'payoffs': payoffs,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'breakeven_points': breakevens,
            'legs': len(legs)
        }
    
    async def get_portfolio_greeks(self, user_id: str) -> Dict[str, float]:
        """Calculate aggregate Greeks for user's options portfolio."""
        user_positions = [p for p in self.positions.values() 
                         if p.user_id == user_id and p.is_open]
        
        total_delta = sum(p.option.delta * p.option.quantity for p in user_positions)
        total_gamma = sum(p.option.gamma * p.option.quantity for p in user_positions)
        total_theta = sum(p.option.theta * p.option.quantity for p in user_positions)
        total_vega = sum(p.option.vega * p.option.quantity for p in user_positions)
        
        return {
            'total_delta': total_delta,
            'total_gamma': total_gamma,
            'total_theta': total_theta,  # Daily time decay
            'total_vega': total_vega,
            'position_count': len(user_positions)
        }
    
    async def screen_options(self, underlying: str, 
                          min_volume: int = 100,
                          max_iv: float = 1.0,
                          min_days: int = 7,
                          max_days: int = 90) -> List[Dict]:
        """Screen for attractive option opportunities."""
        # This would query real market data
        # Simulated screening results
        opportunities = []
        
        strikes = [0.9, 0.95, 1.0, 1.05, 1.1]  # % of current price
        
        for strike_pct in strikes:
            for opt_type in ['call', 'put']:
                opportunities.append({
                    'underlying': underlying,
                    'strike_pct': strike_pct,
                    'option_type': opt_type,
                    'expiry_days': 30,
                    'implied_vol': 0.45,
                    'volume': 250,
                    'delta': 0.5 if opt_type == 'call' else -0.5,
                    'suggested_strategy': 'long' if strike_pct == 1.0 else 'spread'
                })
        
        return opportunities

options_trading = OptionsTrading()
