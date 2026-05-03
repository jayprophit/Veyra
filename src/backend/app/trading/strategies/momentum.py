"""
Momentum Trading Strategy
Trend-following with multiple indicators
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio

@dataclass
class MomentumSignal:
    symbol: str
    signal: str  # 'buy', 'sell', 'hold'
    confidence: float
    indicators: Dict[str, float]
    timestamp: datetime

class MomentumStrategy:
    """
    Momentum trading using RSI, MACD, and moving averages
    """
    
    def __init__(self, 
                 rsi_period: int = 14,
                 rsi_overbought: float = 70,
                 rsi_oversold: float = 30,
                 macd_fast: int = 12,
                 macd_slow: int = 26,
                 macd_signal: int = 9):
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        
        self.active = False
        self.signals: List[MomentumSignal] = []
        self.trade_history: List[Dict] = []
    
    def calculate_rsi(self, prices: List[float]) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < self.rsi_period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, self.rsi_period + 1):
            change = prices[-i] - prices[-(i+1)]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: List[float]) -> Dict[str, float]:
        """Calculate MACD indicator"""
        def ema(prices_list, period):
            multiplier = 2 / (period + 1)
            ema_values = [sum(prices_list[:period]) / period]
            for price in prices_list[period:]:
                ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
            return ema_values[-1] if ema_values else prices_list[-1]
        
        ema_fast = ema(prices, self.macd_fast)
        ema_slow = ema(prices, self.macd_slow)
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        macd_history = [macd_line]  # Simplified
        signal_line = ema(macd_history, self.macd_signal)
        histogram = macd_line - signal_line
        
        return {
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram
        }
    
    def calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices)
        return sum(prices[-period:]) / period
    
    def generate_signal(self, symbol: str, price_history: List[float]) -> MomentumSignal:
        """Generate trading signal based on momentum indicators"""
        if len(price_history) < 50:
            return MomentumSignal(
                symbol=symbol,
                signal='hold',
                confidence=0.0,
                indicators={'error': 'Insufficient data'},
                timestamp=datetime.now()
            )
        
        # Calculate indicators
        rsi = self.calculate_rsi(price_history)
        macd = self.calculate_macd(price_history)
        sma_20 = self.calculate_sma(price_history, 20)
        sma_50 = self.calculate_sma(price_history, 50)
        
        current_price = price_history[-1]
        
        # Signal logic
        buy_signals = 0
        sell_signals = 0
        
        # RSI signals
        if rsi < self.rsi_oversold:
            buy_signals += 1
        elif rsi > self.rsi_overbought:
            sell_signals += 1
        
        # MACD signals
        if macd['histogram'] > 0 and macd['macd_line'] > macd['signal_line']:
            buy_signals += 1
        elif macd['histogram'] < 0 and macd['macd_line'] < macd['signal_line']:
            sell_signals += 1
        
        # Moving average signals
        if current_price > sma_20 > sma_50:
            buy_signals += 1
        elif current_price < sma_20 < sma_50:
            sell_signals += 1
        
        # Golden cross / Death cross
        if sma_20 > sma_50 and price_history[-2] < price_history[-1]:
            buy_signals += 0.5
        elif sma_20 < sma_50:
            sell_signals += 0.5
        
        # Determine signal
        if buy_signals >= 2:
            signal = 'buy'
            confidence = min(buy_signals / 3.5, 1.0)
        elif sell_signals >= 2:
            signal = 'sell'
            confidence = min(sell_signals / 3.5, 1.0)
        else:
            signal = 'hold'
            confidence = 0.3
        
        return MomentumSignal(
            symbol=symbol,
            signal=signal,
            confidence=round(confidence, 2),
            indicators={
                'rsi': round(rsi, 2),
                'macd_line': round(macd['macd_line'], 4),
                'signal_line': round(macd['signal_line'], 4),
                'histogram': round(macd['histogram'], 4),
                'sma_20': round(sma_20, 2),
                'sma_50': round(sma_50, 2)
            },
            timestamp=datetime.now()
        )
    
    async def scan_symbols(self, symbols: List[str], data_provider) -> List[MomentumSignal]:
        """Scan multiple symbols for momentum signals"""
        signals = []
        
        for symbol in symbols:
            try:
                # Get price history
                price_history = await data_provider.get_price_history(symbol, days=60)
                
                if price_history and len(price_history) >= 50:
                    signal = self.generate_signal(symbol, price_history)
                    signals.append(signal)
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
        
        self.signals = signals
        return signals
    
    async def run_momentum_scanner(self, symbols: List[str], data_provider, check_interval: int = 300):
        """Continuously scan for momentum opportunities"""
        self.active = True
        
        while self.active:
            try:
                signals = await self.scan_symbols(symbols, data_provider)
                
                # Report high-confidence signals
                for signal in signals:
                    if signal.confidence > 0.7 and signal.signal != 'hold':
                        print(f"Strong momentum signal: {signal.symbol} - {signal.signal} ({signal.confidence})")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                print(f"Momentum scanner error: {e}")
                await asyncio.sleep(check_interval)
    
    def stop(self):
        """Stop momentum scanner"""
        self.active = False
    
    def get_active_signals(self) -> List[MomentumSignal]:
        """Get current momentum signals"""
        return [s for s in self.signals if s.confidence > 0.6]
