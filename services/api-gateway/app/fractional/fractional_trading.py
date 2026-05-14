"""
Fractional Share Trading
Enable buying fractional amounts of expensive stocks
Inspired by Robinhood, Trading212 fractional shares
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from enum import Enum


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class FractionalOrder:
    """Fractional share order"""
    order_id: str
    user_id: str
    symbol: str
    side: OrderSide
    
    # Amount can be specified in dollars or shares
    dollar_amount: Optional[Decimal] = None
    share_amount: Optional[Decimal] = None
    
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    
    # Execution details
    status: str = "pending"  # pending, filled, partial, cancelled, rejected
    filled_shares: Decimal = Decimal("0")
    filled_dollar_amount: Decimal = Decimal("0")
    avg_fill_price: Optional[Decimal] = None
    
    created_at: datetime = None
    filled_at: Optional[datetime] = None
    
    # Metadata
    time_in_force: str = "day"  # day, gtc, ioc, fok
    extended_hours: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def is_fractional(self) -> bool:
        """Check if this is a fractional order"""
        if self.share_amount:
            return self.share_amount % 1 != 0
        return True  # Dollar-based orders are always fractional


class FractionalTradingManager:
    """
    Manages fractional share trading
    Allows users to buy stocks with any dollar amount
    """
    
    # Supported fractional stocks (in production, fetch from API)
    SUPPORTED_FRACTIONAL_ASSETS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA",
        "NFLX", "CRM", "ADBE", "PYPL", "UBER", "LYFT", "SQ",
        "BTC", "ETH", "ADA", "SOL", "DOT", "AVAX"
    ]
    
    # Minimum order sizes
    MIN_DOLLAR_AMOUNT = Decimal("1.00")
    MIN_SHARE_AMOUNT = Decimal("0.000001")  # 1/1,000,000 of a share
    
    def __init__(self):
        self.active_orders: Dict[str, FractionalOrder] = {}
        self.position_holdings: Dict[str, Dict[str, Decimal]] = {}  # user_id -> symbol -> shares
        self.price_cache: Dict[str, Decimal] = {}
    
    async def place_fractional_order(
        self,
        user_id: str,
        symbol: str,
        side: OrderSide,
        dollar_amount: Optional[float] = None,
        share_amount: Optional[float] = None,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[float] = None
    ) -> FractionalOrder:
        """
        Place a fractional share order
        
        Either dollar_amount OR share_amount must be specified
        
        Args:
            user_id: User placing order
            symbol: Stock symbol
            side: buy or sell
            dollar_amount: Dollar amount to invest (e.g., $50 of AAPL)
            share_amount: Share amount (e.g., 0.5 shares)
            order_type: Market, limit, etc.
            limit_price: Limit price if order_type is LIMIT
        """
        # Validate symbol supports fractional
        if symbol not in self.SUPPORTED_FRACTIONAL_ASSETS:
            raise ValueError(f"{symbol} does not support fractional trading")
        
        # Validate amount specified
        if dollar_amount is None and share_amount is None:
            raise ValueError("Either dollar_amount or share_amount must be specified")
        
        if dollar_amount is not None and share_amount is not None:
            raise ValueError("Cannot specify both dollar_amount and share_amount")
        
        # Validate minimums
        if dollar_amount and Decimal(str(dollar_amount)) < self.MIN_DOLLAR_AMOUNT:
            raise ValueError(f"Minimum order size is ${self.MIN_DOLLAR_AMOUNT}")
        
        if share_amount and Decimal(str(share_amount)) < self.MIN_SHARE_AMOUNT:
            raise ValueError(f"Minimum share amount is {self.MIN_SHARE_AMOUNT}")
        
        # Create order
        order = FractionalOrder(
            order_id=f"frac_{user_id}_{symbol}_{datetime.utcnow().timestamp()}",
            user_id=user_id,
            symbol=symbol,
            side=side,
            dollar_amount=Decimal(str(dollar_amount)) if dollar_amount else None,
            share_amount=Decimal(str(share_amount)) if share_amount else None,
            order_type=order_type,
            limit_price=Decimal(str(limit_price)) if limit_price else None
        )
        
        self.active_orders[order.order_id] = order
        
        # Execute order (mock - in production use actual broker API)
        await self._execute_order(order)
        
        return order
    
    async def _execute_order(self, order: FractionalOrder):
        """Execute the fractional order"""
        # Get current price
        current_price = await self._get_current_price(order.symbol)
        
        if order.dollar_amount:
            # Dollar-based order: calculate shares
            shares = (order.dollar_amount / current_price).quantize(
                Decimal("0.000001"), rounding=ROUND_DOWN
            )
            actual_dollar_amount = shares * current_price
        else:
            # Share-based order: calculate dollar amount
            shares = order.share_amount
            actual_dollar_amount = shares * current_price
        
        # Update order
        order.filled_shares = shares
        order.filled_dollar_amount = actual_dollar_amount
        order.avg_fill_price = current_price
        order.status = "filled"
        order.filled_at = datetime.utcnow()
        
        # Update holdings
        await self._update_holdings(order)
    
    async def _get_current_price(self, symbol: str) -> Decimal:
        """Get current market price for symbol"""
        # In production: fetch from real-time data feed
        mock_prices = {
            "AAPL": Decimal("175.50"),
            "MSFT": Decimal("380.25"),
            "GOOGL": Decimal("142.80"),
            "AMZN": Decimal("178.90"),
            "TSLA": Decimal("245.60"),
            "BTC": Decimal("65000.00"),
            "ETH": Decimal("3400.00")
        }
        return mock_prices.get(symbol, Decimal("100.00"))
    
    async def _update_holdings(self, order: FractionalOrder):
        """Update user's position holdings"""
        if order.user_id not in self.position_holdings:
            self.position_holdings[order.user_id] = {}
        
        current_shares = self.position_holdings[order.user_id].get(order.symbol, Decimal("0"))
        
        if order.side == OrderSide.BUY:
            new_shares = current_shares + order.filled_shares
        else:
            new_shares = current_shares - order.filled_shares
        
        self.position_holdings[order.user_id][order.symbol] = new_shares
    
    async def get_fractional_holdings(self, user_id: str) -> Dict[str, Any]:
        """Get all fractional holdings for a user"""
        holdings = self.position_holdings.get(user_id, {})
        
        result = {}
        for symbol, shares in holdings.items():
            if shares > 0:
                price = await self._get_current_price(symbol)
                value = shares * price
                result[symbol] = {
                    "shares": float(shares),
                    "current_price": float(price),
                    "market_value": float(value),
                    "is_fractional": shares % 1 != 0
                }
        
        return result
    
    async def get_available_fractional_stocks(self) -> List[Dict[str, Any]]:
        """Get list of stocks available for fractional trading"""
        stocks = []
        for symbol in self.SUPPORTED_FRACTIONAL_ASSETS:
            price = await self._get_current_price(symbol)
            stocks.append({
                "symbol": symbol,
                "current_price": float(price),
                "min_dollar_amount": float(self.MIN_DOLLAR_AMOUNT),
                "min_shares": float(self.MIN_SHARE_AMOUNT),
                "supports_fractional": True
            })
        
        return stocks
    
    async def calculate_drip_eligibility(
        self,
        user_id: str,
        symbol: str,
        dividend_amount: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate DRIP (Dividend Reinvestment Plan) eligibility
        """
        price = await self._get_current_price(symbol)
        shares_to_buy = (dividend_amount / price).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
        remaining_cash = dividend_amount - (shares_to_buy * price)
        
        return {
            "symbol": symbol,
            "dividend_amount": float(dividend_amount),
            "stock_price": float(price),
            "fractional_shares_to_buy": float(shares_to_buy),
            "remaining_cash": float(remaining_cash),
            " drip_enabled": True
        }
