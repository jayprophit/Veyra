"""Automated Market Making Module."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)

class MMStrategy(Enum):
    BASIC = "basic"
    INVENTORY_SKEWED = "inventory_skewed"
    ADVERSE_SELECTION = "adverse_selection"
    PEGGED = "pegged"

@dataclass
class MMOrder:
    order_id: str
    side: str
    price: float
    size: float
    spread: float
    timestamp: datetime

@dataclass
class InventoryState:
    symbol: str
    position: float
    avg_entry: float
    target_position: float
    max_position: float
    pnl: float

class AutomatedMarketMaker:
    """
    Professional market making with inventory management and adverse selection protection.
    """
    
    def __init__(self):
        self.strategies: Dict[str, MMStrategy] = {}
        self.orders: Dict[str, List[MMOrder]] = {}
        self.inventory: Dict[str, InventoryState] = {}
        self.quote_history: Dict[str, List[Dict]] = {}
        self.filled_trades: List[Dict] = []
        
        # MM parameters
        self.base_spread_bps = 10
        self.max_inventory_skew = 0.3
        self.rebalance_threshold = 0.2
        
    async def start_market_making(self,
                                 symbol: str,
                                 strategy: str = "basic",
                                 target_position: float = 0,
                                 max_position: float = 1000,
                                 base_spread_bps: float = 10) -> Dict[str, Any]:
        """Start automated market making for symbol."""
        
        self.strategies[symbol] = MMStrategy(strategy)
        self.orders[symbol] = []
        self.inventory[symbol] = InventoryState(
            symbol=symbol,
            position=0,
            avg_entry=0,
            target_position=target_position,
            max_position=max_position,
            pnl=0
        )
        
        self.base_spread_bps = base_spread_bps
        
        logger.info(f"Market making started: {symbol} with {strategy} strategy")
        
        return {
            'symbol': symbol,
            'strategy': strategy,
            'status': 'active',
            'target_position': target_position,
            'max_position': max_position,
            'base_spread_bps': base_spread_bps,
            'started_at': datetime.now().isoformat()
        }
    
    async def generate_quotes(self,
                            symbol: str,
                            mid_price: float,
                            market_conditions: Dict) -> Dict[str, Any]:
        """Generate bid/ask quotes with dynamic spread."""
        
        if symbol not in self.inventory:
            return {'error': 'Market making not initialized'}
        
        inventory = self.inventory[symbol]
        strategy = self.strategies.get(symbol, MMStrategy.BASIC)
        
        # Calculate dynamic spread
        spread = self._calculate_spread(symbol, market_conditions, strategy)
        
        # Inventory skewing
        skew = self._calculate_inventory_skew(inventory)
        
        # Generate quotes
        bid_price = mid_price * (1 - spread/2 + skew)
        ask_price = mid_price * (1 + spread/2 + skew)
        
        # Size based on inventory
        bid_size = self._calculate_size(symbol, 'bid', inventory)
        ask_size = self._calculate_size(symbol, 'ask', inventory)
        
        bid_order = MMOrder(
            order_id=f"mm_bid_{symbol}_{datetime.now().strftime('%H%M%S%f')}",
            side='bid',
            price=round(bid_price, 2),
            size=bid_size,
            spread=spread,
            timestamp=datetime.now()
        )
        
        ask_order = MMOrder(
            order_id=f"mm_ask_{symbol}_{datetime.now().strftime('%H%M%S%f')}",
            side='ask',
            price=round(ask_price, 2),
            size=ask_size,
            spread=spread,
            timestamp=datetime.now()
        )
        
        self.orders[symbol] = [bid_order, ask_order]
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'mid_price': mid_price,
            'spread_bps': round(spread * 10000, 2),
            'inventory_skew': round(skew, 4),
            'quotes': {
                'bid': {'price': bid_order.price, 'size': bid_order.size},
                'ask': {'price': ask_order.price, 'size': ask_order.size}
            }
        }
    
    def _calculate_spread(self, symbol: str, conditions: Dict, strategy: MMStrategy) -> float:
        """Calculate dynamic spread based on conditions."""
        base = self.base_spread_bps / 10000
        
        # Volatility adjustment
        volatility = conditions.get('volatility', 0.2)
        vol_adjustment = volatility * 0.5
        
        # Volume adjustment
        volume = conditions.get('volume', 1000000)
        volume_factor = max(0.5, min(2.0, 1000000 / volume))
        
        if strategy == MMStrategy.ADVERSE_SELECTION:
            # Wider spread for adverse selection protection
            order_flow_imbalance = conditions.get('order_flow_imbalance', 0)
            base += abs(order_flow_imbalance) * 0.001
        
        return base * volume_factor + vol_adjustment
    
    def _calculate_inventory_skew(self, inventory: InventoryState) -> float:
        """Calculate price skew based on inventory position."""
        if inventory.max_position == 0:
            return 0
        
        position_ratio = (inventory.position - inventory.target_position) / inventory.max_position
        
        # Skew: positive = lift prices (want to sell), negative = lower prices (want to buy)
        return -position_ratio * self.max_inventory_skew
    
    def _calculate_size(self, symbol: str, side: str, inventory: InventoryState) -> float:
        """Calculate order size based on inventory."""
        base_size = 100
        
        if side == 'bid':
            # Reduce buy size if long
            if inventory.position > 0:
                return base_size * (1 - inventory.position / inventory.max_position)
        else:
            # Reduce sell size if short
            if inventory.position < 0:
                return base_size * (1 - abs(inventory.position) / inventory.max_position)
        
        return base_size
    
    async def process_fill(self,
                          symbol: str,
                          side: str,
                          price: float,
                          size: float) -> Dict[str, Any]:
        """Process a fill and update inventory."""
        if symbol not in self.inventory:
            return {'error': 'Symbol not found'}
        
        inventory = self.inventory[symbol]
        
        # Update position
        if side == 'bid':  # We bought
            new_position = inventory.position + size
            inventory.avg_entry = (inventory.position * inventory.avg_entry + size * price) / new_position if new_position != 0 else price
            inventory.position = new_position
        else:  # We sold
            # Realized P&L
            if inventory.position > 0:
                realized_pnl = (price - inventory.avg_entry) * min(size, inventory.position)
                inventory.pnl += realized_pnl
            inventory.position -= size
        
        fill_record = {
            'symbol': symbol,
            'side': side,
            'price': price,
            'size': size,
            'timestamp': datetime.now().isoformat(),
            'position_after': inventory.position,
            'pnl': inventory.pnl
        }
        
        self.filled_trades.append(fill_record)
        
        return fill_record
    
    async def get_mm_status(self, symbol: str) -> Dict[str, Any]:
        """Get market making status."""
        if symbol not in self.inventory:
            return {'error': 'Not market making this symbol'}
        
        inventory = self.inventory[symbol]
        orders = self.orders.get(symbol, [])
        
        return {
            'symbol': symbol,
            'status': 'active',
            'strategy': self.strategies.get(symbol, MMStrategy.BASIC).value,
            'inventory': {
                'position': inventory.position,
                'avg_entry': inventory.avg_entry,
                'target': inventory.target_position,
                'max': inventory.max_position,
                'utilization': abs(inventory.position) / inventory.max_position
            },
            'pnl': inventory.pnl,
            'active_quotes': len(orders),
            'total_fills': len(self.filled_trades)
        }
    
    async def stop_market_making(self, symbol: str) -> Dict[str, Any]:
        """Stop market making and flatten position."""
        if symbol not in self.inventory:
            return {'error': 'Not market making this symbol'}
        
        inventory = self.inventory[symbol]
        
        result = {
            'symbol': symbol,
            'status': 'stopped',
            'final_position': inventory.position,
            'final_pnl': inventory.pnl,
            'stopped_at': datetime.now().isoformat()
        }
        
        # Cleanup
        del self.inventory[symbol]
        del self.strategies[symbol]
        if symbol in self.orders:
            del self.orders[symbol]
        
        return result

market_maker = AutomatedMarketMaker()
