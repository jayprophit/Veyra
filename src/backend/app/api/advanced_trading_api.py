"""
Advanced Trading API Endpoints
=============================
Comprehensive advanced trading API for Financial Master
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from ..advanced_trading.trading_engine import get_trading_engine, AdvancedOrder, OrderSide, OrderType, OrderStatus
from ..advanced_trading.algorithmic_strategies import get_algorithmic_strategies, StrategyType
from ..advanced_trading.order_types import get_advanced_order_types, IcebergOrder, TWAPOrder, VWAPOrder
from ..advanced_trading.smart_order_routing import get_smart_order_routing, RoutingDecision
from ..advanced_trading.liquidity_aggregation import get_liquidity_aggregator
from ..advanced_trading.hft_engine import get_hft_engine, HFTStrategy

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced-trading", tags=["advanced-trading"])


# Trading Engine Endpoints
@router.post("/orders")
async def submit_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
    time_in_force: str = "GTC",
    strategy_params: Optional[Dict[str, Any]] = None
):
    """Submit advanced order"""
    try:
        trading_engine = get_trading_engine()
        
        order = AdvancedOrder(
            order_id=f"order_{datetime.now().timestamp()}",
            symbol=symbol,
            side=OrderSide(side),
            order_type=OrderType(order_type),
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
            strategy_params=strategy_params or {}
        )
        
        order_id = await trading_engine.submit_order(order)
        
        return {
            "order_id": order_id,
            "status": "submitted",
            "timestamp": datetime.now().isoformat(),
            "message": "Order submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/{order_id}")
async def get_order_status(order_id: str):
    """Get order status"""
    try:
        trading_engine = get_trading_engine()
        order = trading_engine.get_order_status(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
            
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "order_type": order.order_type.value,
            "quantity": order.quantity,
            "filled_quantity": order.filled_quantity,
            "average_price": order.average_price,
            "status": order.status.value,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/orders/{order_id}")
async def modify_order(
    order_id: str,
    modifications: Dict[str, Any]
):
    """Modify existing order"""
    try:
        trading_engine = get_trading_engine()
        success = await trading_engine.modify_order(order_id, modifications)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to modify order")
            
        return {
            "order_id": order_id,
            "status": "modified",
            "modifications": modifications,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancel order"""
    try:
        trading_engine = get_trading_engine()
        success = await trading_engine.cancel_order(order_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to cancel order")
            
        return {
            "order_id": order_id,
            "status": "cancelled",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def get_active_orders(
    symbol: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """Get active orders"""
    try:
        trading_engine = get_trading_engine()
        # This would need to be implemented in the trading engine
        return {
            "orders": [],
            "count": 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio")
async def get_portfolio():
    """Get portfolio summary"""
    try:
        trading_engine = get_trading_engine()
        portfolio = trading_engine.get_portfolio_summary()
        
        return {
            "portfolio": portfolio,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions/{symbol}")
async def get_position(symbol: str):
    """Get position for symbol"""
    try:
        trading_engine = get_trading_engine()
        position = trading_engine.get_position(symbol)
        
        return {
            "symbol": symbol,
            "position": position,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Algorithmic Trading Endpoints
@router.post("/strategies/{strategy_type}")
async def add_strategy(
    strategy_type: str,
    params: Optional[Dict[str, Any]] = None
):
    """Add algorithmic trading strategy"""
    try:
        algo_strategies = get_algorithmic_strategies()
        await algo_strategies.add_strategy(StrategyType(strategy_type), params)
        
        return {
            "strategy": strategy_type,
            "status": "added",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/strategies/{strategy_type}")
async def remove_strategy(strategy_type: str):
    """Remove algorithmic trading strategy"""
    try:
        algo_strategies = get_algorithmic_strategies()
        await algo_strategies.remove_strategy(StrategyType(strategy_type))
        
        return {
            "strategy": strategy_type,
            "status": "removed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def get_active_strategies():
    """Get active strategies"""
    try:
        algo_strategies = get_algorithmic_strategies()
        performance = algo_strategies.get_strategy_performance()
        
        return {
            "active_strategies": list(algo_strategies.active_strategies),
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategies/train")
async def train_ml_strategies(
    symbols: List[str]
):
    """Train ML strategies with historical data"""
    try:
        algo_strategies = get_algorithmic_strategies()
        # This would need historical data
        historical_data = {}  # Mock historical data
        
        await algo_strategies.train_ml_models(historical_data)
        
        return {
            "symbols": symbols,
            "status": "training_completed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals")
async def get_trading_signals(
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000)
):
    """Get trading signals from strategies"""
    try:
        algo_strategies = get_algorithmic_strategies()
        market_data = {}  # Mock market data
        
        signals = await algo_strategies.generate_signals(market_data)
        
        # Filter by symbol if specified
        if symbol:
            signals = [s for s in signals if s.symbol == symbol]
            
        return {
            "signals": [
                {
                    "strategy_name": signal.strategy_name,
                    "symbol": signal.symbol,
                    "action": signal.action,
                    "confidence": signal.confidence,
                    "price": signal.price,
                    "quantity": signal.quantity,
                    "timestamp": signal.timestamp.isoformat(),
                    "stop_loss": signal.stop_loss,
                    "take_profit": signal.take_profit,
                    "metadata": signal.metadata
                }
                for signal in signals[:limit]
            ],
            "count": len(signals[:limit]),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Advanced Order Types Endpoints
@router.post("/orders/iceberg")
async def create_iceberg_order(
    symbol: str,
    side: str,
    total_quantity: float,
    display_quantity: float,
    random_variation: bool = True,
    min_display: float = 100.0
):
    """Create iceberg order"""
    try:
        order_types = get_advanced_order_types()
        
        iceberg_config = IcebergOrder(
            total_quantity=total_quantity,
            display_quantity=display_quantity,
            random_variation=random_variation,
            min_display=min_display
        )
        
        order_id = await order_types.create_iceberg_order(symbol, side, iceberg_config)
        
        return {
            "order_id": order_id,
            "type": "iceberg",
            "config": {
                "total_quantity": total_quantity,
                "display_quantity": display_quantity,
                "random_variation": random_variation,
                "min_display": min_display
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders/twap")
async def create_twap_order(
    symbol: str,
    side: str,
    total_quantity: float,
    duration_minutes: int,
    num_slices: int,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """Create TWAP order"""
    try:
        order_types = get_advanced_order_types()
        
        twap_config = TWAPOrder(
            total_quantity=total_quantity,
            duration_minutes=duration_minutes,
            num_slices=num_slices,
            start_time=datetime.fromisoformat(start_time) if start_time else None,
            end_time=datetime.fromisoformat(end_time) if end_time else None
        )
        
        order_id = await order_types.create_twap_order(symbol, side, twap_config)
        
        return {
            "order_id": order_id,
            "type": "twap",
            "config": {
                "total_quantity": total_quantity,
                "duration_minutes": duration_minutes,
                "num_slices": num_slices,
                "start_time": start_time,
                "end_time": end_time
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders/vwap")
async def create_vwap_order(
    symbol: str,
    side: str,
    total_quantity: float,
    duration_minutes: int,
    num_slices: int,
    volume_profile: str = "uniform"
):
    """Create VWAP order"""
    try:
        order_types = get_advanced_order_types()
        
        vwap_config = VWAPOrder(
            total_quantity=total_quantity,
            duration_minutes=duration_minutes,
            num_slices=num_slices,
            volume_profile=volume_profile
        )
        
        order_id = await order_types.create_vwap_order(symbol, side, vwap_config)
        
        return {
            "order_id": order_id,
            "type": "vwap",
            "config": {
                "total_quantity": total_quantity,
                "duration_minutes": duration_minutes,
                "num_slices": num_slices,
                "volume_profile": volume_profile
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Smart Order Routing Endpoints
@router.post("/routing/optimize")
async def optimize_order_routing(
    symbol: str,
    side: str,
    quantity: float,
    order_type: str = "market",
    price: Optional[float] = None
):
    """Get optimal routing for order"""
    try:
        smart_routing = get_smart_order_routing()
        
        order = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "price": price
        }
        
        routing_decision = await smart_routing.route_order(order)
        
        return {
            "routing_decision": {
                "venue_id": routing_decision.venue_id,
                "venue_name": routing_decision.venue_name,
                "order_size": routing_decision.order_size,
                "expected_fill_rate": routing_decision.expected_fill_rate,
                "expected_cost": routing_decision.expected_cost,
                "expected_slippage": routing_decision.expected_slippage,
                "confidence": routing_decision.confidence,
                "routing_reason": routing_decision.routing_reason,
                "alternative_venues": routing_decision.alternative_venues
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routing/performance")
async def get_routing_performance():
    """Get routing performance metrics"""
    try:
        smart_routing = get_smart_order_routing()
        performance = smart_routing.get_routing_performance()
        
        return {
            "venue_performance": performance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/routing/split")
async def split_large_order(
    symbol: str,
    side: str,
    quantity: float,
    order_type: str = "market",
    price: Optional[float] = None
):
    """Split large order across venues"""
    try:
        smart_routing = get_smart_order_routing()
        
        order = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "price": price
        }
        
        split_orders = await smart_routing.split_large_order(order)
        
        return {
            "split_orders": [
                {
                    "venue": order.get("routing_venue", "unknown"),
                    "quantity": order.get("quantity", 0),
                    "order_type": order.get("order_type", "market")
                }
                for order in split_orders
            ],
            "original_order_size": quantity,
            "split_count": len(split_orders),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Liquidity Aggregation Endpoints
@router.post("/liquidity/aggregate/{symbol}")
async def aggregate_liquidity(symbol: str):
    """Aggregate liquidity for symbol"""
    try:
        liquidity_aggregator = get_liquidity_aggregator()
        aggregated_book = await liquidity_aggregator.aggregate_liquidity(symbol)
        
        return {
            "symbol": symbol,
            "aggregated_book": {
                "best_bid": aggregated_book.best_bid,
                "best_ask": aggregated_book.best_ask,
                "spread": aggregated_book.spread,
                "mid_price": aggregated_book.mid_price,
                "total_bid_size": aggregated_book.total_bid_size,
                "total_ask_size": aggregated_book.total_ask_size,
                "venue_contributions": aggregated_book.venue_contributions,
                "data_sources": aggregated_book.data_sources
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liquidity/optimal/{symbol}")
async def get_optimal_execution_plan(
    symbol: str,
    order_size: float,
    order_side: str
):
    """Get optimal execution plan"""
    try:
        liquidity_aggregator = get_liquidity_aggregator()
        plan = await liquidity_aggregator.get_optimal_execution_plan(symbol, order_size, order_side)
        
        return {
            "execution_plan": plan,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liquidity/statistics")
async def get_liquidity_statistics():
    """Get liquidity aggregation statistics"""
    try:
        liquidity_aggregator = get_liquidity_aggregator()
        stats = liquidity_aggregator.get_aggregation_statistics()
        
        return {
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# High-Frequency Trading Endpoints
@router.post("/hft/start")
async def start_hft_engine():
    """Start HFT engine"""
    try:
        hft_engine = get_hft_engine()
        await hft_engine.start()
        
        return {
            "status": "started",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hft/stop")
async def stop_hft_engine():
    """Stop HFT engine"""
    try:
        hft_engine = get_hft_engine()
        hft_engine.stop()
        
        return {
            "status": "stopped",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hft/performance")
async def get_hft_performance():
    """Get HFT performance metrics"""
    try:
        hft_engine = get_hft_engine()
        performance = hft_engine.get_performance_report()
        
        return {
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hft/market-makers/{symbol}")
async def add_market_maker(
    symbol: str,
    spread_bps: float = 5.0,
    inventory_limit: float = 10000.0
):
    """Add market maker for symbol"""
    try:
        hft_engine = get_hft_engine()
        hft_engine.add_market_maker(symbol, spread_bps, inventory_limit)
        
        return {
            "symbol": symbol,
            "status": "added",
            "spread_bps": spread_bps,
            "inventory_limit": inventory_limit,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Advanced Trading Dashboard
@router.get("/dashboard")
async def get_advanced_trading_dashboard():
    """Get comprehensive advanced trading dashboard"""
    try:
        trading_engine = get_trading_engine()
        algo_strategies = get_algorithmic_strategies()
        smart_routing = get_smart_order_routing()
        liquidity_aggregator = get_liquidity_aggregator()
        hft_engine = get_hft_engine()
        
        # Get all metrics
        portfolio = trading_engine.get_portfolio_summary()
        active_orders = trading_engine.get_active_orders()
        strategy_performance = algo_strategies.get_strategy_performance()
        routing_performance = smart_routing.get_routing_performance()
        liquidity_stats = liquidity_aggregator.get_aggregation_statistics()
        hft_performance = hft_engine.get_performance_report()
        
        return {
            "portfolio": portfolio,
            "active_orders": active_orders,
            "strategy_performance": strategy_performance,
            "routing_performance": routing_performance,
            "liquidity_statistics": liquidity_stats,
            "hft_performance": hft_performance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
