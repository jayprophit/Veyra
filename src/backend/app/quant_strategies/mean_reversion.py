"""Mean Reversion Strategy - Bollinger Bands, RSI, statistical"""
from typing import Dict, List
from dataclasses import dataclass
import statistics

@dataclass
class ReversionSignal:
    symbol: str
    signal_type: str  # OVERSOLD or OVERBOUGHT
    strength: float
    entry_price: float
    target_price: float
    stop_price: float
    confidence: str

class MeanReversionStrategy:
    """Identify mean reversion opportunities"""
    
    def __init__(self):
        self.lookback = 20
        self.std_threshold = 2.0  # Bollinger threshold
        self.rsi_oversold = 30
        self.rsi_overbought = 70
    
    def calculate_bollinger_bands(self, prices: List[float]) -> Dict:
        """Calculate Bollinger Bands"""
        if len(prices) < self.lookback:
            return {"error": "Insufficient data"}
        
        recent = prices[-self.lookback:]
        sma = statistics.mean(recent)
        std = statistics.stdev(recent) if len(recent) > 1 else 0
        
        upper = sma + (self.std_threshold * std)
        lower = sma - (self.std_threshold * std)
        
        current = prices[-1]
        position = (current - lower) / (upper - lower) if upper != lower else 0.5
        
        return {
            "sma": round(sma, 2),
            "upper_band": round(upper, 2),
            "lower_band": round(lower, 2),
            "current_price": current,
            "percent_b": round(position * 100, 1),  # % position within bands
            "bandwidth": round((upper - lower) / sma * 100, 1) if sma > 0 else 0
        }
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50
        
        # Calculate gains and losses
        gains = []
        losses = []
        
        for i in range(1, min(period + 1, len(prices))):
            change = prices[-i] - prices[-i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if not gains or not losses:
            return 50
        
        avg_gain = statistics.mean(gains)
        avg_loss = statistics.mean(losses)
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signal(self, symbol: str, prices: List[float],
                       volume: List[float] = None) -> ReversionSignal:
        """Generate mean reversion signal"""
        if len(prices) < self.lookback:
            return None
        
        bb = self.calculate_bollinger_bands(prices)
        rsi = self.calculate_rsi(prices)
        
        current = prices[-1]
        
        # Oversold conditions
        oversold_bb = bb["percent_b"] < 5  # Near lower band
        oversold_rsi = rsi < self.rsi_oversold
        
        # Overbought conditions
        overbought_bb = bb["percent_b"] > 95  # Near upper band
        overbought_rsi = rsi > self.rsi_overbought
        
        # Generate signal
        if oversold_bb and oversold_rsi:
            # Strong oversold signal
            target = bb["sma"]  # Revert to mean
            stop = current * 0.95  # 5% stop
            
            return ReversionSignal(
                symbol=symbol,
                signal_type="OVERSOLD",
                strength=min(100, (self.rsi_oversold - rsi) * 2 + (5 - bb["percent_b"]) * 2),
                entry_price=current,
                target_price=round(target, 2),
                stop_price=round(stop, 2),
                confidence="HIGH" if rsi < 20 else "MEDIUM"
            )
        
        elif overbought_bb and overbought_rsi:
            # Strong overbought signal (short)
            target = bb["sma"]
            stop = current * 1.05  # 5% stop on short
            
            return ReversionSignal(
                symbol=symbol,
                signal_type="OVERBOUGHT",
                strength=min(100, (rsi - self.rsi_overbought) * 2 + (bb["percent_b"] - 95) * 2),
                entry_price=current,
                target_price=round(target, 2),
                stop_price=round(stop, 2),
                confidence="HIGH" if rsi > 80 else "MEDIUM"
            )
        
        return None
    
    def scan_universe(self, universe_data: Dict[str, List[float]]) -> List[ReversionSignal]:
        """Scan universe for mean reversion opportunities"""
        signals = []
        
        for symbol, prices in universe_data.items():
            signal = self.generate_signal(symbol, prices)
            if signal and signal.strength > 50:
                signals.append(signal)
        
        return sorted(signals, key=lambda x: x.strength, reverse=True)
    
    def get_position_sizing(self, signal: ReversionSignal, 
                           portfolio_value: float) -> Dict:
        """Calculate position size for mean reversion trade"""
        # Risk-based sizing
        risk_per_trade = portfolio_value * 0.01  # 1% risk
        
        # Calculate risk per share
        if signal.signal_type == "OVERSOLD":
            risk_per_share = signal.entry_price - signal.stop_price
        else:
            risk_per_share = signal.stop_price - signal.entry_price
        
        if risk_per_share <= 0:
            risk_per_share = signal.entry_price * 0.02  # Default 2%
        
        shares = int(risk_per_trade / risk_per_share)
        position_value = shares * signal.entry_price
        
        return {
            "symbol": signal.symbol,
            "side": "LONG" if signal.signal_type == "OVERSOLD" else "SHORT",
            "shares": shares,
            "position_value": position_value,
            "risk_amount": risk_per_trade,
            "target_return_pct": round(
                (signal.target_price - signal.entry_price) / signal.entry_price * 100, 1
            ) if signal.signal_type == "OVERSOLD" else round(
                (signal.entry_price - signal.target_price) / signal.entry_price * 100, 1
            ),
            "risk_reward_ratio": round(
                abs(signal.target_price - signal.entry_price) / abs(signal.stop_price - signal.entry_price), 1
            ) if signal.stop_price != signal.entry_price else 0
        }
