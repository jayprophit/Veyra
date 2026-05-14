"""
High-Frequency Trading Engine
=============================
Ultra-low latency trading engine for institutional HFT
"""

import asyncio
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import deque, defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class HFTStrategy(Enum):
    """HFT strategy types"""
    MARKET_MAKING = "market_making"
    ARBITRAGE = "arbitrage"
    LATENCY_ARBITRAGE = "latency_arbitrage"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    MOMENTUM_IGNITION = "momentum_ignition"
    LIQUIDITY_DETECTION = "liquidity_detection"
    ORDER_FLOW_ANALYSIS = "order_flow_analysis"


@dataclass
class HFTSignal:
    """HFT trading signal"""
    strategy: HFTStrategy
    symbol: str
    action: str  # buy/sell
    quantity: float
    price: Optional[float]
    confidence: float
    latency_ns: int  # nanoseconds
    timestamp_ns: int  # nanoseconds since epoch
    execution_priority: int  # 0=highest priority
    expected_hold_time_ms: int
    risk_score: float
    metadata: Dict[str, Any]


class MarketMaker:
    """Market making strategy for HFT"""
    
    def __init__(self, symbol: str, spread_bps: float = 5.0, inventory_limit: float = 10000.0):
        self.symbol = symbol
        self.spread_bps = spread_bps
        self.inventory_limit = inventory_limit
        self.current_inventory = 0.0
        self.mid_price = 0.0
        self.best_bid = 0.0
        self.best_ask = 0.0
        self.order_book = {"bids": [], "asks": []}
        
    def update_quotes(self, mid_price: float, order_flow: Dict[str, float]) -> Tuple[float, float]:
        """Update bid/ask quotes based on market conditions"""
        try:
            self.mid_price = mid_price
            
            # Calculate spread
            spread = mid_price * self.spread_bps / 10000.0
            half_spread = spread / 2.0
            
            # Inventory skew adjustment
            inventory_ratio = self.current_inventory / self.inventory_limit
            skew_adjustment = inventory_ratio * half_spread * 0.5  # 50% of spread for skew
            
            # Update quotes
            self.best_bid = mid_price - half_spread - skew_adjustment
            self.best_ask = mid_price + half_spread - skew_adjustment
            
            # Size quotes based on order flow
            bid_size = min(abs(order_flow.get("buy_pressure", 0)), 1000.0)
            ask_size = min(abs(order_flow.get("sell_pressure", 0)), 1000.0)
            
            return (self.best_bid, self.best_ask)
            
        except Exception as e:
            logger.error(f"Error updating quotes: {e}")
            return (self.best_bid, self.best_ask)
            
    def should_quote(self) -> bool:
        """Check if should place quotes"""
        return abs(self.current_inventory) < self.inventory_limit


class ArbitrageEngine:
    """Multi-venue arbitrage engine"""
    
    def __init__(self):
        self.venue_prices: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.arbitrage_opportunities: List[Dict] = []
        self.execution_history: List[Dict] = []
        
    async def scan_arbitrage(self, venues: List[str], symbols: List[str]):
        """Scan for arbitrage opportunities"""
        try:
            opportunities = []
            
            for symbol in symbols:
                # Get prices from all venues
                prices = {}
                for venue in venues:
                    price = await self._get_venue_price(venue, symbol)
                    if price:
                        prices[venue] = price
                        
                if len(prices) < 2:
                    continue
                    
                # Find arbitrage opportunities
                min_price_venue = min(prices, key=prices.get)
                max_price_venue = max(prices, key=prices.get)
                
                min_price = prices[min_price_venue]
                max_price = prices[max_price_venue]
                
                # Calculate arbitrage profit
                gross_profit = max_price - min_price
                estimated_fees = await self._calculate_arbitrage_fees(
                    min_price_venue, max_price_venue, symbol, min_price
                )
                net_profit = gross_profit - estimated_fees
                
                if net_profit > 0:
                    # Calculate execution time estimate
                    execution_time = await self._estimate_execution_time(
                        min_price_venue, max_price_venue, symbol
                    )
                    
                    opportunities.append({
                        "symbol": symbol,
                        "buy_venue": min_price_venue,
                        "sell_venue": max_price_venue,
                        "buy_price": min_price,
                        "sell_price": max_price,
                        "gross_profit": gross_profit,
                        "estimated_fees": estimated_fees,
                        "net_profit": net_profit,
                        "profit_margin": net_profit / min_price,
                        "execution_time_ms": execution_time,
                        "timestamp_ns": time.time_ns()
                    })
                        
            self.arbitrage_opportunities = opportunities
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scanning arbitrage: {e}")
            return []
            
    async def execute_arbitrage(self, opportunity: Dict[str, Any]) -> bool:
        """Execute arbitrage opportunity"""
        try:
            # Execute buy order on cheaper venue
            buy_order = {
                "venue": opportunity["buy_venue"],
                "symbol": opportunity["symbol"],
                "side": "buy",
                "quantity": 10000.0,  # Standard size
                "order_type": "market",
                "timestamp_ns": time.time_ns()
            }
            
            # Execute sell order on expensive venue
            sell_order = {
                "venue": opportunity["sell_venue"],
                "symbol": opportunity["symbol"],
                "side": "sell",
                "quantity": 10000.0,
                "order_type": "market",
                "timestamp_ns": time.time_ns()
            }
            
            # Execute simultaneously
            buy_result, sell_result = await asyncio.gather(
                self._execute_venue_order(buy_order),
                self._execute_venue_order(sell_order),
                return_exceptions=True
            )
            
            # Record execution
            execution_record = {
                "opportunity": opportunity,
                "buy_result": buy_result,
                "sell_result": sell_result,
                "executed_at": datetime.now(),
                "success": buy_result.get("success", False) and sell_result.get("success", False)
            }
            
            self.execution_history.append(execution_record)
            
            return execution_record["success"]
            
        except Exception as e:
            logger.error(f"Error executing arbitrage: {e}")
            return False
            
    async def _get_venue_price(self, venue: str, symbol: str) -> Optional[float]:
        """Get price from specific venue"""
        # Simulate venue price fetch
        base_price = 100.0 + np.random.normal(0, 0.1)
        venue_adjustment = {"venue1": 0.0, "venue2": -0.01, "venue3": 0.005}.get(venue, 0.0)
        return base_price + venue_adjustment
        
    async def _calculate_arbitrage_fees(self, buy_venue: str, sell_venue: str, 
                                     symbol: str, quantity: float) -> float:
        """Calculate arbitrage execution fees"""
        # Simulate fee calculation
        buy_fee = quantity * 0.0002  # 2 bps
        sell_fee = quantity * 0.0002
        return buy_fee + sell_fee
        
    async def _estimate_execution_time(self, buy_venue: str, sell_venue: str, 
                                  symbol: str) -> int:
        """Estimate arbitrage execution time"""
        # Simulate execution time based on venue
        venue_speed = {"venue1": 10, "venue2": 15, "venue3": 8}.get(buy_venue, 10)
        return max(venue_speed, {"venue1": 10, "venue2": 15, "venue3": 8}.get(sell_venue, 10))
        
    async def _execute_venue_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Execute order on specific venue"""
        # Simulate venue order execution
        await asyncio.sleep(0.001)  # 1ms execution time
        return {
            "success": True,
            "executed_price": 100.0,
            "executed_quantity": order["quantity"],
            "execution_time_ms": 1
        }


class LatencyOptimizer:
    """Optimize trading latency"""
    
    def __init__(self):
        self.latency_measurements: Dict[str, List[int]] = defaultdict(list)
        self.optimal_venues: Dict[str, str] = {}
        self.connection_pools: Dict[str, Any] = {}
        
    async def measure_latency(self, venue: str) -> int:
        """Measure round-trip latency to venue"""
        try:
            start_time = time.time_ns()
            
            # Send ping to venue
            await self._ping_venue(venue)
            
            end_time = time.time_ns()
            latency_ns = end_time - start_time
            
            # Store measurement
            self.latency_measurements[venue].append(latency_ns)
            
            # Keep only last 1000 measurements
            if len(self.latency_measurements[venue]) > 1000:
                self.latency_measurements[venue] = self.latency_measurements[venue][-1000:]
                
            return latency_ns // 1000000  # Convert to milliseconds
            
        except Exception as e:
            logger.error(f"Error measuring latency to {venue}: {e}")
            return 999999  # High latency on error
            
    async def _ping_venue(self, venue: str):
        """Ping venue for latency measurement"""
        # Simulate venue ping
        await asyncio.sleep(0.0001)  # 0.1ms round trip
        
    def get_optimal_venue(self, symbol: str) -> str:
        """Get optimal venue for symbol based on latency"""
        # Calculate average latency for each venue
        avg_latencies = {}
        for venue, measurements in self.latency_measurements.items():
            if measurements:
                avg_latencies[venue] = np.mean(measurements)
                
        if avg_latencies:
            optimal = min(avg_latencies, key=avg_latencies.get)
            return optimal
        return "default"


class HighFrequencyTradingEngine:
    """Main HFT engine"""
    
    def __init__(self):
        self.is_running = False
        self.market_makers: Dict[str, MarketMaker] = {}
        self.arbitrage_engine = ArbitrageEngine()
        self.latency_optimizer = LatencyOptimizer()
        self.order_book: Dict[str, Dict] = defaultdict(lambda: {"bids": [], "asks": []})
        self.trade_history: List[Dict] = []
        self.performance_metrics = {
            "total_trades": 0,
            "total_pnl": 0.0,
            "win_rate": 0.0,
            "avg_latency_ms": 0.0,
            "throughput_trades_per_sec": 0.0
        }
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
    async def start(self):
        """Start HFT engine"""
        try:
            self.is_running = True
            logger.info("HFT engine started")
            
            # Start HFT tasks
            tasks = [
                asyncio.create_task(self._market_making_loop()),
                asyncio.create_task(self._arbitrage_loop()),
                asyncio.create_task(self._latency_optimization_loop()),
                asyncio.create_task(self._performance_monitoring_loop())
            ]
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error starting HFT engine: {e}")
            self.is_running = False
            
    async def stop(self):
        """Stop HFT engine"""
        self.is_running = False
        logger.info("HFT engine stopped")
        
    async def _market_making_loop(self):
        """Market making main loop"""
        while self.is_running:
            try:
                for symbol, market_maker in self.market_makers.items():
                    # Get current order flow
                    order_flow = await self._get_order_flow(symbol)
                    
                    # Get mid price
                    mid_price = await self._get_mid_price(symbol)
                    
                    if mid_price and market_maker.should_quote():
                        # Update quotes
                        bid, ask = market_maker.update_quotes(mid_price, order_flow)
                        
                        # Place quotes
                        await self._place_quotes(symbol, bid, ask)
                        
                await asyncio.sleep(0.001)  # 1ms loop
                
            except Exception as e:
                logger.error(f"Error in market making loop: {e}")
                await asyncio.sleep(0.01)
                
    async def _arbitrage_loop(self):
        """Arbitrage detection and execution loop"""
        while self.is_running:
            try:
                # Scan for arbitrage opportunities
                venues = ["venue1", "venue2", "venue3"]
                symbols = ["AAPL", "GOOGL", "MSFT"]
                
                opportunities = await self.arbitrage_engine.scan_arbitrage(venues, symbols)
                
                # Execute profitable opportunities
                for opportunity in opportunities:
                    if opportunity["net_profit"] > 0.01:  # Minimum profit threshold
                        await self.arbitrage_engine.execute_arbitrage(opportunity)
                        
                await asyncio.sleep(0.01)  # 10ms scan interval
                
            except Exception as e:
                logger.error(f"Error in arbitrage loop: {e}")
                await asyncio.sleep(0.01)
                
    async def _latency_optimization_loop(self):
        """Latency optimization loop"""
        while self.is_running:
            try:
                venues = ["venue1", "venue2", "venue3"]
                
                # Measure latency to all venues
                for venue in venues:
                    await self.latency_optimizer.measure_latency(venue)
                    
                await asyncio.sleep(1.0)  # Measure every second
                
            except Exception as e:
                logger.error(f"Error in latency optimization loop: {e}")
                await asyncio.sleep(1.0)
                
    async def _performance_monitoring_loop(self):
        """Performance monitoring loop"""
        while self.is_running:
            try:
                # Calculate performance metrics
                self._calculate_performance_metrics()
                
                # Log performance
                logger.info(f"HFT Performance: {self.performance_metrics}")
                
                await asyncio.sleep(5.0)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(5.0)
                
    async def _get_order_flow(self, symbol: str) -> Dict[str, float]:
        """Get current order flow for symbol"""
        # Simulate order flow analysis
        return {
            "buy_pressure": np.random.uniform(-1000, 1000),
            "sell_pressure": np.random.uniform(-1000, 1000),
            "imbalance": np.random.uniform(-500, 500)
        }
        
    async def _get_mid_price(self, symbol: str) -> Optional[float]:
        """Get mid price for symbol"""
        # Get from order book
        if symbol in self.order_book:
            bids = self.order_book[symbol]["bids"]
            asks = self.order_book[symbol]["asks"]
            
            if bids and asks:
                best_bid = max(bids, key=lambda x: x["price"])
                best_ask = min(asks, key=lambda x: x["price"])
                return (best_bid["price"] + best_ask["price"]) / 2.0
                
        return None
        
    async def _place_quotes(self, symbol: str, bid: float, ask: float):
        """Place bid/ask quotes"""
        # Simulate quote placement
        quote_size = 1000.0
        
        # Cancel existing quotes
        await self._cancel_existing_quotes(symbol)
        
        # Place new quotes
        bid_order = {
            "symbol": symbol,
            "side": "buy",
            "price": bid,
            "quantity": quote_size,
            "order_type": "limit",
            "timestamp_ns": time.time_ns()
        }
        
        ask_order = {
            "symbol": symbol,
            "side": "sell",
            "price": ask,
            "quantity": quote_size,
            "order_type": "limit",
            "timestamp_ns": time.time_ns()
        }
        
        # Submit quotes
        await self._submit_order(bid_order)
        await self._submit_order(ask_order)
        
    async def _cancel_existing_quotes(self, symbol: str):
        """Cancel existing quotes for symbol"""
        # Simulate quote cancellation
        pass
        
    async def _submit_order(self, order: Dict[str, Any]):
        """Submit order to exchange"""
        # Simulate order submission
        execution_time = np.random.uniform(0.1, 2.0)  # ms
        await asyncio.sleep(execution_time / 1000.0)
        
    def _calculate_performance_metrics(self):
        """Calculate HFT performance metrics"""
        try:
            # Calculate win rate
            if self.trade_history:
                winning_trades = len([t for t in self.trade_history if t.get("pnl", 0) > 0])
                self.performance_metrics["win_rate"] = winning_trades / len(self.trade_history)
                
            # Calculate average latency
            if self.latency_optimizer.latency_measurements:
                all_measurements = []
                for measurements in self.latency_optimizer.latency_measurements.values():
                    all_measurements.extend(measurements)
                if all_measurements:
                    self.performance_metrics["avg_latency_ms"] = np.mean(all_measurements) / 1000000.0
                    
            # Calculate throughput
            recent_trades = [t for t in self.trade_history 
                            if (datetime.now() - t.get("timestamp", datetime.now())).seconds < 60]
            self.performance_metrics["throughput_trades_per_sec"] = len(recent_trades) / 60.0
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            
    def add_market_maker(self, symbol: str, spread_bps: float = 5.0, 
                        inventory_limit: float = 10000.0):
        """Add market maker for symbol"""
        self.market_makers[symbol] = MarketMaker(symbol, spread_bps, inventory_limit)
        logger.info(f"Added market maker for {symbol}")
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            "performance_metrics": self.performance_metrics,
            "active_market_makers": list(self.market_makers.keys()),
            "arbitrage_opportunities": len(self.arbitrage_engine.arbitrage_opportunities),
            "execution_history": len(self.arbitrage_engine.execution_history),
            "latency_optimization": {
                venue: {
                    "avg_latency_ms": np.mean(measurements) / 1000000.0 if measurements else 0,
                    "measurements_count": len(measurements)
                }
                for venue, measurements in self.latency_optimizer.latency_measurements.items()
            }
        }


# Global HFT engine instance
_hft_engine = None

def get_hft_engine() -> HighFrequencyTradingEngine:
    """Get the global HFT engine instance"""
    global _hft_engine
    if _hft_engine is None:
        _hft_engine = HighFrequencyTradingEngine()
    return _hft_engine
