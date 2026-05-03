"""
Grid Trading Strategy
Place buy/sell orders at regular intervals (grid) around current price
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class GridLevel:
    price: float
    buy_order_id: Optional[str] = None
    sell_order_id: Optional[str] = None
    active: bool = True
    executed: bool = False

class GridTradingStrategy:
    """
    Grid trading - place orders at fixed intervals
    Profits from sideways market movement
    """
    
    def __init__(self, 
                 symbol: str,
                 lower_price: float,
                 upper_price: float,
                 grid_levels: int = 10,
                 quantity_per_grid: float = 1.0):
        self.symbol = symbol
        self.lower_price = lower_price
        self.upper_price = upper_price
        self.grid_levels = grid_levels
        self.quantity_per_grid = quantity_per_grid
        
        self.grids: List[GridLevel] = []
        self.active = False
        self.total_profit = 0.0
        self.trade_count = 0
        
        self._initialize_grids()
    
    def _initialize_grids(self):
        """Create grid levels"""
        price_step = (self.upper_price - self.lower_price) / (self.grid_levels - 1)
        
        for i in range(self.grid_levels):
            price = self.lower_price + (price_step * i)
            self.grids.append(GridLevel(price=round(price, 2)))
    
    async def start_grid(self, exchange_connector):
        """Start grid trading by placing initial orders"""
        self.active = True
        
        for i, grid in enumerate(self.grids):
            # Place buy orders on lower half
            if i < len(self.grids) // 2:
                order = await exchange_connector.place_limit_order(
                    symbol=self.symbol,
                    side='buy',
                    quantity=self.quantity_per_grid,
                    price=grid.price
                )
                grid.buy_order_id = order.get('id')
            
            # Place sell orders on upper half
            else:
                order = await exchange_connector.place_limit_order(
                    symbol=self.symbol,
                    side='sell',
                    quantity=self.quantity_per_grid,
                    price=grid.price
                )
                grid.sell_order_id = order.get('id')
        
        print(f"Grid initialized: {self.grid_levels} levels for {self.symbol}")
    
    async def check_and_rebalance(self, exchange_connector, current_price: float):
        """Check filled orders and replace them"""
        if not self.active:
            return
        
        for grid in self.grids:
            # Check if buy order filled
            if grid.buy_order_id:
                order_status = await exchange_connector.get_order_status(grid.buy_order_id)
                if order_status == 'filled':
                    self.trade_count += 1
                    profit = (grid.price - grid.price * 0.995) * self.quantity_per_grid  # Account for fees
                    self.total_profit += profit
                    
                    # Place new sell order one level up
                    next_level_idx = self.grids.index(grid) + 1
                    if next_level_idx < len(self.grids):
                        new_order = await exchange_connector.place_limit_order(
                            symbol=self.symbol,
                            side='sell',
                            quantity=self.quantity_per_grid,
                            price=self.grids[next_level_idx].price
                        )
                        self.grids[next_level_idx].sell_order_id = new_order.get('id')
                    
                    grid.buy_order_id = None
            
            # Check if sell order filled
            if grid.sell_order_id:
                order_status = await exchange_connector.get_order_status(grid.sell_order_id)
                if order_status == 'filled':
                    self.trade_count += 1
                    profit = (grid.price - grid.price * 0.995) * self.quantity_per_grid
                    self.total_profit += profit
                    
                    # Place new buy order one level down
                    prev_level_idx = self.grids.index(grid) - 1
                    if prev_level_idx >= 0:
                        new_order = await exchange_connector.place_limit_order(
                            symbol=self.symbol,
                            side='buy',
                            quantity=self.quantity_per_grid,
                            price=self.grids[prev_level_idx].price
                        )
                        self.grids[prev_level_idx].buy_order_id = new_order.get('id')
                    
                    grid.sell_order_id = None
    
    async def run_grid(self, exchange_connector, check_interval: int = 30):
        """Run grid trading loop"""
        await self.start_grid(exchange_connector)
        
        while self.active:
            try:
                current_price = await exchange_connector.get_price(self.symbol)
                await self.check_and_rebalance(exchange_connector, current_price)
                await asyncio.sleep(check_interval)
            except Exception as e:
                print(f"Grid trading error: {e}")
                await asyncio.sleep(check_interval)
    
    def stop(self):
        """Stop grid trading"""
        self.active = False
    
    def get_status(self) -> Dict:
        """Get current grid status"""
        active_buys = sum(1 for g in self.grids if g.buy_order_id)
        active_sells = sum(1 for g in self.grids if g.sell_order_id)
        
        return {
            "symbol": self.symbol,
            "grid_levels": self.grid_levels,
            "price_range": f"{self.lower_price} - {self.upper_price}",
            "active": self.active,
            "active_buy_orders": active_buys,
            "active_sell_orders": active_sells,
            "total_trades": self.trade_count,
            "total_profit": round(self.total_profit, 2)
        }
