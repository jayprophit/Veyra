"""Polygon.io Live Market Data - Production Ready"""
import os
import json
import asyncio
import websockets
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass
import aiohttp

@dataclass
class Trade:
    symbol: str
    price: float
    size: int
    timestamp: int
    conditions: List[int]

@dataclass
class Quote:
    symbol: str
    bid_price: float
    bid_size: int
    ask_price: float
    ask_size: int
    timestamp: int

class PolygonDataProvider:
    """Production-ready Polygon.io WebSocket and REST API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        if not self.api_key:
            raise ValueError("Polygon API key required. Set POLYGON_API_KEY env var.")
        
        self.ws_url = f"wss://socket.polygon.io/stocks?apiKey={self.api_key}"
        self.rest_url = "https://api.polygon.io/v2"
        self.ws = None
        self.callbacks = {
            'trade': [],
            'quote': [],
            'aggregate': []
        }
        self.subscribed_symbols = set()
        self._running = False
    
    def on_trade(self, callback: Callable[[Trade], None]):
        """Register trade callback."""
        self.callbacks['trade'].append(callback)
    
    def on_quote(self, callback: Callable[[Quote], None]):
        """Register quote callback."""
        self.callbacks['quote'].append(callback)
    
    async def connect(self):
        """Connect to WebSocket."""
        self.ws = await websockets.connect(self.ws_url)
        self._running = True
        
        # Authenticate
        auth_msg = {"action": "auth", "params": self.api_key}
        await self.ws.send(json.dumps(auth_msg))
        
        # Start listening
        asyncio.create_task(self._listen())
    
    async def _listen(self):
        """Listen for messages."""
        while self._running and self.ws:
            try:
                msg = await self.ws.recv()
                data = json.loads(msg)
                await self._handle_message(data)
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
    
    async def _handle_message(self, data: List[Dict]):
        """Handle incoming messages."""
        for msg in data:
            msg_type = msg.get('ev')
            
            if msg_type == 'T':  # Trade
                trade = Trade(
                    symbol=msg['sym'],
                    price=msg['p'],
                    size=msg['s'],
                    timestamp=msg['t'],
                    conditions=msg.get('c', [])
                )
                for cb in self.callbacks['trade']:
                    await cb(trade)
            
            elif msg_type == 'Q':  # Quote
                quote = Quote(
                    symbol=msg['sym'],
                    bid_price=msg['bp'],
                    bid_size=msg['bs'],
                    ask_price=msg['ap'],
                    ask_size=msg['as'],
                    timestamp=msg['t']
                )
                for cb in self.callbacks['quote']:
                    await cb(quote)
    
    async def subscribe_trades(self, symbols: List[str]):
        """Subscribe to real-time trades."""
        symbols_str = ','.join([f'T.{s}' for s in symbols])
        msg = {"action": "subscribe", "params": symbols_str}
        await self.ws.send(json.dumps(msg))
        self.subscribed_symbols.update(symbols)
    
    async def subscribe_quotes(self, symbols: List[str]):
        """Subscribe to real-time quotes."""
        symbols_str = ','.join([f'Q.{s}' for s in symbols])
        msg = {"action": "subscribe", "params": symbols_str}
        await self.ws.send(json.dumps(msg))
    
    async def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from symbols."""
        symbols_str = ','.join(symbols)
        msg = {"action": "unsubscribe", "params": symbols_str}
        await self.ws.send(json.dumps(msg))
        for s in symbols:
            self.subscribed_symbols.discard(s)
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        self._running = False
        if self.ws:
            await self.ws.close()
    
    # REST API Methods
    async def get_last_trade(self, symbol: str) -> Dict:
        """Get last trade via REST."""
        url = f"{self.rest_url}/last/trade/{symbol}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'apiKey': self.api_key}) as resp:
                if resp.status == 200:
                    return await resp.json()
                raise Exception(f"Failed to get last trade: {resp.status}")
    
    async def get_last_quote(self, symbol: str) -> Dict:
        """Get last quote via REST."""
        url = f"{self.rest_url}/last/nbbo/{symbol}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'apiKey': self.api_key}) as resp:
                if resp.status == 200:
                    return await resp.json()
                raise Exception(f"Failed to get last quote: {resp.status}")
    
    async def get_aggregates(self, symbol: str, multiplier: int, timespan: str, 
                              from_date: str, to_date: str) -> List[Dict]:
        """Get aggregate bars (OHLCV)."""
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'apiKey': self.api_key}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('results', [])
                return []
    
    async def get_daily_open_close(self, symbol: str, date: str) -> Dict:
        """Get daily open/close."""
        url = f"https://api.polygon.io/v1/open-close/{symbol}/{date}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'apiKey': self.api_key}) as resp:
                if resp.status == 200:
                    return await resp.json()
                raise Exception(f"Failed to get daily data: {resp.status}")

# Usage example:
# provider = PolygonDataProvider()
# await provider.connect()
# provider.on_trade(lambda trade: print(f"{trade.symbol}: ${trade.price}"))
# await provider.subscribe_trades(['AAPL', 'MSFT', 'TSLA'])
