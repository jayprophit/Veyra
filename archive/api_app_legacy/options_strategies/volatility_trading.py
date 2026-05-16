"""Volatility Trading - Vol-specific strategies"""
from typing import Dict

class VolatilityTrading:
    """Trade volatility through options"""
    
    def straddle_pnl(self, underlying_move: float,
                    implied_vol: float,
                    days_to_expiry: int,
                    straddle_cost: float) -> Dict:
        """Calculate straddle P&L based on move and vol"""
        # Expected move based on vol
        expected_move = implied_vol * (days_to_expiry / 365) ** 0.5
        
        # Profit if move exceeds cost
        gross_profit = max(0, abs(underlying_move) - straddle_cost)
        
        return {
            "straddle_cost": straddle_cost,
            "underlying_move_pct": underlying_move,
            "expected_move_pct": round(expected_move, 2),
            "gross_profit": round(gross_profit, 2),
            "profitable": abs(underlying_move) > straddle_cost,
            "edge_ratio": round(abs(underlying_move) / expected_move, 2) if expected_move > 0 else 0
        }
    
    def variance_swap(self, realized_vol: float,
                     strike_vol: float,
                     vega_notional: float) -> Dict:
        """Variance swap payoff - vol vs vol"""
        # Payoff = vega_notional * (realized^2 - strike^2)
        payoff = vega_notional * (realized_vol**2 - strike_vol**2) / (2 * strike_vol)
        
        return {
            "strike_vol": strike_vol,
            "realized_vol": realized_vol,
            "vega_notional": vega_notional,
            "payoff": round(payoff, 0),
            "direction": "long_vol" if payoff > 0 else "short_vol",
            "use_case": "pure_volatility_exposure"
        }
    
    def vol_arbitrage(self, iv_rank: int,
                     iv_percentile: int,
                     hv_20: float,
                     hv_50: float) -> Dict:
        """Volatility arbitrage signals"""
        # High IV rank = expensive options
        signal = "sell_vol" if iv_rank > 80 else "buy_vol" if iv_rank < 20 else "neutral"
        
        # HV trend
        hv_trend = "rising" if hv_20 > hv_50 else "falling"
        
        return {
            "iv_rank": iv_rank,
            "iv_percentile": iv_percentile,
            "hv_20": hv_20,
            "hv_50": hv_50,
            "signal": signal,
            "hv_trend": hv_trend,
            "edge": "iv_hv_spread_trading"
        }
    
    def vega_hedge_ratio(self, portfolio_vega: float,
                         underlying_beta: float,
                         vix_level: float) -> Dict:
        """Calculate vega hedging requirements"""
        # VIX futures contract = $1000 per point
        contracts_needed = portfolio_vega / 1000
        beta_adjusted = contracts_needed * underlying_beta
        
        return {
            "portfolio_vega": portfolio_vega,
            "vix_level": vix_level,
            "contracts_needed": round(contracts_needed, 1),
            "beta_adjusted": round(beta_adjusted, 1),
            "hedge_cost_pct": round(vix_level * 0.01, 2),
            "hedge_instrument": "vix_futures"
        }
