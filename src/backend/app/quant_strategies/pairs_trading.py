"""Pairs Trading Engine - Statistical arbitrage via cointegration"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import statistics

@dataclass
class PairSignal:
    long_symbol: str
    short_symbol: str
    z_score: float
    signal_strength: str
    entry_price_long: float
    entry_price_short: float
    expected_return: float

class PairsTradingEngine:
    """Find and trade cointegrated pairs"""
    
    def __init__(self):
        self.pairs: List[Tuple[str, str]] = []
        self.z_threshold = 2.0  # Entry threshold
        self.exit_threshold = 0.5  # Exit threshold
        self.lookback = 60  # Days for calculation
    
    def find_cointegrated_pairs(self, price_data: Dict[str, List[float]], 
                                symbols: List[str]) -> List[Dict]:
        """Find cointegrated pairs from price history"""
        cointegrated = []
        
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                if sym1 not in price_data or sym2 not in price_data:
                    continue
                
                prices1 = price_data[sym1][-self.lookback:]
                prices2 = price_data[sym2][-self.lookback:]
                
                if len(prices1) < self.lookback or len(prices2) < self.lookback:
                    continue
                
                # Calculate correlation
                correlation = self._calculate_correlation(prices1, prices2)
                
                # Check spread stationarity (simplified)
                spread_stationary = self._test_spread_stationarity(prices1, prices2)
                
                if correlation > 0.8 and spread_stationary:
                    # Calculate hedge ratio
                    hedge_ratio = self._calculate_hedge_ratio(prices1, prices2)
                    
                    cointegrated.append({
                        "pair": (sym1, sym2),
                        "correlation": round(correlation, 3),
                        "hedge_ratio": round(hedge_ratio, 3),
                        "quality_score": self._pair_quality(correlation, hedge_ratio),
                        "half_life_days": self._estimate_half_life(prices1, prices2)
                    })
        
        return sorted(cointegrated, key=lambda x: x["quality_score"], reverse=True)
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation"""
        n = len(x)
        if n == 0:
            return 0
        
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denom_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
        denom_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5
        
        if denom_x == 0 or denom_y == 0:
            return 0
        
        return numerator / (denom_x * denom_y)
    
    def _test_spread_stationarity(self, prices1: List[float], 
                                  prices2: List[float]) -> bool:
        """Simplified test for spread stationarity"""
        # Calculate spread
        hedge_ratio = self._calculate_hedge_ratio(prices1, prices2)
        spread = [p1 - hedge_ratio * p2 for p1, p2 in zip(prices1, prices2)]
        
        # Check if spread mean reverts (simplified)
        if len(spread) < 10:
            return False
        
        # Mean reversion test: variance should not increase with time
        first_half_var = statistics.variance(spread[:len(spread)//2])
        second_half_var = statistics.variance(spread[len(spread)//2:])
        
        # If second half variance is not significantly larger, likely stationary
        return second_half_var < first_half_var * 2
    
    def _calculate_hedge_ratio(self, prices1: List[float], 
                               prices2: List[float]) -> float:
        """Calculate hedge ratio via OLS regression"""
        # Simplified: use ratio of means
        if statistics.mean(prices2) == 0:
            return 1.0
        return statistics.mean(prices1) / statistics.mean(prices2)
    
    def _pair_quality(self, correlation: float, hedge_ratio: float) -> float:
        """Calculate pair quality score"""
        # Higher correlation = better
        corr_score = correlation * 50
        
        # Hedge ratio near 1 = more balanced
        balance_score = max(0, 50 - abs(hedge_ratio - 1) * 25)
        
        return corr_score + balance_score
    
    def _estimate_half_life(self, prices1: List[float], 
                            prices2: List[float]) -> float:
        """Estimate mean reversion half-life"""
        # Simplified estimation
        hedge_ratio = self._calculate_hedge_ratio(prices1, prices2)
        spread = [p1 - hedge_ratio * p2 for p1, p2 in zip(prices1, prices2)]
        
        if len(spread) < 20:
            return float('inf')
        
        # Calculate how quickly spread reverts
        changes = [spread[i] - spread[i-1] for i in range(1, len(spread))]
        mean_change = statistics.mean(changes)
        
        if mean_change == 0:
            return float('inf')
        
        # Rough half-life estimate
        return abs(statistics.mean(spread) / mean_change)
    
    def generate_signal(self, pair: Tuple[str, str], 
                       price_data: Dict[str, List[float]]) -> Optional[PairSignal]:
        """Generate trading signal for a pair"""
        sym1, sym2 = pair
        
        if sym1 not in price_data or sym2 not in price_data:
            return None
        
        prices1 = price_data[sym1][-self.lookback:]
        prices2 = price_data[sym2][-self.lookback:]
        
        if len(prices1) < self.lookback or len(prices2) < self.lookback:
            return None
        
        # Calculate current z-score
        hedge_ratio = self._calculate_hedge_ratio(prices1, prices2)
        spread = [p1 - hedge_ratio * p2 for p1, p2 in zip(prices1, prices2)]
        
        current_spread = prices1[-1] - hedge_ratio * prices2[-1]
        mean_spread = statistics.mean(spread)
        std_spread = statistics.stdev(spread) if len(spread) > 1 else 1
        
        z_score = (current_spread - mean_spread) / std_spread if std_spread > 0 else 0
        
        # Generate signal
        if abs(z_score) > self.z_threshold:
            if z_score > 0:
                # Spread too high - short spread (short 1, long 2)
                return PairSignal(
                    long_symbol=sym2,
                    short_symbol=sym1,
                    z_score=z_score,
                    signal_strength="STRONG" if z_score > 2.5 else "MODERATE",
                    entry_price_long=prices2[-1],
                    entry_price_short=prices1[-1],
                    expected_return=abs(z_score) * 0.02  # 2% per unit z-score
                )
            else:
                # Spread too low - long spread (long 1, short 2)
                return PairSignal(
                    long_symbol=sym1,
                    short_symbol=sym2,
                    z_score=z_score,
                    signal_strength="STRONG" if z_score < -2.5 else "MODERATE",
                    entry_price_long=prices1[-1],
                    entry_price_short=prices2[-1],
                    expected_return=abs(z_score) * 0.02
                )
        
        return None
    
    def get_position_sizing(self, signal: PairSignal, 
                           portfolio_value: float) -> Dict:
        """Calculate position sizes for pair trade"""
        # Risk per trade
        risk_per_trade = portfolio_value * 0.02  # 2% risk
        
        # Equal dollar allocation
        allocation_per_leg = risk_per_trade / 2
        
        return {
            "long_symbol": signal.long_symbol,
            "long_shares": round(allocation_per_leg / signal.entry_price_long, 0),
            "long_value": allocation_per_leg,
            "short_symbol": signal.short_symbol,
            "short_shares": round(allocation_per_leg / signal.entry_price_short, 0),
            "short_value": allocation_per_leg,
            "total_exposure": allocation_per_leg * 2,
            "market_neutral": True,
            "expected_pnl": signal.expected_return * risk_per_trade
        }
    
    def monitor_positions(self, active_signals: List[PairSignal],
                         current_prices: Dict[str, float]) -> List[Dict]:
        """Monitor active pair positions for exit"""
        updates = []
        
        for signal in active_signals:
            long_price = current_prices.get(signal.long_symbol)
            short_price = current_prices.get(signal.short_symbol)
            
            if not long_price or not short_price:
                continue
            
            # Calculate current P&L
            long_pnl = (long_price - signal.entry_price_long) / signal.entry_price_long
            short_pnl = (signal.entry_price_short - short_price) / signal.entry_price_short
            total_pnl = long_pnl + short_pnl
            
            # Check exit conditions
            current_z = signal.z_score * (1 - total_pnl / signal.expected_return) if signal.expected_return > 0 else 0
            
            exit_signal = False
            exit_reason = ""
            
            if abs(current_z) < self.exit_threshold:
                exit_signal = True
                exit_reason = "Mean reversion complete"
            elif total_pnl < -0.05:  # 5% stop loss
                exit_signal = True
                exit_reason = "Stop loss triggered"
            elif total_pnl > signal.expected_return * 1.5:  # Take profit
                exit_signal = True
                exit_reason = "Profit target reached"
            
            updates.append({
                "pair": (signal.long_symbol, signal.short_symbol),
                "long_pnl_pct": round(long_pnl * 100, 2),
                "short_pnl_pct": round(short_pnl * 100, 2),
                "total_pnl_pct": round(total_pnl * 100, 2),
                "current_z": round(current_z, 2),
                "exit_signal": exit_signal,
                "exit_reason": exit_reason,
                "hold": not exit_signal
            })
        
        return updates
