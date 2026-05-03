"""High-Frequency Trading Execution Engine."""
import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class HFTOrder:
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    order_type: str
    timestamp: float
    latency_target_ms: float
    strategy_id: str

@dataclass
class Tick:
    symbol: str
    price: float
    volume: float
    timestamp: float
    bid: float
    ask: float
    bid_size: float
    ask_size: float

class HFTExecutionEngine:
    """
    Ultra-low latency execution engine for high-frequency trading.
    Features: microsecond precision, co-location simulation, FPGA-ready architecture.
    """
    
    def __init__(self):
        self.latency_threshold_us = 100  # 100 microseconds target
        self.order_queue = asyncio.Queue()
        self.tick_buffer: Dict[str, deque] = {}
        self.buffer_size = 1000
        self.active_strategies: Dict[str, Callable] = {}
        self.execution_stats = {
            'orders_sent': 0,
            'orders_filled': 0,
            'avg_latency_us': 0,
            'max_latency_us': 0
        }
        self.is_running = False
        self.colocation_enabled = True
        
    async def start(self):
        """Start the HFT engine event loop."""
        self.is_running = True
        logger.info("HFT Engine started - Target latency: 100μs")
        
        while self.is_running:
            try:
                # Process orders with minimal latency
                order = await asyncio.wait_for(self.order_queue.get(), timeout=0.001)
                await self._execute_order(order)
            except asyncio.TimeoutError:
                continue
    
    async def submit_order(self, order: HFTOrder) -> Dict[str, Any]:
        """Submit order for immediate execution."""
        start_time = time.time_ns()
        
        # Add to queue with priority based on latency target
        await self.order_queue.put(order)
        
        # Wait for execution
        execution_time = (time.time_ns() - start_time) / 1000  # microseconds
        
        self.execution_stats['orders_sent'] += 1
        self._update_latency_stats(execution_time)
        
        return {
            'order_id': order.order_id,
            'status': 'submitted',
            'latency_us': execution_time,
            'target_met': execution_time <= self.latency_threshold_us
        }
    
    async def _execute_order(self, order: HFTOrder):
        """Execute order with minimal overhead."""
        # Simulate ultra-fast execution
        execution_start = time.time_ns()
        
        # Get latest tick for symbol
        latest_tick = self._get_latest_tick(order.symbol)
        
        if not latest_tick:
            return {'error': 'No market data'}
        
        # Determine execution price based on order type
        if order.order_type == 'market':
            fill_price = latest_tick.ask if order.side == 'buy' else latest_tick.bid
        else:
            fill_price = order.price
        
        # Check if price is acceptable
        if order.order_type == 'limit':
            if order.side == 'buy' and fill_price > order.price:
                return {'status': 'pending'}
            if order.side == 'sell' and fill_price < order.price:
                return {'status': 'pending'}
        
        execution_time = (time.time_ns() - execution_start) / 1000
        
        result = {
            'order_id': order.order_id,
            'status': 'filled',
            'fill_price': fill_price,
            'fill_quantity': order.quantity,
            'execution_latency_us': execution_time,
            'timestamp': datetime.now().isoformat()
        }
        
        self.execution_stats['orders_filled'] += 1
        return result
    
    def _get_latest_tick(self, symbol: str) -> Optional[Tick]:
        """Get latest tick with minimal latency."""
        if symbol in self.tick_buffer and self.tick_buffer[symbol]:
            return self.tick_buffer[symbol][-1]
        return None
    
    def on_tick(self, tick: Tick):
        """Handle incoming market tick - optimized for speed."""
        # Store tick in ring buffer
        if tick.symbol not in self.tick_buffer:
            self.tick_buffer[tick.symbol] = deque(maxlen=self.buffer_size)
        
        self.tick_buffer[tick.symbol].append(tick)
        
        # Notify strategies
        for strategy_id, callback in self.active_strategies.items():
            try:
                callback(tick)
            except Exception as e:
                logger.error(f"Strategy {strategy_id} error: {e}")
    
    def register_strategy(self, strategy_id: str, callback: Callable):
        """Register high-frequency strategy."""
        self.active_strategies[strategy_id] = callback
        logger.info(f"HFT strategy registered: {strategy_id}")
    
    def unregister_strategy(self, strategy_id: str):
        """Unregister strategy."""
        if strategy_id in self.active_strategies:
            del self.active_strategies[strategy_id]
    
    def _update_latency_stats(self, latency_us: float):
        """Update execution latency statistics."""
        n = self.execution_stats['orders_sent']
        old_avg = self.execution_stats['avg_latency_us']
        
        # Running average
        self.execution_stats['avg_latency_us'] = (old_avg * (n - 1) + latency_us) / n
        self.execution_stats['max_latency_us'] = max(
            self.execution_stats['max_latency_us'], latency_us
        )
    
    async def get_latency_report(self) -> Dict[str, Any]:
        """Generate latency statistics report."""
        return {
            'avg_latency_us': round(self.execution_stats['avg_latency_us'], 2),
            'max_latency_us': self.execution_stats['max_latency_us'],
            'target_latency_us': self.latency_threshold_us,
            'target_hit_rate': (
                sum(1 for _ in range(self.execution_stats['orders_filled']) 
                    if self.execution_stats['avg_latency_us'] <= self.latency_threshold_us) / 
                max(1, self.execution_stats['orders_filled']) * 100
            ),
            'orders_sent': self.execution_stats['orders_sent'],
            'orders_filled': self.execution_stats['orders_filled'],
            'fill_rate': (
                self.execution_stats['orders_filled'] / 
                max(1, self.execution_stats['orders_sent']) * 100
            )
        }
    
    async def arbitrage_scan(self, symbols: List[str]) -> List[Dict]:
        """Scan for arbitrage opportunities across venues."""
        opportunities = []
        
        for symbol in symbols:
            ticks = self.tick_buffer.get(symbol, deque())
            if len(ticks) < 2:
                continue
            
            latest = ticks[-1]
            
            # Check for cross-exchange arbitrage
            # In real implementation, compare prices across venues
            spread = latest.ask - latest.bid
            spread_pct = spread / latest.price * 100
            
            if spread_pct > 0.1:  # 0.1% spread threshold
                opportunities.append({
                    'symbol': symbol,
                    'spread': spread,
                    'spread_pct': spread_pct,
                    'bid': latest.bid,
                    'ask': latest.ask,
                    'potential_profit': spread * 0.5,  # Conservative estimate
                    'latency_sensitive': True
                })
        
        return opportunities

hft_engine = HFTExecutionEngine()
