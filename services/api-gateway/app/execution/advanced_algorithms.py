"""
Advanced Execution Algorithms
=============================
TWAP, VWAP, Implementation Shortfall, Smart Order Routing
Institutional-grade execution with minimal market impact
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class AlgoType(Enum):
    TWAP = "twap"  # Time Weighted Average Price
    VWAP = "vwap"  # Volume Weighted Average Price
    POV = "pov"    # Percentage of Volume
    IS = "is"      # Implementation Shortfall
    ADAPTIVE = "adaptive"  # Adaptive based on market conditions


@dataclass
class ExecutionOrder:
    """Order for algorithmic execution"""
    ticker: str
    side: str  # 'buy' or 'sell'
    total_quantity: int
    algo_type: AlgoType
    start_time: datetime
    end_time: datetime
    urgency: str = 'normal'  # 'low', 'normal', 'high', 'urgent'
    max_participation: float = 0.1  # Max % of volume
    price_limit: Optional[float] = None


@dataclass
class ExecutionSlice:
    """Single execution slice"""
    timestamp: datetime
    quantity: int
    price: float
    filled: bool = False


class ExecutionEngine:
    """
    Advanced algorithmic execution engine
    
    Algorithms:
    - TWAP: Spread evenly over time
    - VWAP: Trade proportionally to historical volume
    - POV: Target percentage of market volume
    - IS: Minimize deviation from arrival price
    - Adaptive: Adjust based on market conditions
    """
    
    def __init__(self):
        self.active_orders: Dict[str, ExecutionOrder] = {}
        self.execution_history: List[Dict] = []
        self.market_data: Dict[str, pd.DataFrame] = {}
    
    async def submit_order(self, order: ExecutionOrder) -> str:
        """Submit order for algorithmic execution"""
        order_id = f"{order.ticker}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.active_orders[order_id] = order
        
        logger.info(
            f"Submitted {order.algo_type.value} order: {order.total_quantity} "
            f"{order.ticker} {order.side}"
        )
        
        # Start execution
        asyncio.create_task(self._execute_order(order_id))
        
        return order_id
    
    async def _execute_order(self, order_id: str):
        """Execute order based on algorithm type"""
        order = self.active_orders.get(order_id)
        if not order:
            return
        
        try:
            if order.algo_type == AlgoType.TWAP:
                await self._execute_twap(order)
            elif order.algo_type == AlgoType.VWAP:
                await self._execute_vwap(order)
            elif order.algo_type == AlgoType.POV:
                await self._execute_pov(order)
            elif order.algo_type == AlgoType.IS:
                await self._execute_is(order)
            elif order.algo_type == AlgoType.ADAPTIVE:
                await self._execute_adaptive(order)
                
        except Exception as e:
            logger.error(f"Execution error for {order_id}: {e}")
        finally:
            if order_id in self.active_orders:
                del self.active_orders[order_id]
    
    async def _execute_twap(self, order: ExecutionOrder):
        """
        TWAP - Time Weighted Average Price
        Spread order evenly across time window
        """
        duration = (order.end_time - order.start_time).total_seconds()
        num_slices = max(int(duration / 60), 1)  # At least 1 per minute
        
        quantity_per_slice = order.total_quantity // num_slices
        remaining = order.total_quantity
        
        slices = []
        for i in range(num_slices):
            slice_qty = min(quantity_per_slice, remaining)
            if slice_qty <= 0:
                break
            
            slice_time = order.start_time + timedelta(seconds=i * (duration / num_slices))
            
            # Wait until slice time
            wait_seconds = (slice_time - datetime.now()).total_seconds()
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
            
            # Execute slice
            price = await self._get_market_price(order.ticker)
            filled = await self._execute_slice(order, slice_qty, price)
            
            slices.append({
                'time': slice_time,
                'quantity': slice_qty,
                'price': price,
                'filled': filled
            })
            
            remaining -= slice_qty
        
        self._record_execution(order, slices, 'twap')
    
    async def _execute_vwap(self, order: ExecutionOrder):
        """
        VWAP - Volume Weighted Average Price
        Trade proportionally to historical volume profile
        """
        # Get historical volume profile (would be real data in production)
        volume_profile = self._get_volume_profile(order.ticker)
        
        # Calculate slice sizes based on volume profile
        total_volume = sum(volume_profile.values())
        
        slices = []
        remaining = order.total_quantity
        
        for minute, volume_pct in sorted(volume_profile.items()):
            slice_qty = int(order.total_quantity * volume_pct)
            slice_qty = min(slice_qty, remaining)
            
            if slice_qty <= 0:
                continue
            
            slice_time = order.start_time + timedelta(minutes=minute)
            
            wait_seconds = (slice_time - datetime.now()).total_seconds()
            if wait_seconds > 0:
                await asyncio.sleep(min(wait_seconds, 60))
            
            price = await self._get_market_price(order.ticker)
            filled = await self._execute_slice(order, slice_qty, price)
            
            slices.append({
                'time': slice_time,
                'quantity': slice_qty,
                'price': price,
                'filled': filled
            })
            
            remaining -= slice_qty
            if remaining <= 0:
                break
        
        self._record_execution(order, slices, 'vwap')
    
    async def _execute_pov(self, order: ExecutionOrder):
        """
        POV - Percentage of Volume
        Participate at fixed % of market volume
        """
        target_participation = order.max_participation
        remaining = order.total_quantity
        
        slices = []
        while remaining > 0 and datetime.now() < order.end_time:
            # Get current market volume (would be real-time in production)
            market_volume = await self._get_market_volume(order.ticker)
            
            # Calculate slice size
            target_slice = int(market_volume * target_participation)
            slice_qty = min(target_slice, remaining, 1000)  # Max 1000 per slice
            
            if slice_qty > 0:
                price = await self._get_market_price(order.ticker)
                filled = await self._execute_slice(order, slice_qty, price)
                
                slices.append({
                    'time': datetime.now(),
                    'quantity': slice_qty,
                    'price': price,
                    'filled': filled
                })
                
                remaining -= slice_qty
            
            # Wait for next volume
            await asyncio.sleep(60)
        
        self._record_execution(order, slices, 'pov')
    
    async def _execute_is(self, order: ExecutionOrder):
        """
        Implementation Shortfall
        Minimize deviation from arrival price
        """
        # Get arrival price
        arrival_price = await self._get_market_price(order.ticker)
        
        # Trade more aggressively early
        slices = []
        remaining = order.total_quantity
        
        # Front-loaded execution
        pct_schedule = [0.3, 0.25, 0.2, 0.15, 0.1]
        
        for pct in pct_schedule:
            if remaining <= 0:
                break
            
            slice_qty = int(order.total_quantity * pct)
            slice_qty = min(slice_qty, remaining)
            
            if slice_qty <= 0:
                continue
            
            price = await self._get_market_price(order.ticker)
            filled = await self._execute_slice(order, slice_qty, price)
            
            slices.append({
                'time': datetime.now(),
                'quantity': slice_qty,
                'price': price,
                'filled': filled
            })
            
            remaining -= slice_qty
            
            # Adaptive wait based on market impact
            if filled and abs(price - arrival_price) / arrival_price > 0.001:
                await asyncio.sleep(120)  # Wait longer if moving price
            else:
                await asyncio.sleep(30)
        
        # VWAP remainder if any
        if remaining > 0:
            await self._execute_pov(order)
        
        self._record_execution(order, slices, 'is', arrival_price)
    
    async def _execute_adaptive(self, order: ExecutionOrder):
        """
        Adaptive Algorithm
        Adjust strategy based on market conditions
        """
        # Measure market conditions
        spread = await self._get_bid_ask_spread(order.ticker)
        volatility = await self._get_realized_volatility(order.ticker)
        
        # Choose strategy based on conditions
        if spread < 0.001 and volatility < 0.2:
            # Good conditions - aggressive
            logger.info(f"{order.ticker}: Low spread/vol, using aggressive execution")
            await self._execute_is(order)
        elif volatility > 0.4:
            # High volatility - use TWAP to spread risk
            logger.info(f"{order.ticker}: High volatility, using TWAP")
            await self._execute_twap(order)
        else:
            # Normal - use VWAP
            logger.info(f"{order.ticker}: Normal conditions, using VWAP")
            await self._execute_vwap(order)
    
    async def _execute_slice(self, order: ExecutionOrder, 
                            quantity: int, price: float) -> bool:
        """Execute a single slice (simulated)"""
        # In production: Send order to broker API
        logger.debug(
            f"Executing slice: {quantity} {order.ticker} @ {price}"
        )
        
        # Simulate 95% fill rate
        fill_probability = 0.95 if order.urgency != 'urgent' else 0.99
        filled = np.random.random() < fill_probability
        
        return filled
    
    async def _get_market_price(self, ticker: str) -> float:
        """Get current market price (simulated)"""
        # In production: Real-time market data feed
        base_price = 100.0 + hash(ticker) % 100
        noise = np.random.normal(0, 0.1)
        return round(base_price + noise, 2)
    
    async def _get_market_volume(self, ticker: str) -> int:
        """Get current market volume (simulated)"""
        # In production: Real-time volume data
        return np.random.randint(10000, 50000)
    
    async def _get_bid_ask_spread(self, ticker: str) -> float:
        """Get bid-ask spread (simulated)"""
        return np.random.uniform(0.0005, 0.005)
    
    async def _get_realized_volatility(self, ticker: str) -> float:
        """Get realized volatility (simulated)"""
        return np.random.uniform(0.1, 0.5)
    
    def _get_volume_profile(self, ticker: str) -> Dict[int, float]:
        """Get intraday volume profile"""
        # Typical U-shaped volume profile
        profile = {}
        for minute in range(390):  # Trading day minutes
            if minute < 30:  # Opening
                profile[minute] = 0.002
            elif minute > 360:  # Closing
                profile[minute] = 0.003
            elif 120 < minute < 240:  # Midday (lower volume)
                profile[minute] = 0.001
            else:
                profile[minute] = 0.0015
        
        # Normalize
        total = sum(profile.values())
        return {k: v/total for k, v in profile.items()}
    
    def _record_execution(self, order: ExecutionOrder, 
                         slices: List[Dict], algo: str, 
                         arrival_price: Optional[float] = None):
        """Record execution results"""
        total_filled = sum(s['quantity'] for s in slices if s['filled'])
        avg_price = np.mean([s['price'] for s in slices if s['filled']])
        
        implementation_shortfall = 0
        if arrival_price and avg_price:
            if order.side == 'buy':
                implementation_shortfall = (avg_price - arrival_price) / arrival_price
            else:
                implementation_shortfall = (arrival_price - avg_price) / arrival_price
        
        record = {
            'ticker': order.ticker,
            'side': order.side,
            'algorithm': algo,
            'total_quantity': order.total_quantity,
            'filled_quantity': total_filled,
            'fill_rate': total_filled / order.total_quantity if order.total_quantity > 0 else 0,
            'avg_price': round(avg_price, 4),
            'arrival_price': arrival_price,
            'implementation_shortfall_bps': round(implementation_shortfall * 10000, 2),
            'num_slices': len(slices),
            'start_time': order.start_time,
            'end_time': datetime.now(),
            'slices': slices
        }
        
        self.execution_history.append(record)
        logger.info(f"Execution complete: {record}")
    
    def get_execution_report(self, ticker: Optional[str] = None) -> List[Dict]:
        """Get execution performance report"""
        if ticker:
            return [h for h in self.execution_history if h['ticker'] == ticker]
        return self.execution_history


# Quick usage functions
def execute_twap(ticker: str, quantity: int, side: str, 
                 duration_minutes: int = 60) -> str:
    """Quick TWAP execution"""
    engine = ExecutionEngine()
    
    order = ExecutionOrder(
        ticker=ticker,
        side=side,
        total_quantity=quantity,
        algo_type=AlgoType.TWAP,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=duration_minutes)
    )
    
    return asyncio.run(engine.submit_order(order))


def execute_vwap(ticker: str, quantity: int, side: str,
                duration_minutes: int = 60) -> str:
    """Quick VWAP execution"""
    engine = ExecutionEngine()
    
    order = ExecutionOrder(
        ticker=ticker,
        side=side,
        total_quantity=quantity,
        algo_type=AlgoType.VWAP,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=duration_minutes)
    )
    
    return asyncio.run(engine.submit_order(order))


def get_execution_performance(order_id: str) -> Optional[Dict]:
    """Get performance for specific execution"""
    # In production: Look up by order_id
    pass
