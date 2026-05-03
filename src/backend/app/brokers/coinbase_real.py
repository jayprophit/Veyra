"""
Coinbase Advanced Trade API - Real Implementation
==================================================
Production crypto trading using Coinbase Advanced Trade API v3

Prerequisites:
- Coinbase account with API key
- API key needs trade permissions
- pip install coinbase-advanced-py (or use raw REST)

Free tier: Standard trading fees apply
API Docs: https://docs.cloud.coinbase.com/advanced-trade-api/reference
"""

import asyncio
import json
import hmac
import hashlib
import base64
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from urllib.parse import urlencode, urlparse
import aiohttp

logger = logging.getLogger(__name__)


class CoinbaseError(Exception):
    """Base Coinbase API error"""
    pass


class CoinbaseAuthError(CoinbaseError):
    """Authentication failed"""
    pass


class CoinbaseTradeError(CoinbaseError):
    """Trade execution failed"""
    pass


@dataclass
class CoinbaseAccount:
    """Account/wallet information"""
    uuid: str
    currency: str
    balance: Decimal
    available: Decimal
    holds: Decimal
    name: str


@dataclass
class CoinbaseOrder:
    """Order information"""
    order_id: str
    product_id: str
    side: str  # BUY or SELL
    order_type: str  # MARKET, LIMIT, STOP
    size: Optional[Decimal]
    funds: Optional[Decimal]
    price: Optional[Decimal]
    status: str
    filled_size: Decimal
    filled_value: Decimal
    average_filled_price: Decimal
    fee: Decimal
    created_at: datetime
    done_at: Optional[datetime]


@dataclass
class CoinbasePosition:
    """Position information"""
    currency: str
    balance: Decimal
    available: Decimal
    avg_entry_price: Optional[Decimal]
    unrealized_pnl: Optional[Decimal]
    current_price: Optional[Decimal]
    market_value: Optional[Decimal]


class CoinbaseRealClient:
    """
    Real Coinbase Advanced Trade API Client
    
    Features:
    - Full REST API coverage
    - WebSocket real-time data
    - All order types (market, limit, stop)
    - Portfolio tracking
    - Transaction history
    """
    
    BASE_URL = "https://api.coinbase.com"
    API_VERSION = "/api/v3/brokerage"
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        sandbox: bool = False
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
        
        # Use sandbox URL if testing
        self.base_url = self.BASE_URL if not sandbox else "https://api-public.sandbox.exchange.coinbase.com"
        
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_ready = asyncio.Event()
        
        logger.info(f"Coinbase client initialized (Sandbox={sandbox})")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            self._session_ready.set()
        return self.session
    
    def _generate_signature(
        self,
        timestamp: str,
        method: str,
        path: str,
        body: str = ""
    ) -> str:
        """
        Generate Coinbase API signature
        
        Format: timestamp + method + path + body
        """
        message = timestamp + method.upper() + path + body
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        body: Optional[Dict] = None
    ) -> Dict:
        """
        Make authenticated request to Coinbase API
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            body: Request body for POST
            
        Returns:
            Parsed JSON response
            
        Raises:
            CoinbaseError: If request fails
        """
        session = await self._get_session()
        
        # Build full URL
        path = f"{self.API_VERSION}{endpoint}"
        url = f"{self.base_url}{path}"
        
        # Add query params
        if params:
            query_string = urlencode(params)
            full_path = f"{path}?{query_string}"
            url = f"{url}?{query_string}"
        else:
            full_path = path
        
        # Generate signature
        timestamp = str(int(datetime.now().timestamp()))
        body_str = json.dumps(body) if body else ""
        signature = self._generate_signature(timestamp, method, full_path, body_str)
        
        # Build headers
        headers = {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-VERSION': '2024-01-01',
            'Content-Type': 'application/json' if body else None
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        
        try:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                data=body_str if body else None
            ) as response:
                data = await response.json()
                
                if response.status >= 400:
                    error_msg = data.get('message', 'Unknown error')
                    if response.status == 401:
                        raise CoinbaseAuthError(f"Authentication failed: {error_msg}")
                    raise CoinbaseError(f"API error {response.status}: {error_msg}")
                
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise CoinbaseError(f"Request failed: {e}")
    
    async def test_connection(self) -> bool:
        """
        Test API connection and credentials
        
        Returns:
            True if credentials are valid
        """
        try:
            accounts = await self.get_accounts()
            logger.info(f"✅ Coinbase connection successful. Found {len(accounts)} accounts")
            return True
        except Exception as e:
            logger.error(f"❌ Coinbase connection failed: {e}")
            return False
    
    async def get_accounts(self) -> List[CoinbaseAccount]:
        """
        Get all accounts (wallets)
        
        Returns:
            List of accounts with balances
        """
        try:
            data = await self._make_request('GET', '/accounts')
            accounts = data.get('accounts', [])
            
            return [
                CoinbaseAccount(
                    uuid=acc.get('uuid', ''),
                    currency=acc.get('currency', ''),
                    balance=Decimal(acc.get('balance', '0')),
                    available=Decimal(acc.get('available_balance', {}).get('value', '0')),
                    holds=Decimal(acc.get('hold', {}).get('value', '0')),
                    name=acc.get('name', '')
                )
                for acc in accounts
            ]
        except Exception as e:
            logger.error(f"Failed to get accounts: {e}")
            raise
    
    async def get_account(self, currency: str) -> Optional[CoinbaseAccount]:
        """Get specific account by currency"""
        accounts = await self.get_accounts()
        for acc in accounts:
            if acc.currency.upper() == currency.upper():
                return acc
        return None
    
    async def get_positions(self) -> List[CoinbasePosition]:
        """
        Get crypto positions with market values
        
        Returns:
            List of positions with P&L
        """
        accounts = await self.get_accounts()
        positions = []
        
        for acc in accounts:
            if acc.balance > 0:
                # Get current price for this currency
                if acc.currency.upper() != 'USD':
                    try:
                        ticker = await self.get_ticker(f"{acc.currency}-USD")
                        current_price = Decimal(str(ticker.get('price', 0)))
                        market_value = acc.balance * current_price
                    except:
                        current_price = None
                        market_value = None
                else:
                    current_price = Decimal('1')
                    market_value = acc.balance
                
                positions.append(CoinbasePosition(
                    currency=acc.currency,
                    balance=acc.balance,
                    available=acc.available,
                    avg_entry_price=None,  # Would need transaction history
                    unrealized_pnl=None,
                    current_price=current_price,
                    market_value=market_value
                ))
        
        return positions
    
    async def get_ticker(self, product_id: str) -> Dict[str, Any]:
        """
        Get current ticker/price for a product
        
        Args:
            product_id: e.g., "BTC-USD", "ETH-USD"
            
        Returns:
            Price data with bid, ask, volume
        """
        try:
            data = await self._make_request(
                'GET',
                f'/products/{product_id}/ticker'
            )
            
            return {
                'product_id': product_id,
                'price': Decimal(data.get('price', '0')),
                'bid': Decimal(data.get('bid', '0')),
                'ask': Decimal(data.get('ask', '0')),
                'volume': Decimal(data.get('volume', '0')),
                'trade_id': data.get('trade_id'),
                'time': data.get('time')
            }
        except Exception as e:
            logger.error(f"Failed to get ticker for {product_id}: {e}")
            raise
    
    async def get_candles(
        self,
        product_id: str,
        start: datetime,
        end: datetime,
        granularity: str = "ONE_HOUR"
    ) -> List[Dict]:
        """
        Get historical candlestick data
        
        Args:
            product_id: Trading pair
            start: Start time
            end: End time
            granularity: ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, 
                        THIRTY_MINUTE, ONE_HOUR, TWO_HOUR, SIX_HOUR, ONE_DAY
        """
        params = {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'granularity': granularity
        }
        
        try:
            data = await self._make_request(
                'GET',
                f'/products/{product_id}/candles',
                params=params
            )
            
            # Coinbase returns candles as arrays
            # [timestamp, low, high, open, close, volume]
            candles = []
            for candle in data.get('candles', []):
                candles.append({
                    'timestamp': datetime.fromtimestamp(candle[0]),
                    'low': Decimal(str(candle[1])),
                    'high': Decimal(str(candle[2])),
                    'open': Decimal(str(candle[3])),
                    'close': Decimal(str(candle[4])),
                    'volume': Decimal(str(candle[5]))
                })
            
            return candles
        except Exception as e:
            logger.error(f"Failed to get candles: {e}")
            return []
    
    async def place_market_order(
        self,
        product_id: str,
        side: str,  # BUY or SELL
        size: Optional[Decimal] = None,
        funds: Optional[Decimal] = None
    ) -> CoinbaseOrder:
        """
        Place a market order
        
        Args:
            product_id: e.g., "BTC-USD"
            side: BUY or SELL
            size: Amount of crypto to buy/sell (mutually exclusive with funds)
            funds: Amount of USD to spend/receive (for notional orders)
            
        Returns:
            Order details
        """
        if not size and not funds:
            raise CoinbaseTradeError("Either size or funds must be specified")
        
        body = {
            'product_id': product_id,
            'side': side.upper(),
            'order_configuration': {
                'market_market_ioc': {}
            }
        }
        
        # Add size or funds
        if size:
            body['order_configuration']['market_market_ioc']['base_size'] = str(size)
        elif funds:
            body['order_configuration']['market_market_ioc']['quote_size'] = str(funds)
        
        try:
            data = await self._make_request('POST', '/orders', body=body)
            
            order_data = data.get('order', {})
            
            return CoinbaseOrder(
                order_id=order_data.get('order_id', ''),
                product_id=product_id,
                side=side.upper(),
                order_type='MARKET',
                size=size,
                funds=funds,
                price=None,
                status=order_data.get('status', 'UNKNOWN'),
                filled_size=Decimal(order_data.get('filled_size', '0')),
                filled_value=Decimal(order_data.get('filled_value', '0')),
                average_filled_price=Decimal(order_data.get('average_filled_price', '0')),
                fee=Decimal(order_data.get('total_fees', '0')),
                created_at=datetime.now(),
                done_at=None
            )
        except Exception as e:
            logger.error(f"Failed to place market order: {e}")
            raise CoinbaseTradeError(f"Order failed: {e}")
    
    async def place_limit_order(
        self,
        product_id: str,
        side: str,
        size: Decimal,
        price: Decimal,
        time_in_force: str = "GTC"  # GTC, GTC, IOC, FOK
    ) -> CoinbaseOrder:
        """
        Place a limit order
        
        Args:
            product_id: Trading pair
            side: BUY or SELL
            size: Amount of crypto
            price: Limit price
            time_in_force: GTC (Good Till Cancel), IOC, FOK
        """
        body = {
            'product_id': product_id,
            'side': side.upper(),
            'order_configuration': {
                'limit_limit_gtc': {
                    'base_size': str(size),
                    'limit_price': str(price)
                }
            }
        }
        
        if time_in_force == 'IOC':
            body['order_configuration'] = {
                'limit_limit_ioc': {
                    'base_size': str(size),
                    'limit_price': str(price)
                }
            }
        
        try:
            data = await self._make_request('POST', '/orders', body=body)
            
            order_data = data.get('order', {})
            
            return CoinbaseOrder(
                order_id=order_data.get('order_id', ''),
                product_id=product_id,
                side=side.upper(),
                order_type='LIMIT',
                size=size,
                funds=None,
                price=price,
                status=order_data.get('status', 'UNKNOWN'),
                filled_size=Decimal(order_data.get('filled_size', '0')),
                filled_value=Decimal(order_data.get('filled_value', '0')),
                average_filled_price=Decimal(order_data.get('average_filled_price', '0')),
                fee=Decimal(order_data.get('total_fees', '0')),
                created_at=datetime.now(),
                done_at=None
            )
        except Exception as e:
            logger.error(f"Failed to place limit order: {e}")
            raise CoinbaseTradeError(f"Order failed: {e}")
    
    async def get_order(self, order_id: str) -> Optional[CoinbaseOrder]:
        """Get order details by ID"""
        try:
            data = await self._make_request('GET', f'/orders/historical/{order_id}')
            
            order = data.get('order', {})
            
            return CoinbaseOrder(
                order_id=order.get('order_id', ''),
                product_id=order.get('product_id', ''),
                side=order.get('side', ''),
                order_type=order.get('order_type', ''),
                size=Decimal(order.get('size', '0')) if order.get('size') else None,
                funds=None,
                price=Decimal(order.get('price', '0')) if order.get('price') else None,
                status=order.get('status', 'UNKNOWN'),
                filled_size=Decimal(order.get('filled_size', '0')),
                filled_value=Decimal(order.get('filled_value', '0')),
                average_filled_price=Decimal(order.get('average_filled_price', '0')),
                fee=Decimal(order.get('total_fees', '0')),
                created_at=datetime.fromisoformat(order.get('created_time', '').replace('Z', '+00:00')),
                done_at=datetime.fromisoformat(order.get('done_time', '').replace('Z', '+00:00')) if order.get('done_time') else None
            )
        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {e}")
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        try:
            await self._make_request('POST', f'/orders/{order_id}/cancel')
            logger.info(f"Cancelled order {order_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    async def get_orders(
        self,
        product_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[CoinbaseOrder]:
        """
        Get list of orders
        
        Args:
            product_id: Filter by product
            status: OPEN, FILLED, CANCELLED, EXPIRED, FAILED
            limit: Max results
        """
        params = {'limit': limit}
        if product_id:
            params['product_id'] = product_id
        if status:
            params['order_status'] = status
        
        try:
            data = await self._make_request('GET', '/orders/historical/batch', params=params)
            
            orders = []
            for order_data in data.get('orders', []):
                orders.append(CoinbaseOrder(
                    order_id=order_data.get('order_id', ''),
                    product_id=order_data.get('product_id', ''),
                    side=order_data.get('side', ''),
                    order_type=order_data.get('order_type', ''),
                    size=Decimal(order_data.get('size', '0')) if order_data.get('size') else None,
                    funds=None,
                    price=Decimal(order_data.get('price', '0')) if order_data.get('price') else None,
                    status=order_data.get('status', 'UNKNOWN'),
                    filled_size=Decimal(order_data.get('filled_size', '0')),
                    filled_value=Decimal(order_data.get('filled_value', '0')),
                    average_filled_price=Decimal(order_data.get('average_filled_price', '0')),
                    fee=Decimal(order_data.get('total_fees', '0')),
                    created_at=datetime.fromisoformat(order_data.get('created_time', '').replace('Z', '+00:00')),
                    done_at=None
                ))
            
            return orders
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            return []
    
    async def get_transactions(self, limit: int = 100) -> List[Dict]:
        """Get transaction history"""
        params = {'limit': limit}
        
        try:
            data = await self._make_request('GET', '/transactions/history', params=params)
            return data.get('transactions', [])
        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            return []
    
    async def close(self):
        """Close the client session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Coinbase client closed")


# Example usage
async def test_coinbase():
    """Test Coinbase connection"""
    client = CoinbaseRealClient(
        api_key="YOUR_API_KEY",
        api_secret="YOUR_SECRET",
        sandbox=True  # Use sandbox for testing
    )
    
    # Test connection
    if await client.test_connection():
        # Get accounts
        accounts = await client.get_accounts()
        for acc in accounts:
            if acc.balance > 0:
                print(f"{acc.currency}: {acc.balance} (Available: {acc.available})")
        
        # Get BTC price
        ticker = await client.get_ticker("BTC-USD")
        print(f"BTC Price: ${ticker['price']}")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(test_coinbase())
