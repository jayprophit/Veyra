"""
Liquidity Aggregation
====================
Aggregate liquidity from multiple venues for optimal execution
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LiquiditySource(Enum):
    """Liquidity source types"""
    EXCHANGE = "exchange"
    DARK_POOL = "dark_pool"
    ECN = "ecn"
    INTERNAL = "internal"
    EXTERNAL = "external"
    RETAIL = "retail"


@dataclass
class LiquidityData:
    """Liquidity data from venue"""
    venue_id: str
    venue_name: str
    source_type: LiquiditySource
    symbol: str
    bids: List[Tuple[float, float]]  # (price, quantity)
    asks: List[Tuple[float, float]]  # (price, quantity)
    timestamp: datetime
    latency_ms: float
    reliability_score: float
    fee_structure: Dict[str, float]
    volume_weight: float


@dataclass
class AggregatedOrderBook:
    """Aggregated order book across venues"""
    symbol: str
    aggregated_bids: List[Tuple[float, float, List[str]]]  # (price, quantity, venue_ids)
    aggregated_asks: List[Tuple[float, float, List[str]]]  # (price, quantity, venue_ids)
    total_bid_size: float
    total_ask_size: float
    best_bid: float
    best_ask: float
    spread: float
    mid_price: float
    venue_contributions: Dict[str, Dict[str, float]]
    aggregation_timestamp: datetime
    data_sources: List[str]


class LiquidityAggregator:
    """Main liquidity aggregation system"""
    
    def __init__(self):
        self.liquidity_sources: Dict[str, Any] = {}
        self.aggregated_books: Dict[str, AggregatedOrderBook] = {}
        self.liquidity_history: List[Dict] = []
        self.venue_weights: Dict[str, float] = {}
        self.aggregation_config = {
            "max_latency_ms": 100.0,
            "min_reliability": 0.8,
            "weight_by_volume": True,
            "include_dark_pools": True,
            "real_time_update": True,
            "aggregation_interval_ms": 50
        }
        
    async def add_liquidity_source(self, source_id: str, source_config: Dict[str, Any]):
        """Add liquidity source"""
        try:
            source_type = LiquiditySource(source_config.get("type", "exchange"))
            
            if source_type == LiquiditySource.EXCHANGE:
                self.liquidity_sources[source_id] = ExchangeLiquiditySource(source_config)
            elif source_type == LiquiditySource.DARK_POOL:
                self.liquidity_sources[source_id] = DarkPoolLiquiditySource(source_config)
            elif source_type == LiquiditySource.ECN:
                self.liquidity_sources[source_id] = ECNLiquiditySource(source_config)
            elif source_type == LiquiditySource.INTERNAL:
                self.liquidity_sources[source_id] = InternalLiquiditySource(source_config)
            else:
                self.liquidity_sources[source_id] = ExternalLiquiditySource(source_config)
                
            logger.info(f"Added liquidity source: {source_id} ({source_type.value})")
            
        except Exception as e:
            logger.error(f"Error adding liquidity source {source_id}: {e}")
            raise
            
    async def aggregate_liquidity(self, symbol: str) -> AggregatedOrderBook:
        """Aggregate liquidity for symbol"""
        try:
            # Get liquidity data from all sources
            liquidity_data = await self._collect_liquidity_data(symbol)
            
            if not liquidity_data:
                return self._create_empty_book(symbol)
                
            # Filter by quality criteria
            filtered_data = self._filter_liquidity_data(liquidity_data)
            
            # Aggregate order book
            aggregated_book = self._aggregate_order_books(symbol, filtered_data)
            
            # Calculate venue weights
            self._update_venue_weights(symbol, aggregated_book)
            
            # Store aggregated book
            self.aggregated_books[symbol] = aggregated_book
            
            # Record aggregation
            self.liquidity_history.append({
                "timestamp": datetime.now(),
                "symbol": symbol,
                "total_sources": len(liquidity_data),
                "filtered_sources": len(filtered_data),
                "total_bid_size": aggregated_book.total_bid_size,
                "total_ask_size": aggregated_book.total_ask_size,
                "spread": aggregated_book.spread,
                "venues": list(aggregated_book.venue_contributions.keys())
            })
            
            logger.info(f"Aggregated liquidity for {symbol}: {len(filtered_data)} sources")
            
            return aggregated_book
            
        except Exception as e:
            logger.error(f"Error aggregating liquidity for {symbol}: {e}")
            return self._create_empty_book(symbol)
            
    async def _collect_liquidity_data(self, symbol: str) -> List[LiquidityData]:
        """Collect liquidity data from all sources"""
        tasks = []
        
        for source_id, source in self.liquidity_sources.items():
            task = asyncio.create_task(source.get_order_book(symbol))
            tasks.append((source_id, task))
            
        # Wait for all sources
        results = []
        for source_id, task in tasks:
            try:
                order_book = await task
                if order_book:
                    liquidity_data = LiquidityData(
                        venue_id=source_id,
                        venue_name=source.name,
                        source_type=source.source_type,
                        symbol=symbol,
                        bids=order_book.get("bids", []),
                        asks=order_book.get("asks", []),
                        timestamp=order_book.get("timestamp", datetime.now()),
                        latency_ms=order_book.get("latency_ms", 50.0),
                        reliability_score=source.reliability_score,
                        fee_structure=source.fee_structure,
                        volume_weight=self.venue_weights.get(source_id, 1.0)
                    )
                    results.append(liquidity_data)
                    
            except Exception as e:
                logger.error(f"Error getting liquidity from {source_id}: {e}")
                
        return results
        
    def _filter_liquidity_data(self, liquidity_data: List[LiquidityData]) -> List[LiquidityData]:
        """Filter liquidity data by quality criteria"""
        filtered = []
        
        for data in liquidity_data:
            # Check latency
            if data.latency_ms > self.aggregation_config["max_latency_ms"]:
                continue
                
            # Check reliability
            if data.reliability_score < self.aggregation_config["min_reliability"]:
                continue
                
            # Check dark pool inclusion
            if (data.source_type == LiquiditySource.DARK_POOL and 
                not self.aggregation_config["include_dark_pools"]):
                continue
                
            filtered.append(data)
            
        return filtered
        
    def _aggregate_order_books(self, symbol: str, 
                            liquidity_data: List[LiquidityData]) -> AggregatedOrderBook:
        """Aggregate order books from multiple sources"""
        try:
            # Combine all bids and asks
            all_bids = []
            all_asks = []
            venue_contributions = {}
            
            for data in liquidity_data:
                # Add venue info to each price level
                venue_bids = [(price, qty, data.venue_id) for price, qty in data.bids]
                venue_asks = [(price, qty, data.venue_id) for price, qty in data.asks]
                
                all_bids.extend(venue_bids)
                all_asks.extend(venue_asks)
                
                # Track venue contributions
                total_bid_qty = sum(qty for _, qty, _ in venue_bids)
                total_ask_qty = sum(qty for _, qty, _ in venue_asks)
                
                if data.venue_id not in venue_contributions:
                    venue_contributions[data.venue_id] = {"bids": 0, "asks": 0}
                    
                venue_contributions[data.venue_id]["bids"] += total_bid_qty
                venue_contributions[data.venue_id]["asks"] += total_ask_qty
            
            # Sort by price
            all_bids.sort(key=lambda x: x[0], reverse=True)  # Highest price first
            all_asks.sort(key=lambda x: x[0])  # Lowest price first
            
            # Aggregate at same price levels
            aggregated_bids = self._aggregate_price_levels(all_bids)
            aggregated_asks = self._aggregate_price_levels(all_asks)
            
            # Calculate totals
            total_bid_size = sum(qty for _, qty, _ in aggregated_bids)
            total_ask_size = sum(qty for _, qty, _ in aggregated_asks)
            
            # Calculate best prices
            best_bid = aggregated_bids[0][0] if aggregated_bids else 0.0
            best_ask = aggregated_asks[0][0] if aggregated_asks else float('inf')
            
            # Calculate spread and mid price
            spread = best_ask - best_bid if best_bid > 0 and best_ask < float('inf') else 0.0
            mid_price = (best_bid + best_ask) / 2.0 if best_bid > 0 and best_ask < float('inf') else 0.0
            
            return AggregatedOrderBook(
                symbol=symbol,
                aggregated_bids=aggregated_bids,
                aggregated_asks=aggregated_asks,
                total_bid_size=total_bid_size,
                total_ask_size=total_ask_size,
                best_bid=best_bid,
                best_ask=best_ask,
                spread=spread,
                mid_price=mid_price,
                venue_contributions=venue_contributions,
                aggregation_timestamp=datetime.now(),
                data_sources=[data.venue_id for data in liquidity_data]
            )
            
        except Exception as e:
            logger.error(f"Error aggregating order books: {e}")
            return self._create_empty_book(symbol)
            
    def _aggregate_price_levels(self, orders: List[Tuple[float, float, str]]) -> List[Tuple[float, float, List[str]]]:
        """Aggregate orders at same price levels"""
        if not orders:
            return []
            
        aggregated = {}
        
        for price, qty, venue_id in orders:
            if price not in aggregated:
                aggregated[price] = {"quantity": 0.0, "venues": set()}
            aggregated[price]["quantity"] += qty
            aggregated[price]["venues"].add(venue_id)
            
        # Convert back to list format
        result = []
        for price, data in aggregated.items():
            result.append((price, data["quantity"], list(data["venues"])))
            
        # Sort by price
        result.sort(key=lambda x: x[0])
        return result
        
    def _update_venue_weights(self, symbol: str, aggregated_book: AggregatedOrderBook):
        """Update venue weights based on contribution"""
        try:
            total_contribution = 0.0
            
            for venue_id, contributions in aggregated_book.venue_contributions.items():
                total_contribution += contributions["bids"] + contributions["asks"]
                
            if total_contribution > 0:
                for venue_id, contributions in aggregated_book.venue_contributions.items():
                    weight = (contributions["bids"] + contributions["asks"]) / total_contribution
                    
                    # Smooth weight updates
                    current_weight = self.venue_weights.get(venue_id, 1.0)
                    new_weight = current_weight * 0.9 + weight * 0.1  # Exponential smoothing
                    self.venue_weights[venue_id] = new_weight
                    
        except Exception as e:
            logger.error(f"Error updating venue weights: {e}")
            
    def _create_empty_book(self, symbol: str) -> AggregatedOrderBook:
        """Create empty order book"""
        return AggregatedOrderBook(
            symbol=symbol,
            aggregated_bids=[],
            aggregated_asks=[],
            total_bid_size=0.0,
            total_ask_size=0.0,
            best_bid=0.0,
            best_ask=float('inf'),
            spread=0.0,
            mid_price=0.0,
            venue_contributions={},
            aggregation_timestamp=datetime.now(),
            data_sources=[]
        )
        
    async def get_optimal_execution_plan(self, symbol: str, order_size: float, 
                                   order_side: str) -> Dict[str, Any]:
        """Get optimal execution plan across venues"""
        try:
            aggregated_book = self.aggregated_books.get(symbol)
            if not aggregated_book:
                return {"error": "No liquidity data available"}
                
            # Analyze liquidity depth
            depth_analysis = self._analyze_liquidity_depth(aggregated_book, order_size)
            
            # Calculate execution costs
            execution_costs = await self._calculate_execution_costs(
                symbol, order_size, order_side, aggregated_book
            )
            
            # Recommend execution strategy
            strategy = self._recommend_execution_strategy(depth_analysis, execution_costs)
            
            return {
                "symbol": symbol,
                "order_size": order_size,
                "order_side": order_side,
                "aggregated_book": {
                    "best_bid": aggregated_book.best_bid,
                    "best_ask": aggregated_book.best_ask,
                    "spread": aggregated_book.spread,
                    "total_bid_size": aggregated_book.total_bid_size,
                    "total_ask_size": aggregated_book.total_ask_size
                },
                "depth_analysis": depth_analysis,
                "execution_costs": execution_costs,
                "recommended_strategy": strategy,
                "venue_contributions": aggregated_book.venue_contributions,
                "data_sources": aggregated_book.data_sources
            }
            
        except Exception as e:
            logger.error(f"Error creating execution plan: {e}")
            return {"error": str(e)}
            
    def _analyze_liquidity_depth(self, book: AggregatedOrderBook, 
                              order_size: float) -> Dict[str, Any]:
        """Analyze liquidity depth"""
        try:
            # Calculate depth levels
            if book.aggregated_bids and book.aggregated_asks:
                # Bid side depth
                bid_depth = 0.0
                bid_levels = 0
                for price, qty, venues in book.aggregated_bids:
                    bid_depth += qty
                    bid_levels += 1
                    if bid_depth >= order_size:
                        break
                        
                # Ask side depth
                ask_depth = 0.0
                ask_levels = 0
                for price, qty, venues in book.aggregated_asks:
                    ask_depth += qty
                    ask_levels += 1
                    if ask_depth >= order_size:
                        break
                        
                # Calculate slippage estimates
                avg_bid_price = sum(price * qty for price, qty, _ in book.aggregated_bids[:bid_levels]) / sum(qty for _, qty, _ in book.aggregated_bids[:bid_levels])
                avg_ask_price = sum(price * qty for price, qty, _ in book.aggregated_asks[:ask_levels]) / sum(qty for _, qty, _ in book.aggregated_asks[:ask_levels])
                
                return {
                    "bid_side": {
                        "available_size": bid_depth,
                        "levels_required": bid_levels,
                        "average_price": avg_bid_price,
                        "slippage_estimate": 0.0 if bid_depth >= order_size else (order_size - bid_depth) / order_size * 0.01
                    },
                    "ask_side": {
                        "available_size": ask_depth,
                        "levels_required": ask_levels,
                        "average_price": avg_ask_price,
                        "slippage_estimate": 0.0 if ask_depth >= order_size else (order_size - ask_depth) / order_size * 0.01
                    },
                    "overall_liquidity_score": (bid_depth + ask_depth) / 2.0
                }
            else:
                return {
                    "bid_side": {"available_size": 0.0, "slippage_estimate": 1.0},
                    "ask_side": {"available_size": 0.0, "slippage_estimate": 1.0},
                    "overall_liquidity_score": 0.0
                }
                
        except Exception as e:
            logger.error(f"Error analyzing liquidity depth: {e}")
            return {"error": str(e)}
            
    async def _calculate_execution_costs(self, symbol: str, order_size: float, 
                                   order_side: str, book: AggregatedOrderBook) -> Dict[str, Any]:
        """Calculate execution costs across venues"""
        try:
            venue_costs = {}
            
            for venue_id, contributions in book.venue_contributions.items():
                # Get venue source
                source = self.liquidity_sources.get(venue_id)
                if not source:
                    continue
                    
                # Calculate fees
                if order_side == "buy":
                    fee_rate = source.fee_structure.get("taker_fee", 0.001)
                else:
                    fee_rate = source.fee_structure.get("taker_fee", 0.001)
                    
                # Estimate execution price
                if order_side == "buy" and book.aggregated_asks:
                    avg_price = sum(price * qty for price, qty, _ in book.aggregated_asks[:5]) / sum(qty for _, qty, _ in book.aggregated_asks[:5])
                elif order_side == "sell" and book.aggregated_bids:
                    avg_price = sum(price * qty for price, qty, _ in book.aggregated_bids[:5]) / sum(qty for _, qty, _ in book.aggregated_bids[:5])
                else:
                    avg_price = book.mid_price
                    
                execution_cost = order_size * avg_price * fee_rate
                
                venue_costs[venue_id] = {
                    "estimated_fee": execution_cost,
                    "liquidity_contribution": contributions["bids"] + contributions["asks"],
                    "average_latency_ms": getattr(source, 'latency_ms', 50.0),
                    "reliability_score": source.reliability_score
                }
                
            return venue_costs
            
        except Exception as e:
            logger.error(f"Error calculating execution costs: {e}")
            return {}
            
    def _recommend_execution_strategy(self, depth_analysis: Dict[str, Any], 
                                 execution_costs: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend optimal execution strategy"""
        try:
            # Analyze liquidity availability
            if order_side == "buy":
                available_liquidity = depth_analysis["ask_side"]["available_size"]
                slippage_estimate = depth_analysis["ask_side"]["slippage_estimate"]
            else:
                available_liquidity = depth_analysis["bid_side"]["available_size"]
                slippage_estimate = depth_analysis["bid_side"]["slippage_estimate"]
                
            # Calculate cost-benefit for each venue
            venue_scores = {}
            for venue_id, costs in execution_costs.items():
                # Normalize costs (lower is better)
                max_cost = max(c["estimated_fee"] for c in execution_costs.values())
                cost_score = 1.0 - (costs["estimated_fee"] / max_cost) if max_cost > 0 else 1.0
                
                # Combine with liquidity and reliability
                liquidity_score = costs["liquidity_contribution"] / 10000.0  # Normalize
                reliability_score = costs["reliability_score"]
                latency_score = max(0, 1.0 - costs["average_latency_ms"] / 100.0)
                
                # Weighted score
                total_score = (cost_score * 0.4 + 
                              liquidity_score * 0.3 + 
                              reliability_score * 0.2 + 
                              latency_score * 0.1)
                
                venue_scores[venue_id] = total_score
                
            # Select best venue
            if venue_scores:
                best_venue = max(venue_scores, key=venue_scores.get)
                
                return {
                    "recommended_venue": best_venue,
                    "confidence": venue_scores[best_venue],
                    "expected_slippage": slippage_estimate,
                    "liquidity_sufficient": available_liquidity >= order_size * 1.1,  # 10% buffer
                    "strategy": "aggressive_execution" if slippage_estimate < 0.01 else "patient_execution",
                    "all_venues_scores": venue_scores
                }
            else:
                return {
                    "error": "No venues available for execution",
                    "liquidity_sufficient": False
                }
                
        except Exception as e:
            logger.error(f"Error recommending execution strategy: {e}")
            return {"error": str(e)}
            
    def get_aggregation_statistics(self) -> Dict[str, Any]:
        """Get aggregation performance statistics"""
        if not self.liquidity_history:
            return {}
            
        # Calculate statistics
        recent_history = self.liquidity_history[-1000:]  # Last 1000 aggregations
        
        stats = {
            "total_aggregations": len(self.liquidity_history),
            "active_symbols": list(self.aggregated_books.keys()),
            "active_sources": list(self.liquidity_sources.keys()),
            "avg_sources_per_symbol": np.mean([h["total_sources"] for h in recent_history]) if recent_history else 0,
            "avg_filtered_sources": np.mean([h["filtered_sources"] for h in recent_history]) if recent_history else 0,
            "avg_spread_bps": np.mean([h["spread"] / h.get("mid_price", 1.0) * 10000 for h in recent_history if h.get("mid_price", 1.0) > 0]) if recent_history else 0,
            "venue_weights": self.venue_weights.copy(),
            "last_aggregation": self.liquidity_history[-1]["timestamp"] if self.liquidity_history else None
        }
        
        return stats


class ExchangeLiquiditySource:
    """Exchange liquidity source"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name", "Exchange")
        self.source_type = LiquiditySource.EXCHANGE
        self.reliability_score = config.get("reliability", 0.95)
        self.fee_structure = config.get("fees", {"maker_fee": 0.001, "taker_fee": 0.002})
        self.latency_ms = config.get("latency_ms", 10.0)
        
    async def get_order_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get order book from exchange"""
        # Simulate exchange order book
        return {
            "bids": [(100.0 - i*0.01, 1000.0 - i*100) for i in range(10)],
            "asks": [(100.0 + i*0.01, 1000.0 - i*100) for i in range(10)],
            "timestamp": datetime.now(),
            "latency_ms": self.latency_ms
        }


class DarkPoolLiquiditySource:
    """Dark pool liquidity source"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name", "Dark Pool")
        self.source_type = LiquiditySource.DARK_POOL
        self.reliability_score = config.get("reliability", 0.90)
        self.fee_structure = config.get("fees", {"maker_fee": 0.0005, "taker_fee": 0.001})
        self.latency_ms = config.get("latency_ms", 50.0)
        
    async def get_order_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get order book from dark pool"""
        # Simulate dark pool order book (less transparent)
        return {
            "bids": [(100.0 - i*0.005, 5000.0 - i*200) for i in range(5)],
            "asks": [(100.0 + i*0.005, 5000.0 - i*200) for i in range(5)],
            "timestamp": datetime.now(),
            "latency_ms": self.latency_ms
        }


class ECNLiquiditySource:
    """ECN liquidity source"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name", "ECN")
        self.source_type = LiquiditySource.ECN
        self.reliability_score = config.get("reliability", 0.92)
        self.fee_structure = config.get("fees", {"maker_fee": 0.0002, "taker_fee": 0.0008})
        self.latency_ms = config.get("latency_ms", 5.0)
        
    async def get_order_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get order book from ECN"""
        # Simulate ECN order book (fast but less liquidity)
        return {
            "bids": [(100.0 - i*0.002, 2000.0 - i*50) for i in range(5)],
            "asks": [(100.0 + i*0.002, 2000.0 - i*50) for i in range(5)],
            "timestamp": datetime.now(),
            "latency_ms": self.latency_ms
        }


class InternalLiquiditySource:
    """Internal liquidity source"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name", "Internal")
        self.source_type = LiquiditySource.INTERNAL
        self.reliability_score = config.get("reliability", 0.98)
        self.fee_structure = config.get("fees", {"maker_fee": 0.0, "taker_fee": 0.0})
        self.latency_ms = config.get("latency_ms", 1.0)
        
    async def get_order_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get order book from internal source"""
        # Simulate internal order book (no fees, very fast)
        return {
            "bids": [(100.0 - i*0.001, 5000.0 - i*25) for i in range(3)],
            "asks": [(100.0 + i*0.001, 5000.0 - i*25) for i in range(3)],
            "timestamp": datetime.now(),
            "latency_ms": self.latency_ms
        }


class ExternalLiquiditySource:
    """External liquidity source"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name", "External")
        self.source_type = LiquiditySource.EXTERNAL
        self.reliability_score = config.get("reliability", 0.85)
        self.fee_structure = config.get("fees", {"maker_fee": 0.0015, "taker_fee": 0.0025})
        self.latency_ms = config.get("latency_ms", 100.0)
        
    async def get_order_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get order book from external source"""
        # Simulate external order book (higher latency)
        return {
            "bids": [(100.0 - i*0.01, 3000.0 - i*100) for i in range(5)],
            "asks": [(100.0 + i*0.01, 3000.0 - i*100) for i in range(5)],
            "timestamp": datetime.now(),
            "latency_ms": self.latency_ms
        }


# Global liquidity aggregator instance
_liquidity_aggregator = None

def get_liquidity_aggregator() -> LiquidityAggregator:
    """Get the global liquidity aggregator instance"""
    global _liquidity_aggregator
    if _liquidity_aggregator is None:
        _liquidity_aggregator = LiquidityAggregator()
    return _liquidity_aggregator
