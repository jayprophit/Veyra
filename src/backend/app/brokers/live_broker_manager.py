"""
Live Broker Connection Manager
==============================
Manages live connections to Alpaca (trading) and Polygon (market data).
Handles authentication, rate limiting, and real-time data streaming.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import aiohttp
import websockets

logger = logging.getLogger(__name__)


class BrokerStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class BrokerConnection:
    name: str
    status: BrokerStatus
    last_connected: Optional[datetime] = None
    last_error: Optional[str] = None
    api_calls_today: int = 0
    ws_connected: bool = False


class LiveBrokerManager:
    """
    Central manager for all live broker connections.
    Handles Alpaca trading and Polygon market data.
    """
    
    def __init__(self):
        # API Keys from environment
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY', 'PKYOURKEYHERE')
        self.alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY', 'YOURSECRETHERE')
        self.alpaca_base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        self.polygon_api_key = os.getenv('POLYGON_API_KEY', 'YOURPOLYGONKEYHERE')
        self.polygon_base_url = 'https://api.polygon.io'
        
        # Connection states
        self.connections: Dict[str, BrokerConnection] = {
            'alpaca': BrokerConnection('alpaca', BrokerStatus.DISCONNECTED),
            'polygon': BrokerConnection('polygon', BrokerStatus.DISCONNECTED)
        }
        
        # WebSocket connections
        self.alpaca_ws: Optional[websockets.WebSocketClientProtocol] = None
        self.polygon_ws: Optional[websockets.WebSocketClientProtocol] = None
        
        # Callbacks for real-time data
        self.price_callbacks: List[Callable[[str, float], Any]] = []
        self.trade_callbacks: List[Callable[[dict], Any]] = []
        
        # Rate limiting
        self.rate_limits = {
            'alpaca': {'calls': 0, 'reset_time': datetime.now()},
            'polygon': {'calls': 0, 'reset_time': datetime.now()}
        }
        
        self._running = False
        self._reconnect_task = None
    
    async def start(self):
        """Start all live broker connections."""
        logger.info("Starting Live Broker Manager...")
        self._running = True
        
        # Connect to Alpaca
        await self._connect_alpaca()
        
        # Connect to Polygon
        await self._connect_polygon()
        
        # Start reconnection monitor
        self._reconnect_task = asyncio.create_task(self._reconnection_loop())
        
        logger.info("Live Broker Manager started successfully")
    
    async def stop(self):
        """Stop all connections."""
        logger.info("Stopping Live Broker Manager...")
        self._running = False
        
        if self._reconnect_task:
            self._reconnect_task.cancel()
        
        # Close WebSocket connections
        if self.alpaca_ws:
            await self.alpaca_ws.close()
        if self.polygon_ws:
            await self.polygon_ws.close()
        
        logger.info("Live Broker Manager stopped")
    
    async def _connect_alpaca(self):
        """Connect to Alpaca API and WebSocket."""
        try:
            self.connections['alpaca'].status = BrokerStatus.CONNECTING
            
            # Test REST API connection
            async with aiohttp.ClientSession() as session:
                headers = {
                    'APCA-API-KEY-ID': self.alpaca_api_key,
                    'APCA-API-SECRET-KEY': self.alpaca_secret_key
                }
                
                async with session.get(
                    f'{self.alpaca_base_url}/v2/account',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        account_data = await response.json()
                        logger.info(f"Alpaca connected. Account: {account_data.get('account_number')}")
                        
                        self.connections['alpaca'].status = BrokerStatus.CONNECTED
                        self.connections['alpaca'].last_connected = datetime.now()
                        
                        # Connect to WebSocket for real-time updates
                        await self._connect_alpaca_websocket()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Alpaca API error: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            self.connections['alpaca'].status = BrokerStatus.ERROR
            self.connections['alpaca'].last_error = str(e)
    
    async def _connect_alpaca_websocket(self):
        """Connect to Alpaca WebSocket for real-time data."""
        try:
            # Alpaca WebSocket URL
            ws_url = 'wss://stream.data.alpaca.markets/v2/iex'
            
            self.alpaca_ws = await websockets.connect(ws_url)
            
            # Authenticate
            auth_msg = {
                "action": "auth",
                "key": self.alpaca_api_key,
                "secret": self.alpaca_secret_key
            }
            await self.alpaca_ws.send(json.dumps(auth_msg))
            
            # Start listening for messages
            asyncio.create_task(self._listen_alpaca_websocket())
            
            self.connections['alpaca'].ws_connected = True
            logger.info("Alpaca WebSocket connected")
        
        except Exception as e:
            logger.error(f"Alpaca WebSocket error: {e}")
    
    async def _listen_alpaca_websocket(self):
        """Listen for Alpaca WebSocket messages."""
        try:
            while self._running and self.alpaca_ws:
                message = await self.alpaca_ws.recv()
                data = json.loads(message)
                
                for item in data:
                    if item.get('T') == 't':  # Trade update
                        symbol = item.get('S')
                        price = item.get('p')
                        
                        # Notify price callbacks
                        for callback in self.price_callbacks:
                            await callback(symbol, price)
                    
                    elif item.get('T') == 'q':  # Quote update
                        symbol = item.get('S')
                        bid = item.get('bp')
                        ask = item.get('ap')
                        
                        logger.debug(f"Quote: {symbol} Bid: {bid} Ask: {ask}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Alpaca WebSocket closed")
            self.connections['alpaca'].ws_connected = False
        except Exception as e:
            logger.error(f"Alpaca WebSocket listener error: {e}")
    
    async def _connect_polygon(self):
        """Connect to Polygon API and WebSocket."""
        try:
            self.connections['polygon'].status = BrokerStatus.CONNECTING
            
            # Test REST API connection
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.polygon_base_url}/v1/marketstatus/now',
                    params={'apiKey': self.polygon_api_key}
                ) as response:
                    if response.status == 200:
                        market_data = await response.json()
                        logger.info(f"Polygon connected. Market status: {market_data.get('market')}")
                        
                        self.connections['polygon'].status = BrokerStatus.CONNECTED
                        self.connections['polygon'].last_connected = datetime.now()
                        
                        # Connect to WebSocket
                        await self._connect_polygon_websocket()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Polygon API error: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"Failed to connect to Polygon: {e}")
            self.connections['polygon'].status = BrokerStatus.ERROR
            self.connections['polygon'].last_error = str(e)
    
    async def _connect_polygon_websocket(self):
        """Connect to Polygon WebSocket."""
        try:
            # Polygon WebSocket URL
            ws_url = f'wss://socket.polygon.io/stocks'
            
            self.polygon_ws = await websockets.connect(ws_url)
            
            # Authenticate
            auth_msg = {"action": "auth", "params": self.polygon_api_key}
            await self.polygon_ws.send(json.dumps(auth_msg))
            
            # Start listening
            asyncio.create_task(self._listen_polygon_websocket())
            
            self.connections['polygon'].ws_connected = True
            logger.info("Polygon WebSocket connected")
        
        except Exception as e:
            logger.error(f"Polygon WebSocket error: {e}")
    
    async def _listen_polygon_websocket(self):
        """Listen for Polygon WebSocket messages.""""
        try:
            while self._running and self.polygon_ws:
                message = await self.polygon_ws.recv()
                data = json.loads(message)
                
                for item in data:
                    if item.get('ev') == 'T':  # Trade
                        symbol = item.get('sym')
                        price = item.get('p')
                        
                        for callback in self.price_callbacks:
                            await callback(symbol, price)
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Polygon WebSocket closed")
            self.connections['polygon'].ws_connected = False
        except Exception as e:
            logger.error(f"Polygon WebSocket listener error: {e}")
    
    async def _reconnection_loop(self):
        """Monitor connections and reconnect if needed."""
        while self._running:
            for name, conn in self.connections.items():
                if conn.status in [BrokerStatus.ERROR, BrokerStatus.DISCONNECTED]:
                    logger.info(f"Attempting to reconnect to {name}...")
                    
                    if name == 'alpaca':
                        await self._connect_alpaca()
                    elif name == 'polygon':
                        await self._connect_polygon()
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    # === Public API Methods ===
    
    def on_price_update(self, callback: Callable[[str, float], Any]):
        """Register callback for price updates."""
        self.price_callbacks.append(callback)
    
    def on_trade_update(self, callback: Callable[[dict], Any]):
        """Register callback for trade updates."""
        self.trade_callbacks.append(callback)
    
    async def get_account_info(self) -> Optional[dict]:
        """Get Alpaca account information."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'APCA-API-KEY-ID': self.alpaca_api_key,
                    'APCA-API-SECRET-KEY': self.alpaca_secret_key
                }
                
                async with session.get(
                    f'{self.alpaca_base_url}/v2/account',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get account info: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    async def get_positions(self) -> List[dict]:
        """Get current positions from Alpaca."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'APCA-API-KEY-ID': self.alpaca_api_key,
                    'APCA-API-SECRET-KEY': self.alpaca_secret_key
                }
                
                async with session.get(
                    f'{self.alpaca_base_url}/v2/positions',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get positions: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    async def submit_order(self, symbol: str, qty: float, side: str, 
                          order_type: str = 'market', time_in_force: str = 'day') -> Optional[dict]:
        """Submit order to Alpaca."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'APCA-API-KEY-ID': self.alpaca_api_key,
                    'APCA-API-SECRET-KEY': self.alpaca_secret_key,
                    'Content-Type': 'application/json'
                }
                
                order_data = {
                    'symbol': symbol,
                    'qty': str(qty),
                    'side': side,
                    'type': order_type,
                    'time_in_force': time_in_force
                }
                
                async with session.post(
                    f'{self.alpaca_base_url}/v2/orders',
                    headers=headers,
                    json=order_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Order submitted: {result.get('id')}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Order failed: {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            return None
    
    async def get_stock_quote(self, symbol: str) -> Optional[dict]:
        """Get real-time stock quote from Polygon."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.polygon_base_url}/v2/last/trade/{symbol}',
                    params={'apiKey': self.polygon_api_key}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get quote for {symbol}: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"Error getting quote: {e}")
            return None
    
    async def subscribe_to_symbols(self, symbols: List[str]):
        """Subscribe to real-time data for symbols."""
        # Alpaca subscription
        if self.alpaca_ws and self.connections['alpaca'].ws_connected:
            subscribe_msg = {
                "action": "subscribe",
                "trades": symbols,
                "quotes": symbols,
                "bars": symbols
            }
            await self.alpaca_ws.send(json.dumps(subscribe_msg))
            logger.info(f"Subscribed to {symbols} on Alpaca")
        
        # Polygon subscription
        if self.polygon_ws and self.connections['polygon'].ws_connected:
            subscribe_msg = {"action": "subscribe", "params": f"T.{','.join(symbols)}"}
            await self.polygon_ws.send(json.dumps(subscribe_msg))
            logger.info(f"Subscribed to {symbols} on Polygon")
    
    def get_status(self) -> dict:
        """Get connection status for all brokers."""
        return {
            name: {
                'status': conn.status.value,
                'last_connected': conn.last_connected.isoformat() if conn.last_connected else None,
                'last_error': conn.last_error,
                'api_calls_today': conn.api_calls_today,
                'ws_connected': conn.ws_connected
            }
            for name, conn in self.connections.items()
        }


import json

# Global instance
broker_manager = LiveBrokerManager()
