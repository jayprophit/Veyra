"""Options Pricer - Black-Scholes and advanced options pricing"""
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum
import math

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

@dataclass
class OptionContract:
    underlying_price: float
    strike_price: float
    time_to_expiry: float  # in years
    volatility: float  # annualized
    risk_free_rate: float  # annualized
    option_type: OptionType
    dividend_yield: float = 0.0

class OptionsPricer:
    """Price options using Black-Scholes model"""
    
    def __init__(self):
        pass
    
    def _cumulative_normal_distribution(self, x: float) -> float:
        """Approximation of cumulative normal distribution"""
        # Abramowitz and Stegun approximation
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911
        
        sign = 1 if x >= 0 else -1
        x = abs(x) / math.sqrt(2.0)
        
        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
        
        return 0.5 * (1.0 + sign * y)
    
    def calculate_d1_d2(self, contract: OptionContract) -> tuple:
        """Calculate d1 and d2 parameters"""
        S = contract.underlying_price
        K = contract.strike_price
        T = contract.time_to_expiry
        r = contract.risk_free_rate
        sigma = contract.volatility
        q = contract.dividend_yield
        
        if T <= 0 or sigma <= 0:
            return 0, 0
        
        d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        return d1, d2
    
    def price_option(self, contract: OptionContract) -> Dict:
        """Calculate option price using Black-Scholes"""
        S = contract.underlying_price
        K = contract.strike_price
        T = contract.time_to_expiry
        r = contract.risk_free_rate
        q = contract.dividend_yield
        
        if T <= 0:
            # At expiry
            if contract.option_type == OptionType.CALL:
                price = max(0, S - K)
            else:
                price = max(0, K - S)
            
            return {
                "option_price": round(price, 2),
                "intrinsic_value": round(price, 2),
                "time_value": 0,
                "is_expired": True
            }
        
        d1, d2 = self.calculate_d1_d2(contract)
        
        Nd1 = self._cumulative_normal_distribution(d1)
        Nd2 = self._cumulative_normal_distribution(d2)
        N_neg_d1 = self._cumulative_normal_distribution(-d1)
        N_neg_d2 = self._cumulative_normal_distribution(-d2)
        
        if contract.option_type == OptionType.CALL:
            price = S * math.exp(-q * T) * Nd1 - K * math.exp(-r * T) * Nd2
            intrinsic = max(0, S - K)
        else:
            price = K * math.exp(-r * T) * N_neg_d2 - S * math.exp(-q * T) * N_neg_d1
            intrinsic = max(0, K - S)
        
        time_value = price - intrinsic
        
        return {
            "option_price": round(price, 2),
            "intrinsic_value": round(intrinsic, 2),
            "time_value": round(time_value, 2),
            "d1": round(d1, 4),
            "d2": round(d2, 4),
            "moneyness": round((S / K - 1) * 100, 1),
            "is_expired": False
        }
    
    def calculate_greeks(self, contract: OptionContract) -> Dict:
        """Calculate option Greeks"""
        S = contract.underlying_price
        K = contract.strike_price
        T = contract.time_to_expiry
        r = contract.risk_free_rate
        sigma = contract.volatility
        q = contract.dividend_yield
        
        if T <= 0:
            return {"error": "Option expired"}
        
        d1, d2 = self.calculate_d1_d2(contract)
        
        Nd1 = self._cumulative_normal_distribution(d1)
        Nd2 = self._cumulative_normal_distribution(d2)
        N_neg_d1 = self._cumulative_normal_distribution(-d1)
        N_neg_d2 = self._cumulative_normal_distribution(-d2)
        
        # Probability density function at d1
        n_d1 = math.exp(-d1 ** 2 / 2) / math.sqrt(2 * math.pi)
        
        sqrt_t = math.sqrt(T)
        
        if contract.option_type == OptionType.CALL:
            delta = math.exp(-q * T) * Nd1
            theta = (-S * n_d1 * sigma * math.exp(-q * T) / (2 * sqrt_t) 
                    - r * K * math.exp(-r * T) * Nd2 + q * S * math.exp(-q * T) * Nd1)
        else:
            delta = -math.exp(-q * T) * N_neg_d1
            theta = (-S * n_d1 * sigma * math.exp(-q * T) / (2 * sqrt_t) 
                    + r * K * math.exp(-r * T) * N_neg_d2 - q * S * math.exp(-q * T) * N_neg_d1)
        
        # Gamma (same for calls and puts)
        gamma = n_d1 * math.exp(-q * T) / (S * sigma * sqrt_t)
        
        # Vega (same for calls and puts) - per 1% change in volatility
        vega = S * sqrt_t * n_d1 * math.exp(-q * T) * 0.01
        
        # Rho - per 1% change in rates
        if contract.option_type == OptionType.CALL:
            rho = K * T * math.exp(-r * T) * Nd2 * 0.01
        else:
            rho = -K * T * math.exp(-r * T) * N_neg_d2 * 0.01
        
        return {
            "delta": round(delta, 4),
            "gamma": round(gamma, 4),
            "theta": round(theta, 4),  # Daily theta
            "vega": round(vega, 4),    # Per 1% vol change
            "rho": round(rho, 4),      # Per 1% rate change
            "interpretation": {
                "delta": f"For $1 move in underlying, option moves ${delta:.2f}",
                "theta": f"Option loses ${abs(theta):.2f} per day (time decay)",
                "vega": f"For 1% vol increase, option gains ${vega:.2f}"
            }
        }
    
    def implied_volatility(self, contract: OptionContract, 
                          market_price: float, 
                          precision: float = 0.0001) -> Dict:
        """Calculate implied volatility using bisection method"""
        low, high = 0.001, 5.0  # 0.1% to 500%
        
        for _ in range(100):  # Max iterations
            mid = (low + high) / 2
            test_contract = OptionContract(
                contract.underlying_price,
                contract.strike_price,
                contract.time_to_expiry,
                mid,
                contract.risk_free_rate,
                contract.option_type,
                contract.dividend_yield
            )
            
            price = self.price_option(test_contract)["option_price"]
            
            if abs(price - market_price) < precision:
                return {
                    "implied_volatility": round(mid * 100, 2),
                    "converged": True,
                    "iterations": _
                }
            
            if price < market_price:
                low = mid
            else:
                high = mid
        
        return {
            "implied_volatility": round(mid * 100, 2),
            "converged": False,
            "error": "Failed to converge"
        }
    
    def analyze_strategy(self, contracts: list, 
                        quantities: list) -> Dict:
        """Analyze multi-leg options strategy"""
        total_price = 0
        total_delta = 0
        total_gamma = 0
        total_theta = 0
        total_vega = 0
        
        for contract, qty in zip(contracts, quantities):
            price_data = self.price_option(contract)
            greeks = self.calculate_greeks(contract)
            
            total_price += price_data["option_price"] * qty
            total_delta += greeks["delta"] * qty
            total_gamma += greeks["gamma"] * qty
            total_theta += greeks["theta"] * qty
            total_vega += greeks["vega"] * qty
        
        # Strategy classification
        legs = len(contracts)
        strategy_type = "UNKNOWN"
        if legs == 1:
            strategy_type = "SINGLE_LEG"
        elif legs == 2:
            if quantities[0] > 0 and quantities[1] > 0:
                strategy_type = "SPREAD"
            elif quantities[0] * quantities[1] < 0:
                strategy_type = "SPREAD"
            else:
                strategy_type = "STRADDLE/STRANGLE"
        elif legs == 4:
            strategy_type = "IRON_CONDOR/BUTTERFLY"
        
        return {
            "strategy_type": strategy_type,
            "net_debit_credit": round(total_price, 2),
            "total_greeks": {
                "delta": round(total_delta, 4),
                "gamma": round(total_gamma, 4),
                "theta": round(total_theta, 4),
                "vega": round(total_vega, 4)
            },
            "risk_characteristics": {
                "directional_exposure": "BULLISH" if total_delta > 0 else "BEARISH" if total_delta < 0 else "NEUTRAL",
                "volatility_exposure": "LONG_VOL" if total_vega > 0 else "SHORT_VOL",
                "time_decay": "POSITIVE" if total_theta > 0 else "NEGATIVE"
            }
        }
