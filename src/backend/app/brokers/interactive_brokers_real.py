"""
Interactive Brokers (IBKR) Real API Integration
================================================
Production-grade trading via TWS/IB Gateway using ib_insync

Prerequisites:
- TWS or IB Gateway running locally or remotely
- IBKR account with API permissions enabled
- pip install ib_insync

Free tier: Paper trading available at no cost
Live trading: Requires funded IBKR account
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

try:
    from ib_insync import IB, Stock, Crypto, Forex, Future, Option
    from ib_insync import MarketOrder, LimitOrder, StopOrder, BracketOrder
    from ib_insync import util
    IB_INSYNC_AVAILABLE = True
except ImportError:
    IB_INSYNC_AVAILABLE = False
    logging.warning("ib_insync not installed. Run: pip install ib_insync")

logger = logging.getLogger(__name__)


class IBKRConnectionError(Exception):
    """Raised when IBKR connection fails"""
    pass


class IBKROrderError(Exception):
    """Raised when order submission fails"""
    pass


@dataclass
class IBKRPosition:
    """Standardized position data"""
    symbol: str
    quantity: float
    avg_cost: float
    market_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    currency: str
    sec_type: str  # STK, CRYPTO, OPT, FUT, etc.


@dataclass
class IBKROrder:
    """Standardized order data"""
    order_id: str
    symbol: str
    action: str  # BUY, SELL
    quantity: float
    order_type: str  # MKT, LMT, STP
    limit_price: Optional[float]
    stop_price: Optional[float]
    status: str
    filled_quantity: float
    avg_fill_price: float
    commission: float
    currency: str
    submitted_at: datetime


class InteractiveBrokersRealClient:
    """
    Real Interactive Brokers API Client
    
    Features:
    - Connects to TWS or IB Gateway
    - Real-time market data
    - Live order execution
    - Portfolio sync
    - Options, futures, forex support
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7497,  # 7496 for TWS, 7497 for IB Gateway
        client_id: int = 1,
        paper_trading: bool = True
    ):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.paper = paper_trading
        self.ib = None
        self._connected = False
        
        if not IB_INSYNC_AVAILABLE:
            raise ImportError("ib_insync required. Install: pip install ib_insync")
        
        logger.info(f"IBKR Client initialized (Paper={paper_trading})")
    
    async def connect(self, timeout: int = 10) -> bool:
        """
        Connect to TWS/IB Gateway
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connected successfully
            
        Raises:
            IBKRConnectionError: If connection fails
        """
        try:
            self.ib = IB()
            
            # Connect asynchronously
            await self.ib.connectAsync(
                host=self.host,
                port=self.port,
                clientId=self.client_id,
                timeout=timeout
            )
            
            self._connected = self.ib.isConnected()
            
            if self._connected:
                logger.info(f"✅ Connected to IBKR at {self.host}:{self.port}")
                
                # Verify paper trading mode
                if self.paper:
                    account = self.ib.managedAccounts()
                    if account and 'DU' not in account[0]:  # DU = Demo account
                        logger.warning("⚠️ Connected to LIVE account but paper mode requested!")
                
                return True
            else:
                raise IBKRConnectionError("Connection established but not ready")
                
        except Exception as e:
            logger.error(f"❌ IBKR connection failed: {e}")
            raise IBKRConnectionError(f"Failed to connect: {e}")
    
    async def disconnect(self):
        """Disconnect from IBKR"""
        if self.ib and self._connected:
            self.ib.disconnect()
            self._connected = False
            logger.info("Disconnected from IBKR")
    
    async def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account summary including:
        - Net liquidation value
        - Cash balance
        - Buying power
        - Maintenance margin
        - Available funds
        """
        if not self._connected:
            raise IBKRConnectionError("Not connected")
        
        try:
            account_values = self.ib.accountValues()
            
            # Extract key metrics
            summary = {
                "net_liquidation": self._get_account_value(account_values, 'NetLiquidation'),
                "cash": self._get_account_value(account_values, 'CashBalance'),
                "buying_power": self._get_account_value(account_values, 'BuyingPower'),
                "available_funds": self._get_account_value(account_values, 'AvailableFunds'),
                "maintenance_margin": self._get_account_value(account_values, 'MaintMarginReq'),
                "initial_margin": self._get_account_value(account_values, 'InitMarginReq'),
                "currency": 'USD',  # Default, will be updated
                "account_type": 'paper' if self.paper else 'live',
                "account_id": self.ib.managedAccounts()[0] if self.ib.managedAccounts() else None,
                "timestamp": datetime.now().isoformat()
            }
            
            # Get currency from net liquidation
            for av in account_values:
                if av.tag == 'NetLiquidation' and av.currency:
                    summary['currency'] = av.currency
                    break
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get account summary: {e}")
            raise
    
    def _get_account_value(self, account_values: List, tag: str) -> float:
        """Extract numeric value from account values list"""
        for av in account_values:
            if av.tag == tag:
                try:
                    return float(av.value)
                except (ValueError, TypeError):
                    return 0.0
        return 0.0
    
    async def get_positions(self) -> List[IBKRPosition]:
        """
        Get all current positions
        
        Returns:
            List of positions across all asset classes
        """
        if not self._connected:
            raise IBKRConnectionError("Not connected")
        
        try:
            positions = self.ib.positions()
            result = []
            
            for pos in positions:
                contract = pos.contract
                
                # Get current market price
                ticker = self.ib.reqMktData(contract, '', False, False)
                await asyncio.sleep(0.1)  # Brief wait for data
                
                market_price = ticker.last or ticker.close or pos.avgCost
                market_value = pos.position * market_price
                unrealized_pnl = market_value - (pos.position * pos.avgCost)
                
                result.append(IBKRPosition(
                    symbol=contract.symbol,
                    quantity=pos.position,
                    avg_cost=pos.avgCost,
                    market_price=market_price,
                    market_value=market_value,
                    unrealized_pnl=unrealized_pnl,
                    realized_pnl=0.0,  # IB doesn't provide this directly
                    currency=contract.currency,
                    sec_type=contract.secType
                ))
                
                # Cancel market data subscription
                self.ib.cancelMktData(contract)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            raise
    
    async def get_quote(self, symbol: str, sec_type: str = 'STK') -> Dict[str, Any]:
        """
        Get real-time quote for a symbol
        
        Args:
            symbol: Stock/crypto/forex symbol
            sec_type: Security type (STK, CRYPTO, FOREX, etc.)
            
        Returns:
            Quote data with bid, ask, last, volume
        """
        if not self._connected:
            raise IBKRConnectionError("Not connected")
        
        try:
            contract = self._create_contract(symbol, sec_type)
            
            # Request market data
            ticker = self.ib.reqMktData(contract, '', False, False)
            
            # Wait for data (max 2 seconds)
            for _ in range(20):
                if ticker.last or ticker.bid or ticker.ask:
                    break
                await asyncio.sleep(0.1)
            
            quote = {
                "symbol": symbol,
                "sec_type": sec_type,
                "bid": ticker.bid,
                "ask": ticker.ask,
                "last": ticker.last,
                "high": ticker.high,
                "low": ticker.low,
                "volume": ticker.volume,
                "vwap": ticker.vwap,
                "timestamp": datetime.now().isoformat()
            }
            
            # Cancel subscription
            self.ib.cancelMktData(contract)
            
            return quote
            
        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {e}")
            raise
    
    async def place_order(
        self,
        symbol: str,
        action: str,  # BUY or SELL
        quantity: float,
        order_type: str = "MKT",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        sec_type: str = "STK"
    ) -> IBKROrder:
        """
        Place an order
        
        Args:
            symbol: Trading symbol
            action: BUY or SELL
            quantity: Number of shares/contracts
            order_type: MKT, LMT, STP, STP_LMT
            limit_price: Required for limit orders
            stop_price: Required for stop orders
            sec_type: Security type
            
        Returns:
            Order details with ID and status
        """
        if not self._connected:
            raise IBKRConnectionError("Not connected")
        
        try:
            # Create contract
            contract = self._create_contract(symbol, sec_type)
            
            # Create order
            if order_type == "MKT":
                order = MarketOrder(action, quantity)
            elif order_type == "LMT":
                if limit_price is None:
                    raise IBKROrderError("Limit price required for LMT orders")
                order = LimitOrder(action, quantity, limit_price)
            elif order_type == "STP":
                if stop_price is None:
                    raise IBKROrderError("Stop price required for STP orders")
                order = StopOrder(action, quantity, stop_price)
            elif order_type == "STP_LMT":
                if stop_price is None or limit_price is None:
                    raise IBKROrderError("Both stop and limit price required")
                from ib_insync import StopLimitOrder
                order = StopLimitOrder(action, quantity, limit_price, stop_price)
            else:
                raise IBKROrderError(f"Unsupported order type: {order_type}")
            
            # Place order
            trade = self.ib.placeOrder(contract, order)
            
            # Wait briefly for order to be submitted
            await asyncio.sleep(0.2)
            
            # Return order details
            return IBKROrder(
                order_id=str(trade.order.orderId),
                symbol=symbol,
                action=action,
                quantity=quantity,
                order_type=order_type,
                limit_price=limit_price,
                stop_price=stop_price,
                status=trade.orderStatus.status if trade.orderStatus else "Pending",
                filled_quantity=trade.orderStatus.filled if trade.orderStatus else 0,
                avg_fill_price=trade.orderStatus.avgFillPrice if trade.orderStatus else 0,
                commission=0.0,  # Will be updated on fill
                currency=contract.currency,
                submitted_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise IBKROrderError(f"Order failed: {e}")
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        if not self._connected:
            raise IBKRConnectionError("Not connected")
        
        try:
            # Get open orders and find matching ID
            trades = self.ib.openTrades()
            for trade in trades:
                if str(trade.order.orderId) == order_id:
                    self.ib.cancelOrder(trade.order)
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    async def get_order_status(self, order_id: str) -> Optional[IBKROrder]:
        """Get status of a specific order"""
        if not self._connected:
            raise IBKRConnectionError("Not connected")
        
        try:
            trades = self.ib.trades()
            for trade in trades:
                if str(trade.order.orderId) == order_id:
                    return IBKROrder(
                        order_id=order_id,
                        symbol=trade.contract.symbol,
                        action=trade.order.action,
                        quantity=trade.order.totalQuantity,
                        order_type=trade.order.orderType,
                        limit_price=getattr(trade.order, 'lmtPrice', None),
                        stop_price=getattr(trade.order, 'auxPrice', None),
                        status=trade.orderStatus.status,
                        filled_quantity=trade.orderStatus.filled,
                        avg_fill_price=trade.orderStatus.avgFillPrice,
                        commission=sum(c.commission for c in trade.fills) if trade.fills else 0,
                        currency=trade.contract.currency,
                        submitted_at=datetime.now()
                    )
            return None
        except Exception as e:
            logger.error(f"Failed to get order status: {e}")
            return None
    
    async def get_open_orders(self) -> List[IBKROrder]:
        """Get all open orders"""
        if not self._connected:
            raise IBKRConnectionError("Not connected")
        
        try:
            trades = self.ib.openTrades()
            return [
                IBKROrder(
                    order_id=str(trade.order.orderId),
                    symbol=trade.contract.symbol,
                    action=trade.order.action,
                    quantity=trade.order.totalQuantity,
                    order_type=trade.order.orderType,
                    limit_price=getattr(trade.order, 'lmtPrice', None),
                    stop_price=getattr(trade.order, 'auxPrice', None),
                    status=trade.orderStatus.status,
                    filled_quantity=trade.orderStatus.filled,
                    avg_fill_price=trade.orderStatus.avgFillPrice,
                    commission=0.0,
                    currency=trade.contract.currency,
                    submitted_at=datetime.now()
                )
                for trade in trades
            ]
        except Exception as e:
            logger.error(f"Failed to get open orders: {e}")
            return []
    
    async def get_options_chain(self, symbol: str) -> List[Dict]:
        """
        Get options chain for a stock
        
        Returns:
            List of option contracts with strikes and expiries
        """
        if not self._connected:
            raise IBKRConnectionError("Not connected")
        
        try:
            # Create underlying stock contract
            stock = Stock(symbol, 'SMART', 'USD')
            self.ib.qualifyContracts(stock)
            
            # Request option chain
            chains = self.ib.reqSecDefOptParams(
                underlyingSymbol=symbol,
                underlyingSecType='STK',
                underlyingConId=stock.conId,
                futFopExchange=''
            )
            
            if not chains:
                return []
            
            chain = chains[0]  # Use first exchange
            
            options = []
            for expiry in chain.expirations[:10]:  # Limit to 10 expirations
                for strike in chain.strikes:
                    for right in ['C', 'P']:  # Calls and Puts
                        option = Option(symbol, expiry, strike, right, 'SMART')
                        options.append({
                            'symbol': symbol,
                            'expiry': expiry,
                            'strike': strike,
                            'type': 'CALL' if right == 'C' else 'PUT',
                            'exchange': chain.exchange
                        })
            
            return options
            
        except Exception as e:
            logger.error(f"Failed to get options chain: {e}")
            return []
    
    def _create_contract(self, symbol: str, sec_type: str) -> Any:
        """Create appropriate contract based on security type"""
        if sec_type == 'STK':
            return Stock(symbol, 'SMART', 'USD')
        elif sec_type == 'CRYPTO':
            return Crypto(symbol, 'PAXOS', 'USD')
        elif sec_type == 'FOREX':
            return Forex(symbol)
        elif sec_type == 'FUT':
            # Simplified - would need specific expiry
            return Future(symbol, '202412', 'GLOBEX')
        else:
            return Stock(symbol, 'SMART', 'USD')
    
    async def get_portfolio_history(self, days: int = 30) -> List[Dict]:
        """
        Get portfolio value history
        Note: IBKR doesn't provide historical portfolio values directly
        """
        # This would need to be tracked locally in database
        logger.warning("Portfolio history not available from IBKR directly - track locally")
        return []
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to IBKR"""
        return self._connected and self.ib and self.ib.isConnected()


# Convenience async context manager
class IBKRConnection:
    """Async context manager for IBKR connections"""
    
    def __init__(self, **kwargs):
        self.client = InteractiveBrokersRealClient(**kwargs)
    
    async def __aenter__(self):
        await self.client.connect()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()


# Example usage
async def test_ibkr():
    """Test IBKR connection"""
    async with IBKRConnection(
        host="127.0.0.1",
        port=7497,
        client_id=1,
        paper_trading=True
    ) as ib:
        # Get account summary
        account = await ib.get_account_summary()
        print(f"Account: {account}")
        
        # Get positions
        positions = await ib.get_positions()
        print(f"Positions: {len(positions)}")
        
        # Get quote
        quote = await ib.get_quote('AAPL')
        print(f"AAPL Quote: {quote}")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_ibkr())
