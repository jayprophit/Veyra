"""Paper Trading Simulator for Risk-Free Practice."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

@dataclass
class PaperOrder:
    order_id: str
    user_id: str
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float]
    status: OrderStatus
    filled_quantity: float
    avg_fill_price: float
    commission: float
    created_at: datetime
    filled_at: Optional[datetime] = None

@dataclass
class PaperPosition:
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float

class PaperTradingSimulator:
    """
    Realistic paper trading simulator with market condition modeling.
    Simulates slippage, partial fills, and market impact.
    """
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.orders: Dict[str, PaperOrder] = {}
        self.positions: Dict[str, Dict[str, PaperPosition]] = {}
        self.order_history: List[PaperOrder] = []
        self.market_prices: Dict[str, float] = {}
        self.commission_rate = 0.001
        self.slippage_model = "variable"  # fixed or variable
    
    async def create_account(self, user_id: str, 
                            initial_balance: float = 100000.0) -> Dict[str, Any]:
        """Create paper trading account."""
        self.users[user_id] = {
            'user_id': user_id,
            'balance': initial_balance,
            'equity': initial_balance,
            'created_at': datetime.now(),
            'total_trades': 0,
            'winning_trades': 0,
            'total_commissions': 0.0
        }
        
        self.positions[user_id] = {}
        
        logger.info(f"Paper trading account created: {user_id}")
        return self.users[user_id]
    
    async def submit_order(self,
                          user_id: str,
                          symbol: str,
                          side: str,
                          quantity: float,
                          order_type: str = "market",
                          price: Optional[float] = None) -> PaperOrder:
        """Submit paper trading order."""
        if user_id not in self.users:
            raise ValueError(f"User not found: {user_id}")
        
        order_id = f"paper_{user_id}_{datetime.now().strftime('%H%M%S%f')}"
        
        order = PaperOrder(
            order_id=order_id,
            user_id=user_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            status=OrderStatus.PENDING,
            filled_quantity=0.0,
            avg_fill_price=0.0,
            commission=0.0,
            created_at=datetime.now()
        )
        
        # Simulate order execution
        await self._simulate_execution(order)
        
        self.orders[order_id] = order
        self.order_history.append(order)
        
        return order
    
    async def _simulate_execution(self, order: PaperOrder):
        """Simulate realistic order execution."""
        current_price = self.market_prices.get(order.symbol, 100.0)
        
        # Market impact model
        impact = self._calculate_market_impact(order.symbol, order.quantity, order.side)
        
        if order.order_type == "market":
            # Market orders fill immediately with slippage
            slippage = self._calculate_slippage(order.symbol, order.quantity)
            fill_price = current_price * (1 + slippage) if order.side == "buy" else current_price * (1 - slippage)
            fill_price += impact
            
            order.avg_fill_price = fill_price
            order.filled_quantity = order.quantity
            order.status = OrderStatus.FILLED
            order.filled_at = datetime.now()
            order.commission = fill_price * order.quantity * self.commission_rate
            
        elif order.order_type == "limit":
            # Limit orders only fill if price is favorable
            if order.side == "buy" and current_price <= order.price:
                order.avg_fill_price = min(order.price, current_price)
                order.filled_quantity = order.quantity
                order.status = OrderStatus.FILLED
            elif order.side == "sell" and current_price >= order.price:
                order.avg_fill_price = max(order.price, current_price)
                order.filled_quantity = order.quantity
                order.status = OrderStatus.FILLED
            else:
                order.status = OrderStatus.PENDING
        
        # Update positions if filled
        if order.status == OrderStatus.FILLED:
            await self._update_position(order)
            await self._update_user_stats(order)
    
    def _calculate_slippage(self, symbol: str, quantity: float) -> float:
        """Calculate realistic slippage based on order size."""
        # Larger orders = more slippage
        base_slippage = 0.0001  # 1 basis point
        size_factor = min(quantity / 10000, 0.001)  # Cap at 10bps
        volatility_factor = 0.0005  # Add volatility adjustment
        
        return base_slippage + size_factor + volatility_factor
    
    def _calculate_market_impact(self, symbol: str, quantity: float, side: str) -> float:
        """Calculate temporary market impact."""
        # Simplified market impact model
        impact = (quantity / 100000) * 0.0002  # 2bps per 100k shares
        return impact if side == "buy" else -impact
    
    async def _update_position(self, order: PaperOrder):
        """Update position after fill."""
        user_positions = self.positions[order.user_id]
        
        if order.symbol not in user_positions:
            user_positions[order.symbol] = PaperPosition(
                symbol=order.symbol,
                quantity=0.0,
                avg_entry_price=0.0,
                current_price=order.avg_fill_price,
                unrealized_pnl=0.0,
                realized_pnl=0.0
            )
        
        pos = user_positions[order.symbol]
        
        if order.side == "buy":
            # Increase position
            total_cost = pos.quantity * pos.avg_entry_price + order.filled_quantity * order.avg_fill_price
            pos.quantity += order.filled_quantity
            pos.avg_entry_price = total_cost / pos.quantity if pos.quantity > 0 else 0
        else:
            # Decrease/close position
            if order.filled_quantity <= pos.quantity:
                # Realized P&L
                pnl = (order.avg_fill_price - pos.avg_entry_price) * order.filled_quantity
                pos.realized_pnl += pnl
                pos.quantity -= order.filled_quantity
            else:
                # Short selling (if allowed)
                pos.quantity -= order.filled_quantity
    
    async def _update_user_stats(self, order: PaperOrder):
        """Update user trading statistics."""
        user = self.users[order.user_id]
        user['total_trades'] += 1
        user['total_commissions'] += order.commission
        
        # Update balance
        cost = order.avg_fill_price * order.filled_quantity
        if order.side == "buy":
            user['balance'] -= (cost + order.commission)
        else:
            user['balance'] += (cost - order.commission)
    
    async def update_market_prices(self, prices: Dict[str, float]):
        """Update market prices and recalculate P&L."""
        self.market_prices.update(prices)
        
        # Update unrealized P&L for all positions
        for user_id, positions in self.positions.items():
            for symbol, pos in positions.items():
                if symbol in prices:
                    pos.current_price = prices[symbol]
                    pos.unrealized_pnl = (pos.current_price - pos.avg_entry_price) * pos.quantity
            
            # Update user equity
            total_unrealized = sum(p.unrealized_pnl for p in positions.values())
            self.users[user_id]['equity'] = self.users[user_id]['balance'] + total_unrealized
    
    async def get_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Get paper trading portfolio."""
        if user_id not in self.users:
            return {'error': 'User not found'}
        
        user = self.users[user_id]
        positions = self.positions.get(user_id, {})
        
        return {
            'user_id': user_id,
            'balance': user['balance'],
            'equity': user['equity'],
            'total_return': (user['equity'] / 100000 - 1) * 100,
            'total_trades': user['total_trades'],
            'total_commissions': user['total_commissions'],
            'positions': [{
                'symbol': p.symbol,
                'quantity': p.quantity,
                'avg_entry': p.avg_entry_price,
                'current_price': p.current_price,
                'unrealized_pnl': p.unrealized_pnl,
                'realized_pnl': p.realized_pnl
            } for p in positions.values() if p.quantity != 0],
            'open_orders': [{
                'order_id': o.order_id,
                'symbol': o.symbol,
                'side': o.side,
                'quantity': o.quantity,
                'filled': o.filled_quantity,
                'status': o.status.value
            } for o in self.orders.values()
            if o.user_id == user_id and o.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]]
        }
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel pending order."""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.status == OrderStatus.PENDING:
            order.status = OrderStatus.CANCELLED
            return True
        
        return False

paper_trading = PaperTradingSimulator()
