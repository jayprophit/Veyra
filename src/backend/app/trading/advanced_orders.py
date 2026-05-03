"""Advanced Order Types for Financial Master."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    OCO = "oco"  # One Cancels Other
    BRACKET = "bracket"
    ICEBERG = "iceberg"

class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIGGERED = "triggered"

@dataclass
class Order:
    id: str
    symbol: str
    side: str  # buy/sell
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = None
    updated_at: datetime = None
    parent_id: Optional[str] = None  # For OCO/bracket
    child_orders: List[str] = None
    trailing_pct: Optional[float] = None
    display_qty: Optional[float] = None  # For iceberg
    hidden_qty: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.child_orders is None:
            self.child_orders = []

class AdvancedOrderManager:
    """Manages complex order types and execution."""
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.price_tracking: Dict[str, List[float]] = {}
        self.order_counter = 0
    
    def _generate_id(self) -> str:
        self.order_counter += 1
        return f"ord_{self.order_counter}_{datetime.now().strftime('%H%M%S')}"
    
    async def place_market_order(self, symbol: str, side: str, quantity: float) -> Order:
        """Place a market order."""
        order = Order(
            id=self._generate_id(),
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=quantity,
            status=OrderStatus.FILLED
        )
        self.orders[order.id] = order
        logger.info(f"Market order placed: {order.id}")
        return order
    
    async def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Order:
        """Place a limit order."""
        order = Order(
            id=self._generate_id(),
            symbol=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
            status=OrderStatus.OPEN
        )
        self.orders[order.id] = order
        return order
    
    async def place_stop_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> Order:
        """Place a stop order."""
        order = Order(
            id=self._generate_id(),
            symbol=symbol,
            side=side,
            order_type=OrderType.STOP,
            quantity=quantity,
            stop_price=stop_price,
            status=OrderStatus.PENDING
        )
        self.orders[order.id] = order
        return order
    
    async def place_trailing_stop(self, symbol: str, side: str, quantity: float, 
                                  trailing_pct: float) -> Order:
        """Place a trailing stop order."""
        order = Order(
            id=self._generate_id(),
            symbol=symbol,
            side=side,
            order_type=OrderType.TRAILING_STOP,
            quantity=quantity,
            trailing_pct=trailing_pct,
            status=OrderStatus.OPEN
        )
        self.orders[order.id] = order
        
        # Track price for trailing calculation
        if symbol not in self.price_tracking:
            self.price_tracking[symbol] = []
        
        logger.info(f"Trailing stop placed: {order.id} at {trailing_pct}%")
        return order
    
    async def place_oco_order(self, symbol: str, side: str, quantity: float,
                              limit_price: float, stop_price: float) -> Dict[str, Order]:
        """Place One-Cancels-Other order (limit + stop)."""
        parent_id = self._generate_id()
        
        # Limit order
        limit_order = Order(
            id=self._generate_id(),
            symbol=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=limit_price,
            parent_id=parent_id,
            status=OrderStatus.OPEN
        )
        
        # Stop order
        stop_order = Order(
            id=self._generate_id(),
            symbol=symbol,
            side=side,
            order_type=OrderType.STOP,
            quantity=quantity,
            stop_price=stop_price,
            parent_id=parent_id,
            status=OrderStatus.PENDING
        )
        
        # Link orders
        limit_order.child_orders = [stop_order.id]
        stop_order.child_orders = [limit_order.id]
        
        self.orders[limit_order.id] = limit_order
        self.orders[stop_order.id] = stop_order
        
        logger.info(f"OCO order placed: {parent_id}")
        
        return {
            'parent_id': parent_id,
            'limit_order': limit_order,
            'stop_order': stop_order
        }
    
    async def place_bracket_order(self, symbol: str, side: str, quantity: float,
                                  entry_price: float, take_profit: float, 
                                  stop_loss: float) -> Dict[str, Order]:
        """Place bracket order (entry + TP + SL)."""
        parent_id = self._generate_id()
        
        # Entry order
        entry = Order(
            id=self._generate_id(),
            symbol=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=entry_price,
            parent_id=parent_id,
            status=OrderStatus.OPEN
        )
        
        # Take profit (opposite side)
        tp_side = 'sell' if side == 'buy' else 'buy'
        take_profit_order = Order(
            id=self._generate_id(),
            symbol=symbol,
            side=tp_side,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=take_profit,
            parent_id=parent_id,
            status=OrderStatus.PENDING
        )
        
        # Stop loss (opposite side)
        stop_loss_order = Order(
            id=self._generate_id(),
            symbol=symbol,
            side=tp_side,
            order_type=OrderType.STOP,
            quantity=quantity,
            stop_price=stop_loss,
            parent_id=parent_id,
            status=OrderStatus.PENDING
        )
        
        entry.child_orders = [take_profit_order.id, stop_loss_order.id]
        
        self.orders[entry.id] = entry
        self.orders[take_profit_order.id] = take_profit_order
        self.orders[stop_loss_order.id] = stop_loss_order
        
        return {
            'parent_id': parent_id,
            'entry': entry,
            'take_profit': take_profit_order,
            'stop_loss': stop_loss_order
        }
    
    async def place_iceberg_order(self, symbol: str, side: str, total_quantity: float,
                                  display_qty: float, price: float) -> Order:
        """Place iceberg order (large order hidden in slices)."""
        order = Order(
            id=self._generate_id(),
            symbol=symbol,
            side=side,
            order_type=OrderType.ICEBERG,
            quantity=total_quantity,
            price=price,
            display_qty=display_qty,
            hidden_qty=total_quantity - display_qty,
            status=OrderStatus.OPEN
        )
        self.orders[order.id] = order
        return order
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order and linked orders."""
        order = self.orders.get(order_id)
        if not order:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        
        # Cancel linked orders
        for child_id in order.child_orders:
            if child_id in self.orders:
                self.orders[child_id].status = OrderStatus.CANCELLED
        
        return True
    
    async def check_trailing_stops(self, symbol: str, current_price: float):
        """Check and update trailing stops based on price movement."""
        for order in self.orders.values():
            if (order.symbol == symbol and 
                order.order_type == OrderType.TRAILING_STOP and
                order.status == OrderStatus.OPEN):
                
                # Track highest/lowest price
                if symbol not in self.price_tracking:
                    self.price_tracking[symbol] = []
                self.price_tracking[symbol].append(current_price)
                
                if order.side == 'buy':
                    # For short positions, trail from lowest price
                    extreme = min(self.price_tracking[symbol])
                    trigger = extreme * (1 + order.trailing_pct / 100)
                    if current_price >= trigger:
                        order.status = OrderStatus.TRIGGERED
                        logger.info(f"Trailing stop triggered: {order.id} at {current_price}")
                else:
                    # For long positions, trail from highest price
                    extreme = max(self.price_tracking[symbol])
                    trigger = extreme * (1 - order.trailing_pct / 100)
                    if current_price <= trigger:
                        order.status = OrderStatus.TRIGGERED
                        logger.info(f"Trailing stop triggered: {order.id} at {current_price}")
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self.orders.get(order_id)
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders."""
        orders = [o for o in self.orders.values() if o.status == OrderStatus.OPEN]
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        return orders

order_manager = AdvancedOrderManager()
