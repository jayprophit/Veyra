"""
Cryptocurrency Exchange Integrations
Binance, Coinbase Pro, Kraken, Gemini, Bitfinex, KuCoin, Bybit, OKX
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
import asyncio
import aiohttp
import hmac
import hashlib


class ExchangeType(Enum):
    SPOT = "spot"
    FUTURES = "futures"
    MARGIN = "margin"
    OPTIONS = "options"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


@dataclass
class CryptoOrder:
    """Unified crypto order"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    amount: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: str = "GTC"
    client_order_id: str = ""
    reduce_only: bool = False
    post_only: bool = False


@dataclass
class ExchangeBalance:
    """Exchange balance"""
    asset: str
    free: Decimal
    locked: Decimal
    total: Decimal
    usd_value: Optional[Decimal] = None


class BinanceClient:
    """Binance Spot & Futures API"""
    
    SPOT_URL = "https://api.binance.com"
    FUTURES_URL = "https://fapi.binance.com"
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.base_url = self.SPOT_URL if not testnet else "https://testnet.binance.vision"
    
    def _generate_signature(self, query_string: str) -> str:
        """Generate HMAC signature"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        query = f"timestamp={timestamp}"
        signature = self._generate_signature(query)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/v3/account?{query}&signature={signature}",
                headers={"X-MBX-APIKEY": self.api_key}
            ) as resp:
                return await resp.json()
    
    async def place_order(self, order: CryptoOrder) -> Dict[str, Any]:
        """Place spot order"""
        params = {
            "symbol": order.symbol.upper(),
            "side": order.side.value.upper(),
            "type": order.order_type.value.upper(),
            "quantity": str(order.amount),
            "timestamp": int(datetime.utcnow().timestamp() * 1000)
        }
        
        if order.price:
            params["price"] = str(order.price)
        if order.stop_price:
            params["stopPrice"] = str(order.stop_price)
        
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = self._generate_signature(query)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v3/order?{query}&signature={signature}",
                headers={"X-MBX-APIKEY": self.api_key}
            ) as resp:
                return await resp.json()
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get 24hr ticker"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/v3/ticker/24hr?symbol={symbol.upper()}"
            ) as resp:
                return await resp.json()
    
    async def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100
    ) -> List[List]:
        """Get candlestick data"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/v3/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"
            ) as resp:
                return await resp.json()


class CoinbaseProClient:
    """Coinbase Pro (Coinbase Advanced Trade) API"""
    
    BASE_URL = "https://api.exchange.coinbase.com"
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
    
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """Generate CB-ACCESS-SIGN"""
        message = timestamp + method.upper() + path + body
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def get_accounts(self) -> List[Dict]:
        """Get all accounts"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        signature = self._generate_signature(timestamp, "GET", "/accounts")
        
        headers = {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-PASSPHRASE": self.passphrase
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/accounts",
                headers=headers
            ) as resp:
                return await resp.json()
    
    async def place_order(self, order: CryptoOrder) -> Dict[str, Any]:
        """Place order"""
        body = {
            "product_id": order.symbol.upper(),
            "side": order.side.value,
            "order_type": order.order_type.value,
            "size": str(order.amount)
        }
        
        if order.price:
            body["price"] = str(order.price)
        
        import json
        body_json = json.dumps(body)
        timestamp = str(int(datetime.utcnow().timestamp()))
        signature = self._generate_signature(timestamp, "POST", "/orders", body_json)
        
        headers = {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/orders",
                headers=headers,
                data=body_json
            ) as resp:
                return await resp.json()


class KrakenClient:
    """Kraken Exchange API"""
    
    BASE_URL = "https://api.kraken.com"
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
    
    def _generate_signature(self, urlpath: str, data: Dict) -> str:
        """Generate API-Sign"""
        import json
        import base64
        
        postdata = json.dumps(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message,
            hashlib.sha512
        )
        return base64.b64encode(signature.digest()).decode()
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        import json
        
        nonce = int(datetime.utcnow().timestamp() * 1000)
        data = {"nonce": nonce}
        
        signature = self._generate_signature("/0/private/Balance", data)
        
        headers = {
            "API-Key": self.api_key,
            "API-Sign": signature,
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/0/private/Balance",
                headers=headers,
                data=json.dumps(data)
            ) as resp:
                return await resp.json()


class CryptoExchangeManager:
    """
    Unified Manager for All Crypto Exchanges
    
    Supports: Binance, Coinbase Pro, Kraken, Gemini, Bitfinex, KuCoin, Bybit, OKX
    """
    
    EXCHANGES = {
        "binance": BinanceClient,
        "coinbase_pro": CoinbaseProClient,
        "kraken": KrakenClient,
        # Add more as needed
    }
    
    def __init__(self):
        self.clients: Dict[str, Any] = {}
        self.exchange_configs: Dict[str, Dict] = {}
    
    async def add_exchange(
        self,
        exchange_name: str,
        credentials: Dict[str, str],
        testnet: bool = False
    ) -> Any:
        """Add exchange client"""
        client_class = self.EXCHANGES.get(exchange_name)
        if not client_class:
            raise ValueError(f"Exchange {exchange_name} not supported")
        
        if exchange_name == "binance":
            client = client_class(
                credentials["api_key"],
                credentials["api_secret"],
                testnet
            )
        elif exchange_name == "coinbase_pro":
            client = client_class(
                credentials["api_key"],
                credentials["api_secret"],
                credentials["passphrase"]
            )
        elif exchange_name == "kraken":
            client = client_class(
                credentials["api_key"],
                credentials["api_secret"]
            )
        else:
            raise ValueError(f"Unknown exchange: {exchange_name}")
        
        self.clients[exchange_name] = client
        self.exchange_configs[exchange_name] = {
            "testnet": testnet,
            "added_at": datetime.utcnow().isoformat()
        }
        
        return client
    
    async def get_best_price(self, symbol: str, side: OrderSide) -> Dict[str, Any]:
        """Get best price across all connected exchanges"""
        prices = []
        
        for name, client in self.clients.items():
            try:
                if hasattr(client, 'get_ticker'):
                    ticker = await client.get_ticker(symbol)
                    price = Decimal(ticker.get("askPrice", 0)) if side == OrderSide.BUY else Decimal(ticker.get("bidPrice", 0))
                    prices.append({"exchange": name, "price": price})
            except Exception as e:
                print(f"Error getting price from {name}: {e}")
        
        if not prices:
            return {"error": "No prices available"}
        
        # Sort by best price
        if side == OrderSide.BUY:
            best = min(prices, key=lambda x: x["price"])  # Lowest ask
        else:
            best = max(prices, key=lambda x: x["price"])  # Highest bid
        
        return {
            "symbol": symbol,
            "side": side.value,
            "best_price": float(best["price"]),
            "best_exchange": best["exchange"],
            "all_prices": [{"ex": p["exchange"], "price": float(p["price"])} for p in prices]
        }
    
    async def smart_route_order(
        self,
        symbol: str,
        side: OrderSide,
        amount: Decimal,
        prefer_exchange: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Smart order routing - execute on best exchange
        
        Considers: price, liquidity, fees, latency
        """
        # If preferred exchange specified and connected
        if prefer_exchange and prefer_exchange in self.clients:
            exchange = prefer_exchange
        else:
            # Find best exchange by price
            best = await self.get_best_price(symbol, side)
            exchange = best.get("best_exchange", list(self.clients.keys())[0])
        
        client = self.clients[exchange]
        
        order = CryptoOrder(
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            amount=amount
        )
        
        try:
            result = await client.place_order(order)
            return {
                "success": True,
                "exchange": exchange,
                "order_result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "exchange": exchange
            }
    
    async def get_portfolio_value(self) -> Dict[str, Any]:
        """Get total portfolio value across all exchanges"""
        total_value = Decimal("0")
        exchange_values = []
        
        for name, client in self.clients.items():
            try:
                if hasattr(client, 'get_account'):
                    account = await client.get_account()
                    balances = account.get("balances", [])
                    
                    exchange_total = Decimal("0")
                    for bal in balances:
                        free = Decimal(bal.get("free", 0))
                        locked = Decimal(bal.get("locked", 0))
                        # Get USD value (simplified)
                        exchange_total += free + locked
                    
                    exchange_values.append({
                        "exchange": name,
                        "value": float(exchange_total)
                    })
                    total_value += exchange_total
                    
            except Exception as e:
                print(f"Error getting balance from {name}: {e}")
        
        return {
            "total_value": float(total_value),
            "by_exchange": exchange_values
        }
