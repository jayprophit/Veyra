"""
Smart Order Routing
==================
Intelligent order routing for optimal execution across multiple venues
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


class VenueType(Enum):
    """Trading venue types"""
    EXCHANGE = "exchange"
    DARK_POOL = "dark_pool"
    ECN = "ecn"  # Electronic Communication Network
    INTERNAL = "internal"
    BROKER = "broker"


class OrderPriority(Enum):
    """Order priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Venue:
    """Trading venue information"""
    venue_id: str
    name: str
    venue_type: VenueType
    fees: Dict[str, float]  # maker_fee, taker_fee
    liquidity: float  # 0-1 scale
    speed: float  # execution speed 0-1
    min_order_size: float
    max_order_size: float
    supported_order_types: List[str]
    market_data_delay: float  # milliseconds
    reliability: float  # 0-1 scale
    cost_benefit_ratio: float


@dataclass
class RoutingDecision:
    """Smart order routing decision"""
    venue_id: str
    venue_name: str
    order_size: float
    expected_fill_rate: float
    expected_cost: float
    expected_slippage: float
    confidence: float
    routing_reason: str
    alternative_venues: List[Dict[str, Any]]


class SmartOrderRouting:
    """Smart order routing system"""
    
    def __init__(self):
        self.venues: Dict[str, Venue] = {}
        self.routing_history: List[Dict] = []
        self.market_conditions: Dict[str, Dict] = {}
        self.liquidity_tracker = LiquidityTracker()
        self.cost_analyzer = CostAnalyzer()
        
        # Initialize default venues
        self._initialize_venues()
        
    def _initialize_venues(self):
        """Initialize default trading venues"""
        # Major exchanges
        self.venues["NYSE"] = Venue(
            venue_id="NYSE",
            name="New York Stock Exchange",
            venue_type=VenueType.EXCHANGE,
            fees={"maker_fee": 0.001, "taker_fee": 0.002},
            liquidity=0.95,
            speed=0.85,
            min_order_size=1.0,
            max_order_size=1000000.0,
            supported_order_types=["market", "limit", "stop", "iceberg"],
            market_data_delay=10.0,
            reliability=0.98,
            cost_benefit_ratio=0.92
        )
        
        self.venues["NASDAQ"] = Venue(
            venue_id="NASDAQ",
            name="NASDAQ Stock Market",
            venue_type=VenueType.EXCHANGE,
            fees={"maker_fee": 0.0008, "taker_fee": 0.0015},
            liquidity=0.93,
            speed=0.90,
            min_order_size=1.0,
            max_order_size=1000000.0,
            supported_order_types=["market", "limit", "stop", "iceberg", "twap"],
            market_data_delay=8.0,
            reliability=0.97,
            cost_benefit_ratio=0.94
        )
        
        # Dark pools
        self.venues["DARK_POOL_1"] = Venue(
            venue_id="DARK_POOL_1",
            name="Institutional Dark Pool",
            venue_type=VenueType.DARK_POOL,
            fees={"maker_fee": 0.0005, "taker_fee": 0.001},
            liquidity=0.75,
            speed=0.70,
            min_order_size=10000.0,
            max_order_size=5000000.0,
            supported_order_types=["limit", "iceberg", "twap"],
            market_data_delay=50.0,
            reliability=0.95,
            cost_benefit_ratio=0.88
        )
        
        # ECNs
        self.venues["ECN_1"] = Venue(
            venue_id="ECN_1",
            name="Electronic Communication Network",
            venue_type=VenueType.ECN,
            fees={"maker_fee": 0.0002, "taker_fee": 0.0008},
            liquidity=0.85,
            speed=0.95,
            min_order_size=1.0,
            max_order_size=100000.0,
            supported_order_types=["market", "limit", "iceberg"],
            market_data_delay=5.0,
            reliability=0.96,
            cost_benefit_ratio=0.91
        )
        
    async def route_order(self, order: Dict[str, Any]) -> RoutingDecision:
        """Route order to optimal venue"""
        try:
            # Get eligible venues
            eligible_venues = self._get_eligible_venues(order)
            
            if not eligible_venues:
                return RoutingDecision(
                    venue_id="",
                    venue_name="No eligible venues",
                    order_size=order.get("quantity", 0),
                    expected_fill_rate=0.0,
                    expected_cost=0.0,
                    expected_slippage=0.0,
                    confidence=0.0,
                    routing_reason="No eligible venues for order",
                    alternative_venues=[]
                )
            
            # Analyze market conditions
            market_conditions = await self._get_market_conditions(order["symbol"])
            
            # Score venues
            venue_scores = []
            for venue in eligible_venues:
                score = await self._score_venue(venue, order, market_conditions)
                venue_scores.append((venue, score))
            
            # Sort by score
            venue_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select best venue
            best_venue, best_score = venue_scores[0]
            
            # Calculate routing metrics
            expected_fill_rate = self._calculate_fill_rate(best_venue, order, market_conditions)
            expected_cost = self.cost_analyzer.calculate_total_cost(best_venue, order)
            expected_slippage = self._calculate_slippage(best_venue, order, market_conditions)
            
            # Prepare alternatives
            alternatives = []
            for venue, score in venue_scores[1:4]:  # Top 3 alternatives
                alternatives.append({
                    "venue_id": venue.venue_id,
                    "venue_name": venue.name,
                    "score": score,
                    "expected_fill_rate": self._calculate_fill_rate(venue, order, market_conditions),
                    "expected_cost": self.cost_analyzer.calculate_total_cost(venue, order)
                })
            
            routing_decision = RoutingDecision(
                venue_id=best_venue.venue_id,
                venue_name=best_venue.name,
                order_size=order.get("quantity", 0),
                expected_fill_rate=expected_fill_rate,
                expected_cost=expected_cost,
                expected_slippage=expected_slippage,
                confidence=min(best_score * 100, 95),
                routing_reason=self._get_routing_reason(best_venue, order, market_conditions),
                alternative_venues=alternatives
            )
            
            # Record routing decision
            self.routing_history.append({
                "timestamp": datetime.now(),
                "order": order,
                "decision": routing_decision,
                "market_conditions": market_conditions
            })
            
            logger.info(f"Order routed to {best_venue.name} with confidence {routing_decision.confidence:.2f}%")
            
            return routing_decision
            
        except Exception as e:
            logger.error(f"Error routing order: {e}")
            raise
            
    def _get_eligible_venues(self, order: Dict[str, Any]) -> List[Venue]:
        """Get venues eligible for order"""
        eligible = []
        order_type = order.get("order_type", "market")
        order_size = order.get("quantity", 0)
        
        for venue in self.venues.values():
            # Check order type support
            if order_type not in venue.supported_order_types:
                continue
                
            # Check order size limits
            if order_size < venue.min_order_size or order_size > venue.max_order_size:
                continue
                
            eligible.append(venue)
            
        return eligible
        
    async def _get_market_conditions(self, symbol: str) -> Dict[str, Any]:
        """Get current market conditions"""
        # Check if we have recent data
        if symbol in self.market_conditions:
            last_update = self.market_conditions[symbol].get("timestamp")
            if last_update and (datetime.now() - last_update).seconds < 60:
                return self.market_conditions[symbol]
        
        # Simulate market conditions (in production, would get from market data)
        conditions = {
            "symbol": symbol,
            "timestamp": datetime.now(),
            "volatility": np.random.uniform(0.1, 0.3),
            "volume": np.random.uniform(1000000, 10000000),
            "spread": np.random.uniform(0.01, 0.05),
            "trend": np.random.choice(["bullish", "bearish", "sideways"]),
            "liquidity_score": np.random.uniform(0.7, 1.0),
            "market_impact": np.random.uniform(0.001, 0.01)
        }
        
        self.market_conditions[symbol] = conditions
        return conditions
        
    async def _score_venue(self, venue: Venue, order: Dict[str, Any], 
                          market_conditions: Dict[str, Any]) -> float:
        """Score venue for order routing"""
        try:
            score = 0.0
            
            # Liquidity score (30% weight)
            liquidity_score = venue.liquidity * market_conditions["liquidity_score"]
            score += liquidity_score * 0.30
            
            # Cost score (25% weight)
            total_cost = self.cost_analyzer.calculate_total_cost(venue, order)
            cost_score = max(0, 1.0 - total_cost / 0.01)  # Normalize to 0-1
            score += cost_score * 0.25
            
            # Speed score (20% weight)
            speed_score = venue.speed * (1.0 - market_conditions["volatility"] / 0.5)
            score += speed_score * 0.20
            
            # Reliability score (15% weight)
            reliability_score = venue.reliability
            score += reliability_score * 0.15
            
            # Fill rate score (10% weight)
            fill_rate = self._calculate_fill_rate(venue, order, market_conditions)
            fill_rate_score = min(fill_rate, 1.0)
            score += fill_rate_score * 0.10
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring venue: {e}")
            return 0.0
            
    def _calculate_fill_rate(self, venue: Venue, order: Dict[str, Any], 
                          market_conditions: Dict[str, Any]) -> float:
        """Calculate expected fill rate"""
        base_fill_rate = venue.reliability * 0.95  # Base reliability
        
        # Adjust for market conditions
        volatility_factor = max(0.5, 1.0 - market_conditions["volatility"])
        liquidity_factor = market_conditions["liquidity_score"]
        
        # Adjust for order type
        order_type = order.get("order_type", "market")
        if order_type == "market":
            order_type_factor = 1.0
        elif order_type == "limit":
            order_type_factor = 0.8
        else:  # advanced order types
            order_type_factor = 0.7
            
        fill_rate = base_fill_rate * volatility_factor * liquidity_factor * order_type_factor
        
        return min(fill_rate, 1.0)
        
    def _calculate_slippage(self, venue: Venue, order: Dict[str, Any], 
                          market_conditions: Dict[str, Any]) -> float:
        """Calculate expected slippage"""
        base_slippage = market_conditions["spread"] / 2  # Half spread
        
        # Adjust for venue speed
        speed_factor = 1.0 - venue.speed * 0.3  # Faster venues have less slippage
        
        # Adjust for order size
        order_size = order.get("quantity", 0)
        size_factor = min(1.0, order_size / 10000.0)  # Larger orders have more slippage
        
        # Adjust for market volatility
        volatility_factor = market_conditions["volatility"]
        
        slippage = base_slippage * speed_factor * size_factor * volatility_factor
        
        return slippage
        
    def _get_routing_reason(self, venue: Venue, order: Dict[str, Any], 
                         market_conditions: Dict[str, Any]) -> str:
        """Get routing reason explanation"""
        reasons = []
        
        if venue.liquidity > 0.9:
            reasons.append("High liquidity")
            
        if venue.speed > 0.9:
            reasons.append("Fast execution")
            
        if venue.fees["taker_fee"] < 0.001:
            reasons.append("Low fees")
            
        if market_conditions["liquidity_score"] > 0.8:
            reasons.append("Favorable market conditions")
            
        if venue.reliability > 0.95:
            reasons.append("High reliability")
            
        return ", ".join(reasons) if reasons else "Optimal venue selection"
        
    async def split_large_order(self, order: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split large orders across multiple venues"""
        try:
            order_size = order.get("quantity", 0)
            max_single_venue = 100000.0  # Max size per venue
            
            if order_size <= max_single_venue:
                return [order]
                
            # Get eligible venues
            eligible_venues = self._get_eligible_venues(order)
            
            if len(eligible_venues) == 0:
                return [order]
                
            # Calculate split ratios based on venue liquidity
            total_liquidity = sum(v.liquidity for v in eligible_venues)
            splits = []
            
            remaining_size = order_size
            
            for venue in eligible_venues[:-1]:  # All but last
                split_ratio = venue.liquidity / total_liquidity
                split_size = min(remaining_size * split_ratio, venue.max_order_size)
                
                if split_size > 0:
                    split_order = order.copy()
                    split_order["quantity"] = split_size
                    split_order["routing_venue"] = venue.venue_id
                    splits.append(split_order)
                    remaining_size -= split_size
                    
            # Put remaining in last venue
            if remaining_size > 0:
                last_venue = eligible_venues[-1]
                split_order = order.copy()
                split_order["quantity"] = remaining_size
                split_order["routing_venue"] = last_venue.venue_id
                splits.append(split_order)
                
            logger.info(f"Order split into {len(splits)} venues")
            return splits
            
        except Exception as e:
            logger.error(f"Error splitting order: {e}")
            return [order]
            
    def get_routing_performance(self) -> Dict[str, Any]:
        """Get routing performance metrics"""
        if not self.routing_history:
            return {}
            
        # Analyze routing history
        venue_performance = {}
        
        for routing in self.routing_history[-1000:]:  # Last 1000 routings
            venue_id = routing["decision"].venue_id
            if venue_id not in venue_performance:
                venue_performance[venue_id] = {
                    "count": 0,
                    "avg_fill_rate": 0.0,
                    "avg_cost": 0.0,
                    "avg_slippage": 0.0
                }
                
            perf = venue_performance[venue_id]
            perf["count"] += 1
            perf["avg_fill_rate"] += routing["decision"].expected_fill_rate
            perf["avg_cost"] += routing["decision"].expected_cost
            perf["avg_slippage"] += routing["decision"].expected_slippage
            
        # Calculate averages
        for venue_id, perf in venue_performance.items():
            if perf["count"] > 0:
                perf["avg_fill_rate"] /= perf["count"]
                perf["avg_cost"] /= perf["count"]
                perf["avg_slippage"] /= perf["count"]
                
        return venue_performance
        
    def update_venue_performance(self, venue_id: str, execution_result: Dict[str, Any]):
        """Update venue performance based on execution results"""
        try:
            venue = self.venues.get(venue_id)
            if not venue:
                return
                
            # Update venue metrics based on actual execution
            actual_fill_rate = execution_result.get("fill_rate", 0.0)
            actual_cost = execution_result.get("total_cost", 0.0)
            actual_slippage = execution_result.get("slippage", 0.0)
            
            # Exponential moving average update
            alpha = 0.1  # Smoothing factor
            
            # Update liquidity estimate
            if actual_fill_rate > 0.8:
                venue.liquidity = min(1.0, venue.liquidity * (1 + alpha * 0.01))
            else:
                venue.liquidity = max(0.1, venue.liquidity * (1 - alpha * 0.02))
                
            # Update speed estimate
            execution_time = execution_result.get("execution_time_ms", 100.0)
            if execution_time < 50:  # Fast execution
                venue.speed = min(1.0, venue.speed * (1 + alpha * 0.01))
            else:
                venue.speed = max(0.1, venue.speed * (1 - alpha * 0.01))
                
            # Update reliability
            if execution_result.get("success", False):
                venue.reliability = min(1.0, venue.reliability * (1 + alpha * 0.005))
            else:
                venue.reliability = max(0.5, venue.reliability * (1 - alpha * 0.01))
                
            logger.info(f"Updated venue performance for {venue_id}")
            
        except Exception as e:
            logger.error(f"Error updating venue performance: {e}")


class LiquidityTracker:
    """Track liquidity across venues"""
    
    def __init__(self):
        self.liquidity_history: Dict[str, List] = defaultdict(list)
        
    def update_liquidity(self, venue_id: str, symbol: str, liquidity: float):
        """Update liquidity data"""
        self.liquidity_history[f"{venue_id}_{symbol}"].append({
            "timestamp": datetime.now(),
            "liquidity": liquidity
        })
        
        # Keep only last 1000 data points
        if len(self.liquidity_history[f"{venue_id}_{symbol}"]) > 1000:
            self.liquidity_history[f"{venue_id}_{symbol}"] = self.liquidity_history[f"{venue_id}_{symbol}"][-1000:]


class CostAnalyzer:
    """Analyze trading costs across venues"""
    
    def calculate_total_cost(self, venue: Venue, order: Dict[str, Any]) -> float:
        """Calculate total trading cost"""
        try:
            order_value = order.get("quantity", 0) * order.get("price", 100.0)
            order_type = order.get("order_type", "market")
            
            # Trading fees
            if order_type in ["market", "stop"]:
                fee = order_value * venue.fees["taker_fee"]
            else:
                fee = order_value * venue.fees["maker_fee"]
                
            # Market impact cost (simplified)
            market_impact = self._calculate_market_impact(venue, order)
            
            # Opportunity cost (simplified)
            opportunity_cost = venue.market_data_delay / 1000.0 * 0.001  # $0.001 per second
            
            total_cost = fee + market_impact + opportunity_cost
            
            return total_cost
            
        except Exception as e:
            logger.error(f"Error calculating cost: {e}")
            return 0.0
            
    def _calculate_market_impact(self, venue: Venue, order: Dict[str, Any]) -> float:
        """Calculate market impact cost"""
        order_size = order.get("quantity", 0)
        avg_daily_volume = 10000000.0  # Mock daily volume
        
        # Market impact model
        impact_ratio = (order_size / avg_daily_volume) ** 0.5
        market_impact = impact_ratio * 0.01  # 1% base impact
        
        return market_impact


# Global smart order routing instance
_smart_order_routing = None

def get_smart_order_routing() -> SmartOrderRouting:
    """Get the global smart order routing instance"""
    global _smart_order_routing
    if _smart_order_routing is None:
        _smart_order_routing = SmartOrderRouting()
    return _smart_order_routing
