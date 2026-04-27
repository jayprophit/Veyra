"""Tick Processor - Process real-time market tick data"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import statistics

@dataclass
class Tick:
    symbol: str
    price: float
    size: int
    timestamp: datetime
    exchange: str
    side: str  # BID, ASK, TRADE

@dataclass
class OHLCV:
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime

class TickProcessor:
    """Process real-time tick data and build candles"""
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.tick_buffer: Dict[str, deque] = {s: deque(maxlen=1000) for s in symbols}
        self.ohlcv_history: Dict[str, List[OHLCV]] = {s: [] for s in symbols}
        self.current_candle: Dict[str, Optional[OHLCV]] = {s: None for s in symbols}
        self.last_price: Dict[str, float] = {}
        self.vwap: Dict[str, float] = {}
        self.tick_count: Dict[str, int] = {s: 0 for s in symbols}
    
    def process_tick(self, tick: Tick) -> Optional[OHLCV]:
        """Process incoming tick and update candle"""
        if tick.symbol not in self.symbols:
            return None
        
        # Store tick
        self.tick_buffer[tick.symbol].append(tick)
        self.tick_count[tick.symbol] += 1
        self.last_price[tick.symbol] = tick.price
        
        # Update VWAP
        self._update_vwap(tick)
        
        # Update or create candle
        candle = self._update_candle(tick)
        
        return candle
    
    def _update_candle(self, tick: Tick) -> Optional[OHLCV]:
        """Update current candle with new tick"""
        current = self.current_candle[tick.symbol]
        
        # Check if we need new candle (1-minute intervals)
        if current is None or tick.timestamp.minute != current.timestamp.minute:
            # Save completed candle
            if current is not None:
                self.ohlcv_history[tick.symbol].append(current)
            
            # Create new candle
            new_candle = OHLCV(
                open=tick.price,
                high=tick.price,
                low=tick.price,
                close=tick.price,
                volume=tick.size,
                timestamp=tick.timestamp.replace(second=0, microsecond=0)
            )
            self.current_candle[tick.symbol] = new_candle
            return new_candle
        
        # Update existing candle
        current.high = max(current.high, tick.price)
        current.low = min(current.low, tick.price)
        current.close = tick.price
        current.volume += tick.size
        
        return current
    
    def _update_vwap(self, tick: Tick):
        """Update Volume-Weighted Average Price"""
        buffer = self.tick_buffer[tick.symbol]
        if len(buffer) == 0:
            return
        
        total_value = sum(t.price * t.size for t in buffer)
        total_volume = sum(t.size for t in buffer)
        
        if total_volume > 0:
            self.vwap[tick.symbol] = total_value / total_volume
    
    def get_tick_stats(self, symbol: str, seconds: int = 60) -> Dict:
        """Get tick statistics for last N seconds"""
        if symbol not in self.tick_buffer:
            return {"error": "Symbol not found"}
        
        cutoff = datetime.utcnow().timestamp() - seconds
        recent_ticks = [
            t for t in self.tick_buffer[symbol]
            if t.timestamp.timestamp() > cutoff
        ]
        
        if not recent_ticks:
            return {"error": "No recent ticks"}
        
        prices = [t.price for t in recent_ticks]
        sizes = [t.size for t in recent_ticks]
        
        return {
            "symbol": symbol,
            "tick_count": len(recent_ticks),
            "avg_price": round(statistics.mean(prices), 4),
            "price_range": round(max(prices) - min(prices), 4),
            "avg_size": round(statistics.mean(sizes), 0),
            "total_volume": sum(sizes),
            "vwap": round(self.vwap.get(symbol, prices[-1]), 4),
            "velocity": len(recent_ticks) / seconds  # ticks per second
        }
    
    def detect_imbalance(self, symbol: str) -> Dict:
        """Detect buy/sell imbalance in recent ticks"""
        if symbol not in self.tick_buffer:
            return {"error": "Symbol not found"}
        
        buffer = self.tick_buffer[symbol]
        if len(buffer) < 10:
            return {"error": "Insufficient ticks"}
        
        buy_volume = sum(t.size for t in buffer if t.side == "BID")
        sell_volume = sum(t.size for t in buffer if t.side == "ASK")
        trade_volume = sum(t.size for t in buffer if t.side == "TRADE")
        
        total = buy_volume + sell_volume + trade_volume
        if total == 0:
            return {"imbalance": 0}
        
        imbalance = (buy_volume - sell_volume) / total
        
        return {
            "symbol": symbol,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "trade_volume": trade_volume,
            "imbalance_ratio": round(imbalance, 3),
            "pressure": "BUY" if imbalance > 0.2 else "SELL" if imbalance < -0.2 else "NEUTRAL"
        }
    
    def get_liquidity_profile(self, symbol: str) -> Dict:
        """Analyze liquidity from tick data"""
        if symbol not in self.tick_buffer:
            return {"error": "Symbol not found"}
        
        buffer = list(self.tick_buffer[symbol])
        if len(buffer) < 20:
            return {"error": "Insufficient data"}
        
        # Calculate spread from bid/ask ticks
        bid_prices = [t.price for t in buffer if t.side == "BID"]
        ask_prices = [t.price for t in buffer if t.side == "ASK"]
        
        if bid_prices and ask_prices:
            best_bid = max(bid_prices)
            best_ask = min(ask_prices)
            spread = best_ask - best_bid
            spread_pct = (spread / ((best_bid + best_ask) / 2)) * 100
        else:
            spread = 0
            spread_pct = 0
        
        # Calculate depth indicators
        sizes = [t.size for t in buffer]
        
        return {
            "symbol": symbol,
            "spread": round(spread, 4),
            "spread_pct": round(spread_pct, 3),
            "avg_tick_size": round(statistics.mean(sizes), 0),
            "tick_frequency": self.tick_count[symbol] / 60,  # per minute
            "liquidity_score": "HIGH" if spread_pct < 0.1 else "MEDIUM" if spread_pct < 0.5 else "LOW"
        }
    
    def build_candles(self, symbol: str, timeframe: str = "1m") -> List[OHLCV]:
        """Build historical candles from tick data"""
        return self.ohlcv_history.get(symbol, [])
    
    def get_market_depth_summary(self, symbol: str) -> Dict:
        """Get summary of market depth from tick analysis"""
        stats = self.get_tick_stats(symbol, seconds=300)  # 5 min
        imbalance = self.detect_imbalance(symbol)
        liquidity = self.get_liquidity_profile(symbol)
        
        return {
            "symbol": symbol,
            "price_action": {
                "last_price": self.last_price.get(symbol),
                "vwap": self.vwap.get(symbol),
                "range_5m": stats.get("price_range", 0)
            },
            "flow": {
                "imbalance": imbalance.get("imbalance_ratio", 0),
                "pressure": imbalance.get("pressure", "NEUTRAL")
            },
            "liquidity": {
                "spread": liquidity.get("spread_pct", 0),
                "score": liquidity.get("liquidity_score", "UNKNOWN")
            },
            "recommendation": self._get_execution_recommendation(liquidity, imbalance)
        }
    
    def _get_execution_recommendation(self, liquidity: Dict, imbalance: Dict) -> str:
        """Generate execution recommendation"""
        spread_score = liquidity.get("liquidity_score", "MEDIUM")
        pressure = imbalance.get("pressure", "NEUTRAL")
        
        if spread_score == "HIGH" and pressure == "NEUTRAL":
            return "AGGRESSIVE_EXECUTION"
        elif spread_score == "LOW":
            return "PASSIVE_EXECUTION_PATIENT"
        elif pressure in ["BUY", "SELL"]:
            return f"JOIN_{pressure}_SIDE"
        return "NORMAL_EXECUTION"
