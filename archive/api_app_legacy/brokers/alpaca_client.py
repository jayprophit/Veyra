"""
Alpaca Trading API Integration
Commission-free stock and crypto trading
Paper trading support for testing
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import aiohttp
import asyncio


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class TimeInForce(Enum):
    DAY = "day"
    GTC = "gtc"
    OPG = "opg"  # Opening
    CLS = "cls"  # Closing
    IOC = "ioc"  # Immediate or cancel
    FOK = "fok"  # Fill or kill


@dataclass
class AlpacaOrder:
    """Alpaca order request"""
    symbol: str
    qty: Optional[Decimal] = None
    notional: Optional[Decimal] = None  # Dollar amount
    side: OrderSide = OrderSide.BUY
    type: OrderType = OrderType.MARKET
    time_in_force: TimeInForce = TimeInForce.DAY
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    trail_price: Optional[Decimal] = None
    trail_percent: Optional[float] = None
    extended_hours: bool = False
    client_order_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "symbol": self.symbol,
            "side": self.side.value,
            "type": self.type.value,
            "time_in_force": self.time_in_force.value,
            "extended_hours": self.extended_hours
        }
        
        if self.qty:
            data["qty"] = str(self.qty)
        elif self.notional:
            data["notional"] = str(self.notional)
            
        if self.limit_price:
            data["limit_price"] = str(self.limit_price)
        if self.stop_price:
            data["stop_price"] = str(self.stop_price)
        if self.trail_price:
            data["trail_price"] = str(self.trail_price)
        if self.trail_percent:
            data["trail_percent"] = str(self.trail_percent)
        if self.client_order_id:
            data["client_order_id"] = self.client_order_id
            
        return data


@dataclass
class AlpacaPosition:
    """Alpaca position data"""
    symbol: str
    qty: Decimal
    avg_entry_price: Decimal
    market_value: Decimal
    current_price: Decimal
    unrealized_pl: Decimal
    unrealized_plpc: float
    asset_class: str  # us_equity, crypto
    exchange: str


class AlpacaClient:
    """
    Alpaca Trading API Client
    
    Supports:
    - Paper trading (testing)
    - Live trading (production)
    - Fractional shares
    - Extended hours trading
    - Crypto trading
    """
    
    PAPER_BASE_URL = "https://paper-api.alpaca.markets"
    LIVE_BASE_URL = "https://api.alpaca.markets"
    DATA_URL = "https://data.alpaca.markets"
    
    def __init__(self, api_key: str, api_secret: str, paper: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        self.base_url = self.PAPER_BASE_URL if paper else self.LIVE_BASE_URL
        
        self.headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": api_secret,
            "Content-Type": "application/json"
        }
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the client session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/v2/account",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Account error: {response.status}")
    
    async def submit_order(self, order: AlpacaOrder) -> Dict[str, Any]:
        """Submit a new order"""
        session = await self._get_session()
        
        async with session.post(
            f"{self.base_url}/v2/orders",
            headers=self.headers,
            json=order.to_dict()
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Order error: {error}")
    
    async def get_orders(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get list of orders"""
        session = await self._get_session()
        
        params = {"limit": limit}
        if status:
            params["status"] = status
        if after:
            params["after"] = after.isoformat()
        
        async with session.get(
            f"{self.base_url}/v2/orders",
            headers=self.headers,
            params=params
        ) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        session = await self._get_session()
        
        async with session.delete(
            f"{self.base_url}/v2/orders/{order_id}",
            headers=self.headers
        ) as response:
            return response.status == 204
    
    async def get_positions(self) -> List[AlpacaPosition]:
        """Get all open positions"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/v2/positions",
            headers=self.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                positions = []
                for pos in data:
                    positions.append(AlpacaPosition(
                        symbol=pos["symbol"],
                        qty=Decimal(pos["qty"]),
                        avg_entry_price=Decimal(pos["avg_entry_price"]),
                        market_value=Decimal(pos["market_value"]),
                        current_price=Decimal(pos["current_price"]),
                        unrealized_pl=Decimal(pos["unrealized_pl"]),
                        unrealized_plpc=float(pos["unrealized_plpc"]),
                        asset_class=pos["asset_class"],
                        exchange=pos["exchange"]
                    ))
                return positions
            return []
    
    async def close_position(self, symbol: str) -> Dict[str, Any]:
        """Close all or part of a position"""
        session = await self._get_session()
        
        async with session.delete(
            f"{self.base_url}/v2/positions/{symbol}",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Close position error: {error}")
    
    async def get_portfolio_history(
        self,
        period: str = "1M",  # 1D, 1W, 1M, 3M, 6M, 1A, all
        timeframe: Optional[str] = None  # 1Min, 5Min, 15Min, 1H, 1D
    ) -> Dict[str, Any]:
        """Get portfolio historical data"""
        session = await self._get_session()
        
        params = {"period": period}
        if timeframe:
            params["timeframe"] = timeframe
        
        async with session.get(
            f"{self.base_url}/v2/account/portfolio/history",
            headers=self.headers,
            params=params
        ) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def get_bars(
        self,
        symbols: List[str],
        timeframe: str = "1D",  # 1Min, 5Min, 15Min, 1H, 1D
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get historical bar data"""
        session = await self._get_session()
        
        symbols_str = ",".join(symbols)
        
        params = {
            "symbols": symbols_str,
            "timeframe": timeframe,
            "limit": limit
        }
        if start:
            params["start"] = start.isoformat()
        if end:
            params["end"] = end.isoformat()
        
        async with session.get(
            f"{self.DATA_URL}/v2/stocks/bars",
            headers=self.headers,
            params=params
        ) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def get_crypto_quote(self, symbol: str) -> Dict[str, Any]:
        """Get latest crypto quote"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.DATA_URL}/v1beta3/crypto/us/latest/quotes",
            headers=self.headers,
            params={"symbols": symbol}
        ) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def get_clock(self) -> Dict[str, Any]:
        """Get market clock (is_open, next_open, next_close)"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/v2/clock",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def get_calendar(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get market calendar"""
        session = await self._get_session()
        
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        
        async with session.get(
            f"{self.base_url}/v2/calendar",
            headers=self.headers,
            params=params
        ) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def get_trades(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get latest trades (for last price)"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.DATA_URL}/v2/stocks/trades/latest",
            headers=self.headers,
            params={"symbols": symbol}
        ) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def get_corporate_actions(
        self,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get corporate actions (splits, dividends, mergers)"""
        session = await self._get_session()
        
        params = {}
        if since:
            params["since"] = since.isoformat()
        
        async with session.get(
            f"{self.base_url}/v2/corporate_actions",
            headers=self.headers,
            params=params
        ) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def stream_trades(self, symbols: List[str]):
        """
        Stream real-time trades via WebSocket
        
        Yields trade updates for subscribed symbols
        """
        # WebSocket URL
        ws_url = "wss://stream.data.alpaca.markets/v2/iex"  # or /v2/sip for pro
        
        import websockets
        
        auth_msg = {
            "action": "auth",
            "key": self.api_key,
            "secret": self.api_secret
        }
        
        subscribe_msg = {
            "action": "subscribe",
            "trades": symbols,
            "quotes": [],
            "bars": []
        }
        
        async with websockets.connect(ws_url) as ws:
            # Authenticate
            await ws.send(json.dumps(auth_msg))
            auth_response = await ws.recv()
            
            # Subscribe to trades
            await ws.send(json.dumps(subscribe_msg))
            
            while True:
                try:
                    message = await ws.recv()
                    data = json.loads(message)
                    yield data
                except websockets.exceptions.ConnectionClosed:
                    break


import json
