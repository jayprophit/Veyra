"""
Grid Trading Bot
================
Automated grid trading for sideways markets.
Buys low, sells high within a price range.

Phase 11 Extension - Grid Trading Capability
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class GridStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class GridLevel:
    """Single grid level configuration"""
    price: float
    buy_order_id: Optional[str] = None
    sell_order_id: Optional[str] = None
    filled_buy: bool = False
    filled_sell: bool = False
    quantity: float = 0.0


@dataclass
class GridBotConfig:
    """Grid bot configuration"""
    symbol: str
    lower_price: float
    upper_price: float
    grids: int = 10
    investment: float = 100.0
    exchange: str = "alpaca"  # alpaca, pionex, binance
    paper_trading: bool = True


class GridTradingBot:
    """
    Grid Trading Bot for sideways markets.
    
    Creates a grid of buy/sell orders between lower and upper price bounds.
    When price drops to a grid level -> BUY
    When price rises to next grid level -> SELL
    
    Perfect for:
    - Sideways markets
    - Volatile but range-bound assets
    - Accumulating small profits consistently
    """
    
    def __init__(self, config: GridBotConfig):
        self.config = config
        self.status = GridStatus.STOPPED
        self.grid_levels: List[GridLevel] = []
        self.current_price: float = 0.0
        self.total_profit: float = 0.0
        self.total_trades: int = 0
        self.created_at = datetime.now()
        self.bot_id = f"GRID_{config.symbol}_{int(datetime.now().timestamp())}"
        
        # Calculate grid spacing
        self.grid_spacing = (config.upper_price - config.lower_price) / config.grids
        self.quantity_per_grid = config.investment / config.grids
        
        self._initialize_grids()
    
    def _initialize_grids(self):
        """Initialize grid levels"""
        for i in range(self.config.grids + 1):
            price = self.config.lower_price + (i * self.grid_spacing)
            self.grid_levels.append(GridLevel(price=price))
        logger.info(f"Initialized {len(self.grid_levels)} grid levels for {self.config.symbol}")
    
    async def start(self):
        """Start the grid bot"""
        self.status = GridStatus.ACTIVE
        logger.info(f"Grid bot {self.bot_id} started for {self.config.symbol}")
        
        # Start monitoring loop
        while self.status == GridStatus.ACTIVE:
            try:
                await self._check_prices_and_trade()
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Grid bot error: {e}")
                await asyncio.sleep(10)
    
    async def _check_prices_and_trade(self):
        """Check current price and execute grid trades"""
        # In real implementation, this would fetch from exchange
        # For now, simulate with mock price
        self.current_price = await self._get_current_price()
        
        # Find nearest grid levels
        for i, level in enumerate(self.grid_levels):
            # Check if price hit this level
            if abs(self.current_price - level.price) < (self.grid_spacing * 0.1):
                if not level.filled_buy:
                    await self._execute_buy(level)
                
                # Check if we can sell at next level up
                if i < len(self.grid_levels) - 1:
                    next_level = self.grid_levels[i + 1]
                    if level.filled_buy and not next_level.filled_sell:
                        await self._execute_sell(level, next_level)
    
    async def _get_current_price(self) -> float:
        """Get current market price"""
        # Mock implementation - replace with exchange API
        import random
        return self.config.lower_price + random.random() * (self.config.upper_price - self.config.lower_price)
    
    async def _execute_buy(self, level: GridLevel):
        """Execute buy order at grid level"""
        if self.config.paper_trading:
            logger.info(f"[PAPER] BUY {self.quantity_per_grid} {self.config.symbol} @ {level.price}")
        else:
            logger.info(f"[LIVE] BUY {self.quantity_per_grid} {self.config.symbol} @ {level.price}")
        
        level.filled_buy = True
        level.quantity = self.quantity_per_grid
        self.total_trades += 1
    
    async def _execute_sell(self, buy_level: GridLevel, sell_level: GridLevel):
        """Execute sell order at next grid level"""
        profit = (sell_level.price - buy_level.price) * buy_level.quantity
        
        if self.config.paper_trading:
            logger.info(f"[PAPER] SELL {buy_level.quantity} {self.config.symbol} @ {sell_level.price} | Profit: ${profit:.2f}")
        else:
            logger.info(f"[LIVE] SELL {buy_level.quantity} {self.config.symbol} @ {sell_level.price} | Profit: ${profit:.2f}")
        
        sell_level.filled_sell = True
        buy_level.filled_buy = False  # Reset for next cycle
        buy_level.quantity = 0
        self.total_profit += profit
        self.total_trades += 1
    
    def pause(self):
        """Pause the bot"""
        self.status = GridStatus.PAUSED
        logger.info(f"Grid bot {self.bot_id} paused")
    
    def stop(self):
        """Stop the bot completely"""
        self.status = GridStatus.STOPPED
        logger.info(f"Grid bot {self.bot_id} stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            "bot_id": self.bot_id,
            "symbol": self.config.symbol,
            "status": self.status.value,
            "current_price": self.current_price,
            "grid_range": f"{self.config.lower_price} - {self.config.upper_price}",
            "grids": self.config.grids,
            "total_profit": self.total_profit,
            "total_trades": self.total_trades,
            "grid_levels": [
                {
                    "price": level.price,
                    "filled_buy": level.filled_buy,
                    "filled_sell": level.filled_sell,
                    "quantity": level.quantity
                }
                for level in self.grid_levels
            ]
        }


class PionexGridBot(GridTradingBot):
    """
    Pionex-specific Grid Bot implementation.
    Takes advantage of Pionex's 0.05% trading fees.
    """
    
    def __init__(self, symbol: str, lower_price: float, upper_price: float, 
                 grids: int = 10, investment: float = 100.0):
        config = GridBotConfig(
            symbol=symbol,
            lower_price=lower_price,
            upper_price=upper_price,
            grids=grids,
            investment=investment,
            exchange="pionex",
            paper_trading=True
        )
        super().__init__(config)
        self.trading_fee = 0.0005  # 0.05% Pionex fee
    
    def calculate_grid_profit(self, grid_number: int) -> float:
        """
        Calculate expected profit per grid considering Pionex fees.
        
        Args:
            grid_number: Which grid level (0 to grids)
        
        Returns:
            Expected profit after fees
        """
        price_per_grid = (self.config.upper_price - self.config.lower_price) / self.config.grids
        gross_profit = price_per_grid * self.quantity_per_grid
        
        # Subtract fees (buy + sell)
        buy_fee = self.quantity_per_grid * self.config.lower_price * self.trading_fee
        sell_fee = self.quantity_per_grid * (self.config.lower_price + price_per_grid) * self.trading_fee
        total_fees = buy_fee + sell_fee
        
        net_profit = gross_profit - total_fees
        return net_profit
    
    def get_profit_summary(self) -> Dict[str, Any]:
        """Get profit summary with fee calculations"""
        total_gross = self.total_profit
        estimated_fees = self.total_trades * self.quantity_per_grid * self.current_price * self.trading_fee
        net_profit = total_gross - estimated_fees
        
        return {
            "symbol": self.config.symbol,
            "exchange": "Pionex (0.05% fees)",
            "total_gross_profit": total_gross,
            "estimated_fees": estimated_fees,
            "net_profit": net_profit,
            "total_trades": self.total_trades,
            "avg_profit_per_trade": net_profit / self.total_trades if self.total_trades > 0 else 0,
            "grids": self.config.grids,
            "investment": self.config.investment
        }


# Quick-start functions for common strategies
def create_btc_grid_bot(investment: float = 100.0, paper: bool = True) -> GridTradingBot:
    """
    Create a BTC grid bot with typical range for sideways market.
    Range: $40,000 - $50,000 (adjust as needed)
    """
    config = GridBotConfig(
        symbol="BTC/USD",
        lower_price=40000,
        upper_price=50000,
        grids=10,
        investment=investment,
        exchange="alpaca",
        paper_trading=paper
    )
    return GridTradingBot(config)


def create_eth_grid_bot(investment: float = 100.0, paper: bool = True) -> GridTradingBot:
    """
    Create an ETH grid bot with typical range.
    Range: $2,000 - $3,000 (adjust as needed)
    """
    config = GridBotConfig(
        symbol="ETH/USD",
        lower_price=2000,
        upper_price=3000,
        grids=10,
        investment=investment,
        exchange="alpaca",
        paper_trading=paper
    )
    return GridTradingBot(config)


def create_pionex_btc_grid(investment: float = 100.0) -> PionexGridBot:
    """Create a Pionex BTC grid bot for lowest fees"""
    return PionexGridBot(
        symbol="BTC/USDT",
        lower_price=40000,
        upper_price=50000,
        grids=20,
        investment=investment
    )


# Example usage
if __name__ == "__main__":
    # Create and start a grid bot
    bot = create_btc_grid_bot(investment=50.0, paper=True)
    
    # Print configuration
    print(f"Grid Bot Created:")
    print(f"Symbol: {bot.config.symbol}")
    print(f"Range: ${bot.config.lower_price:,} - ${bot.config.upper_price:,}")
    print(f"Grids: {bot.config.grids}")
    print(f"Investment: ${bot.config.investment}")
    print(f"Quantity per grid: {bot.quantity_per_grid:.6f}")
    
    # Run for demonstration
    async def demo():
        await bot.start()
    
    # asyncio.run(demo())
