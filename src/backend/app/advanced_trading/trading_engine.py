"""
Advanced Trading Engine
======================
High-frequency trading with advanced order types and execution strategies
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Advanced order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    PEGGED = "pegged"
    RESERVE = "reserve"
    TRAILING_STOP = "trailing_stop"
    OCO = "oco"  # One-Cancels-Other
    IFD = "ifd"  # If-Done
class OrderSide(Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"
    
class OrderStatus(Enum):
    """Order status"""
    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class AdvancedOrder:
    """Advanced order structure"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"
    created_at: datetime = None
    updated_at: datetime = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_price: float = 0.0
    commission: float = 0.0
    strategy_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.strategy_params is None:
            self.strategy_params = {}


class AdvancedTradingEngine:
    """Advanced trading engine with high-frequency capabilities"""
    
    def __init__(self):
        self.orders: Dict[str, AdvancedOrder] = {}
        self.order_book: Dict[str, Dict] = defaultdict(lambda: {"bids": [], "asks": []})
        self.trades: List[Dict] = []
        self.market_data: Dict[str, Dict] = {}
        self.position_manager = PositionManager()
        self.risk_manager = RiskManager()
        self.execution_engine = ExecutionEngine()
        
    async def submit_order(self, order: AdvancedOrder) -> str:
        """Submit order for execution"""
        try:
            # Risk check
            risk_check = await self.risk_manager.validate_order(order)
            if not risk_check.approved:
                order.status = OrderStatus.REJECTED
                return f"Order rejected: {risk_check.reason}"
                
            # Store order
            self.orders[order.order_id] = order
            
            # Route to execution engine
            await self.execution_engine.execute_order(order, self.order_book[order.symbol])
            
            logger.info(f"Order submitted: {order.order_id} - {order.side.value} {order.quantity} {order.symbol}")
            return order.order_id
            
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            raise
            
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        try:
            order = self.orders.get(order_id)
            if not order:
                return False
                
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
                return False
                
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.now()
            
            # Remove from order book
            await self.execution_engine.cancel_order(order_id)
            
            logger.info(f"Order cancelled: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
            
    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> bool:
        """Modify existing order"""
        try:
            order = self.orders.get(order_id)
            if not order:
                return False
                
            if order.status not in [OrderStatus.PENDING, OrderStatus.PARTIAL]:
                return False
                
            # Cancel original order
            await self.cancel_order(order_id)
            
            # Create new order with modifications
            new_order = AdvancedOrder(
                order_id=str(uuid.uuid4()),
                symbol=order.symbol,
                side=order.side,
                order_type=modifications.get('order_type', order.order_type),
                quantity=modifications.get('quantity', order.quantity),
                price=modifications.get('price', order.price),
                stop_price=modifications.get('stop_price', order.stop_price),
                strategy_params=modifications.get('strategy_params', order.strategy_params)
            )
            
            await self.submit_order(new_order)
            
            logger.info(f"Order modified: {order_id} -> {new_order.order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error modifying order: {e}")
            return False
            
    def get_order_status(self, order_id: str) -> Optional[AdvancedOrder]:
        """Get order status"""
        return self.orders.get(order_id)
        
    def get_position(self, symbol: str) -> Dict[str, float]:
        """Get current position"""
        return self.position_manager.get_position(symbol)
        
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary"""
        return {
            "total_value": self.position_manager.get_total_value(),
            "positions": self.position_manager.get_all_positions(),
            "cash": self.position_manager.get_cash_balance(),
            "margin": self.position_manager.get_margin_usage(),
            "pnl": self.position_manager.get_total_pnl()
        }
        
    async def process_market_data(self, symbol: str, data: Dict[str, Any]):
        """Process market data updates"""
        try:
            self.market_data[symbol] = data
            
            # Update order book
            if 'bids' in data and 'asks' in data:
                self.order_book[symbol]["bids"] = data['bids']
                self.order_book[symbol]["asks"] = data['asks']
                
            # Trigger order matching
            await self.execution_engine.match_orders(symbol, self.order_book[symbol])
            
            # Update positions
            self.position_manager.update_market_data(symbol, data)
            
        except Exception as e:
            logger.error(f"Error processing market data: {e}")


class PositionManager:
    """Position management system"""
    
    def __init__(self):
        self.positions: Dict[str, Dict] = defaultdict(lambda: {
            "quantity": 0.0,
            "average_price": 0.0,
            "unrealized_pnl": 0.0,
            "realized_pnl": 0.0
        })
        self.cash_balance = 1000000.0  # Starting cash
        
    def update_position(self, symbol: str, quantity: float, price: float):
        """Update position after trade"""
        position = self.positions[symbol]
        
        if position["quantity"] == 0:
            position["average_price"] = price
        else:
            # Calculate new average price
            total_cost = position["quantity"] * position["average_price"]
            new_cost = quantity * price
            total_quantity = position["quantity"] + quantity
            
            position["average_price"] = (total_cost + new_cost) / total_quantity
            
        position["quantity"] += quantity
        
        # Update cash
        self.cash_balance -= quantity * price
        
    def get_position(self, symbol: str) -> Dict[str, float]:
        """Get position details"""
        return dict(self.positions.get(symbol, {
            "quantity": 0.0,
            "average_price": 0.0,
            "unrealized_pnl": 0.0,
            "realized_pnl": 0.0
        }))
        
    def get_all_positions(self) -> Dict[str, Dict]:
        """Get all positions"""
        return dict(self.positions)
        
    def get_cash_balance(self) -> float:
        """Get cash balance"""
        return self.cash_balance
        
    def get_total_value(self) -> float:
        """Get total portfolio value"""
        total = self.cash_balance
        for symbol, position in self.positions.items():
            if position["quantity"] != 0:
                # Add position value (simplified)
                total += position["quantity"] * position["average_price"]
        return total
        
    def get_margin_usage(self) -> float:
        """Get margin usage"""
        # Simplified margin calculation
        total_value = self.get_total_value()
        return (total_value - self.cash_balance) / total_value if total_value > 0 else 0
        
    def get_total_pnl(self) -> float:
        """Get total P&L"""
        total = 0.0
        for position in self.positions.values():
            total += position["realized_pnl"] + position["unrealized_pnl"]
        return total
        
    def update_market_data(self, symbol: str, data: Dict[str, Any]):
        """Update position with market data"""
        if symbol in self.positions and 'last_price' in data:
            position = self.positions[symbol]
            if position["quantity"] != 0:
                # Calculate unrealized P&L
                current_price = data['last_price']
                position["unrealized_pnl"] = position["quantity"] * (
                    current_price - position["average_price"]
                )


class RiskManager:
    """Risk management system"""
    
    def __init__(self):
        self.max_position_size = 1000000.0
        self.max_order_size = 100000.0
        self.max_leverage = 5.0
        self.var_limit = 50000.0
        
    async def validate_order(self, order: AdvancedOrder) -> 'RiskCheckResult':
        """Validate order against risk limits"""
        try:
            # Check order size
            if order.quantity > self.max_order_size:
                return RiskCheckResult(False, f"Order size {order.quantity} exceeds limit {self.max_order_size}")
                
            # Check position size (simplified)
            if order.quantity * (order.price or 0) > self.max_position_size:
                return RiskCheckResult(False, "Position size exceeds limit")
                
            # Check leverage (simplified)
            if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
                # Additional checks for leveraged orders
                pass
                
            return RiskCheckResult(True, "Order approved")
            
        except Exception as e:
            logger.error(f"Risk validation error: {e}")
            return RiskCheckResult(False, f"Risk validation failed: {str(e)}")


@dataclass
class RiskCheckResult:
    """Risk check result"""
    approved: bool
    reason: str


class ExecutionEngine:
    """Order execution engine"""
    
    def __init__(self):
        self.execution_algorithms = {
            OrderType.TWAP: self._execute_twap,
            OrderType.VWAP: self._execute_vwap,
            OrderType.ICEBERG: self._execute_iceberg,
            OrderType.MARKET: self._execute_market,
            OrderType.LIMIT: self._execute_limit
        }
        
    async def execute_order(self, order: AdvancedOrder, order_book: Dict):
        """Execute order using appropriate algorithm"""
        try:
            algorithm = self.execution_algorithms.get(order.order_type)
            if algorithm:
                await algorithm(order, order_book)
            else:
                await self._execute_default(order, order_book)
                
        except Exception as e:
            logger.error(f"Execution error: {e}")
            order.status = OrderStatus.REJECTED
            
    async def cancel_order(self, order_id: str) -> dict:
        """Cancel order execution"""
        try:
            # Find the order in active orders
            if order_id not in self.active_orders:
                raise ValueError(f"Order {order_id} not found")
            
            order = self.active_orders[order_id]
            
            # Check if order can be cancelled (not already filled or cancelled)
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
                return {
                    "success": False,
                    "order_id": order_id,
                    "status": order.status.value,
                    "message": f"Order cannot be cancelled - current status: {order.status.value}"
                }
            
            # Update order status
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.now()
            
            # Remove from active orders
            del self.active_orders[order_id]
            
            # Log the cancellation
            logger.info(f"Order {order_id} cancelled successfully")
            
            return {
                "success": True,
                "order_id": order_id,
                "status": "CANCELLED",
                "cancelled_at": order.updated_at.isoformat(),
                "message": "Order cancelled successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return {
                "success": False,
                "order_id": order_id,
                "error": str(e),
                "message": "Order cancellation failed"
            }
        
    async def match_orders(self, symbol: str, order_book: Dict) -> dict:
        """Match orders in order book"""
        try:
            # Separate buy and sell orders
            buy_orders = [order for order in order_book.values() 
                         if order.side == OrderSide.BUY and order.status == OrderStatus.PENDING]
            sell_orders = [order for order in order_book.values() 
                          if order.side == OrderSide.SELL and order.status == OrderStatus.PENDING]
            
            # Sort orders: buy orders by price descending, sell orders by price ascending
            buy_orders.sort(key=lambda x: x.price, reverse=True)
            sell_orders.sort(key=lambda x: x.price)
            
            matches = []
            total_volume = 0
            
            # Match orders
            for buy_order in buy_orders:
                for sell_order in sell_orders:
                    # Check if orders can match
                    if buy_order.price >= sell_order.price:
                        # Calculate match quantity
                        match_quantity = min(buy_order.quantity - buy_order.filled_quantity,
                                           sell_order.quantity - sell_order.filled_quantity)
                        
                        if match_quantity > 0:
                            # Create match
                            match_price = (buy_order.price + sell_order.price) / 2  # Mid-price
                            
                            match = {
                                "buy_order_id": buy_order.order_id,
                                "sell_order_id": sell_order.order_id,
                                "symbol": symbol,
                                "quantity": match_quantity,
                                "price": match_price,
                                "timestamp": datetime.now().isoformat()
                            }
                            
                            matches.append(match)
                            total_volume += match_quantity
                            
                            # Update order filled quantities
                            buy_order.filled_quantity += match_quantity
                            sell_order.filled_quantity += match_quantity
                            
                            # Update order statuses
                            if buy_order.filled_quantity >= buy_order.quantity:
                                buy_order.status = OrderStatus.FILLED
                            else:
                                buy_order.status = OrderStatus.PARTIAL
                                
                            if sell_order.filled_quantity >= sell_order.quantity:
                                sell_order.status = OrderStatus.FILLED
                            else:
                                sell_order.status = OrderStatus.PARTIAL
                            
                            # Update timestamps
                            buy_order.updated_at = datetime.now()
                            sell_order.updated_at = datetime.now()
            
            logger.info(f"Order matching completed for {symbol}: {len(matches)} matches, {total_volume} total volume")
            
            return {
                "success": True,
                "symbol": symbol,
                "matches": len(matches),
                "total_volume": total_volume,
                "details": matches,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Order matching failed for {symbol}: {e}")
            return {
                "success": False,
                "symbol": symbol,
                "error": str(e),
                "message": "Order matching failed"
            }
        
    async def _execute_twap(self, order: AdvancedOrder, order_book: Dict):
        """Execute TWAP (Time-Weighted Average Price) order"""
        # TWAP implementation
        duration = order.strategy_params.get('duration', 3600)  # 1 hour default
        slice_count = order.strategy_params.get('slices', 12)
        slice_size = order.quantity / slice_count
        slice_interval = duration / slice_count
        
        for i in range(slice_count):
            # Execute slice
            await self._execute_market_slice(order, slice_size)
            await asyncio.sleep(slice_interval)
            
    async def _execute_vwap(self, order: AdvancedOrder, order_book: Dict):
        """Execute VWAP (Volume-Weighted Average Price) order"""
        try:
            # Get VWAP parameters
            lookback_periods = order.strategy_params.get('lookback_periods', 20)
            participation_rate = order.strategy_params.get('participation_rate', 0.1)  # 10% of volume
            
            # Simulate getting historical volume data (in real implementation, this would come from market data)
            historical_volumes = []
            for i in range(lookback_periods):
                # Simulate volume data - replace with real market data
                volume = np.random.normal(1000000, 200000)  # 1M avg volume
                historical_volumes.append(max(volume, 100000))  # Minimum volume
            
            # Calculate volume weights
            total_volume = sum(historical_volumes)
            volume_weights = [v / total_volume for v in historical_volumes]
            
            # Get current market price from order book
            current_price = self._get_market_price(order.symbol, order_book)
            
            # Calculate VWAP target price
            vwap_target = current_price  # In reality, this would be calculated from historical data
            
            # Determine execution schedule based on volume profile
            remaining_quantity = order.quantity
            executed_quantity = 0
            execution_prices = []
            
            # Execute in slices based on volume profile
            for i, weight in enumerate(volume_weights):
                if remaining_quantity <= 0:
                    break
                
                # Calculate slice size based on volume participation rate
                slice_volume = historical_volumes[i] * participation_rate
                slice_size = min(remaining_quantity, slice_volume)
                
                if slice_size > 0:
                    # Execute slice at market price (with some price improvement logic)
                    execution_price = self._get_vwap_price(order, order_book, vwap_target)
                    
                    # Record execution
                    execution_prices.append(execution_price)
                    executed_quantity += slice_size
                    remaining_quantity -= slice_size
                    
                    # Update order
                    order.filled_quantity += slice_size
                    order.avg_fill_price = sum(execution_prices) / len(execution_prices)
                    order.updated_at = datetime.now()
                    
                    logger.info(f"VWAP slice executed: {slice_size} @ {execution_price}")
                    
                    # Small delay between slices
                    await asyncio.sleep(0.1)
            
            # Update order status
            if order.filled_quantity >= order.quantity:
                order.status = OrderStatus.FILLED
            else:
                order.status = OrderStatus.PARTIAL
            
            # Calculate actual VWAP achieved
            actual_vwap = sum(execution_prices) / len(execution_prices) if execution_prices else 0
            
            logger.info(f"VWAP execution completed: {executed_quantity}/{order.quantity} @ {actual_vwap}")
            
        except Exception as e:
            logger.error(f"VWAP execution failed: {e}")
            order.status = OrderStatus.REJECTED
            raise
    
    def _get_market_price(self, symbol: str, order_book: Dict) -> float:
        """Get current market price from order book"""
        # Simplified market price calculation
        buy_orders = [o for o in order_book.values() if o.side == OrderSide.BUY and o.status == OrderStatus.PENDING]
        sell_orders = [o for o in order_book.values() if o.side == OrderSide.SELL and o.status == OrderStatus.PENDING]
        
        if buy_orders and sell_orders:
            best_bid = max(o.price for o in buy_orders)
            best_ask = min(o.price for o in sell_orders)
            return (best_bid + best_ask) / 2
        elif buy_orders:
            return max(o.price for o in buy_orders)
        elif sell_orders:
            return min(o.price for o in sell_orders)
        else:
            return 100.0  # Default price
    
    def _get_vwap_price(self, order: AdvancedOrder, order_book: Dict, vwap_target: float) -> float:
        """Get execution price for VWAP order"""
        market_price = self._get_market_price(order.symbol, order_book)
        
        # Try to get price improvement while staying near VWAP target
        if order.side == OrderSide.BUY:
            # For buy orders, try to buy below market but not too far from VWAP
            max_price = min(market_price, vwap_target * 1.001)  # 0.1% above VWAP max
            return max_price * 0.999  # Small discount
        else:
            # For sell orders, try to sell above market but not too far from VWAP
            min_price = max(market_price, vwap_target * 0.999)  # 0.1% below VWAP min
            return min_price * 1.001  # Small premium
        
    async def _execute_iceberg(self, order: AdvancedOrder, order_book: Dict):
        """Execute Iceberg order"""
        try:
            # Get Iceberg parameters
            visible_quantity = order.strategy_params.get('visible_quantity', order.quantity * 0.1)  # 10% visible default
            hidden_quantity = order.quantity - visible_quantity
            slice_interval = order.strategy_params.get('slice_interval', 1.0)  # 1 second between slices
            
            executed_quantity = 0
            execution_prices = []
            slice_count = 0
            
            while executed_quantity < order.quantity:
                # Determine current slice size
                remaining_hidden = hidden_quantity - (executed_quantity - visible_quantity)
                remaining_visible = visible_quantity if slice_count == 0 else 0
                
                current_slice_size = min(
                    remaining_visible + remaining_hidden,
                    order.quantity - executed_quantity
                )
                
                if current_slice_size <= 0:
                    break
                
                # Execute current slice
                execution_price = self._get_market_price(order.symbol, order_book)
                
                # For buy orders, try to get slightly better price
                if order.side == OrderSide.BUY:
                    execution_price *= 0.999  # 0.1% discount
                else:
                    execution_price *= 1.001  # 0.1% premium
                
                # Record execution
                execution_prices.append(execution_price)
                executed_quantity += current_slice_size
                slice_count += 1
                
                # Update order
                order.filled_quantity = executed_quantity
                order.avg_fill_price = sum(execution_prices) / len(execution_prices)
                order.updated_at = datetime.now()
                
                logger.info(f"Iceberg slice {slice_count}: {current_slice_size} @ {execution_price} (Visible: {remaining_visible > 0})")
                
                # Wait between slices to avoid market impact
                if executed_quantity < order.quantity:
                    await asyncio.sleep(slice_interval)
            
            # Update order status
            if order.filled_quantity >= order.quantity:
                order.status = OrderStatus.FILLED
            else:
                order.status = OrderStatus.PARTIAL
            
            # Calculate execution statistics
            avg_price = sum(execution_prices) / len(execution_prices) if execution_prices else 0
            
            logger.info(f"Iceberg execution completed: {executed_quantity}/{order.quantity} @ {avg_price}, {slice_count} slices")
            
        except Exception as e:
            logger.error(f"Iceberg execution failed: {e}")
            order.status = OrderStatus.REJECTED
            raise
        
    async def _execute_market(self, order: AdvancedOrder, order_book: Dict):
        """Execute market order"""
        # Market order implementation
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.updated_at = datetime.now()
        
    async def _execute_limit(self, order: AdvancedOrder, order_book: Dict):
        """Execute limit order"""
        try:
            # Get current market price
            current_price = self._get_market_price(order.symbol, order_book)
            
            # Check if limit order can be executed immediately
            can_execute = False
            
            if order.side == OrderSide.BUY:
                # Buy limit order executes if market price <= limit price
                can_execute = current_price <= order.price
            else:
                # Sell limit order executes if market price >= limit price
                can_execute = current_price >= order.price
            
            if can_execute:
                # Execute immediately at current market price (which is favorable)
                execution_price = current_price
                
                # For additional price improvement
                if order.side == OrderSide.BUY:
                    execution_price = min(execution_price, order.price * 0.999)  # Try for better price
                else:
                    execution_price = max(execution_price, order.price * 1.001)  # Try for better price
                
                # Update order
                order.status = OrderStatus.FILLED
                order.filled_quantity = order.quantity
                order.avg_fill_price = execution_price
                order.updated_at = datetime.now()
                
                logger.info(f"Limit order executed immediately: {order.quantity} @ {execution_price}")
                
            else:
                # Order cannot be executed immediately, keep it in order book
                order.status = OrderStatus.PENDING
                order.updated_at = datetime.now()
                
                # Add to order book for future matching
                if order.symbol not in order_book:
                    order_book[order.symbol] = {}
                order_book[order.symbol][order.order_id] = order
                
                logger.info(f"Limit order placed in book: {order.side.value} {order.quantity} @ {order.price}")
                
                # Try to match with existing orders
                await self.match_orders(order.symbol, order_book)
            
        except Exception as e:
            logger.error(f"Limit order execution failed: {e}")
            order.status = OrderStatus.REJECTED
            raise
        
    async def _execute_default(self, order: AdvancedOrder, order_book: Dict):
        """Default execution method"""
        await self._execute_market(order, order_book)
        
    async def _execute_market_slice(self, order: AdvancedOrder, slice_size: float) -> dict:
        """Execute market order slice"""
        try:
            # Get current market price (simplified - would use real market data)
            execution_price = order.price if hasattr(order, 'price') else 100.0
            
            # Apply small market impact adjustment for large slices
            market_impact = min(0.001, slice_size / 1000000)  # Max 0.1% impact
            
            if order.side == OrderSide.BUY:
                execution_price *= (1 + market_impact)  # Buy at slightly higher price
            else:
                execution_price *= (1 - market_impact)  # Sell at slightly lower price
            
            # Update order with slice execution
            order.filled_quantity += slice_size
            
            # Calculate average fill price
            if hasattr(order, 'total_executed_value'):
                order.total_executed_value += execution_price * slice_size
            else:
                order.total_executed_value = execution_price * slice_size
            
            order.avg_fill_price = order.total_executed_value / order.filled_quantity
            order.updated_at = datetime.now()
            
            # Update order status if fully filled
            if order.filled_quantity >= order.quantity:
                order.status = OrderStatus.FILLED
            else:
                order.status = OrderStatus.PARTIAL
            
            logger.info(f"Market slice executed: {slice_size} @ {execution_price}")
            
            return {
                "success": True,
                "slice_size": slice_size,
                "execution_price": execution_price,
                "total_filled": order.filled_quantity,
                "order_status": order.status.value,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Market slice execution failed: {e}")
            return {
                "success": False,
                "slice_size": slice_size,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Global trading engine instance
_trading_engine = None

def get_trading_engine() -> AdvancedTradingEngine:
    """Get the global trading engine instance"""
    global _trading_engine
    if _trading_engine is None:
        _trading_engine = AdvancedTradingEngine()
    return _trading_engine
