"""Financial Master - WebSocket Real-Time Data Feeds. Cost: £0 (free tier)."""

import os, json, asyncio, websockets, aiohttp
from typing import Optional, Dict, List, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WebSocketFeeds')

class DataProvider(Enum):
    FINNHUB = "finnhub"
    POLYGON = "polygon"
    ALPACA = "alpaca"
    MOCK = "mock"

@dataclass
class WebSocketConfig:
    primary_provider: DataProvider = DataProvider.MOCK
    finnhub_api_key: Optional[str] = None
    finnhub_ws_url: str = "wss://ws.finnhub.io?token={api_key}"
    reconnect_interval: int = 5
    max_reconnect_attempts: int = 10
    default_tickers: List[str] = field(default_factory=lambda: ["VUAG", "AGGH", "AYEM", "HMWO"])
    mock_update_interval: float = 2.0

@dataclass
class PriceTick:
    ticker: str
    price: float
    timestamp: datetime
    volume: Optional[int] = None
    change: Optional[float] = None
    source: str = "unknown"
    def to_dict(self): return {"ticker": self.ticker, "price": self.price, "timestamp": self.timestamp.isoformat(), "volume": self.volume, "change": self.change, "source": self.source}

class BaseWebSocketClient:
    def __init__(self, config: WebSocketConfig):
        self.config = config
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self._callbacks: List[Callable[[PriceTick], None]] = []
        self._subscribed: Set[str] = set()
        self._stop_event = asyncio.Event()
    def on_tick(self, cb: Callable[[PriceTick], None]): self._callbacks.append(cb)
    def _notify(self, tick: PriceTick):
        for cb in self._callbacks:
            try: cb(tick)
            except Exception as e: logger.error(f"Callback error: {e}")
    async def run(self):
        while not self._stop_event.is_set():
            try:
                if not self.connected: await self._connect()
                if self.connected: await self._receive()
            except Exception as e:
                logger.error(f"{self.__class__.__name__} error: {e}")
                self.connected = False
            if not self._stop_event.is_set():
                wait = min(self.config.reconnect_interval * (2 ** self.reconnect_attempts), 60)
                await asyncio.sleep(wait)
    async def _connect(self): raise NotImplementedError
    async def _receive(self): raise NotImplementedError
    def stop(self): self._stop_event.set(); self.connected = False

class MockWebSocketClient(BaseWebSocketClient):
    """Mock client for testing without API keys."""
    async def _connect(self): self.connected = True; logger.info("Mock connected")
    async def _receive(self):
        base_prices = {"VUAG": 85.50, "AGGH": 92.30, "AYEM": 78.45, "HMWO": 156.20}
        current = base_prices.copy()
        while not self._stop_event.is_set():
            for ticker in self.config.default_tickers:
                if ticker not in current: current[ticker] = 100.0
                import random
                change = (random.random() - 0.5) * 0.004
                current[ticker] *= (1 + change)
                self._notify(PriceTick(ticker, round(current[ticker], 2), datetime.now(), int(random.random()*10000), round(change*100, 2), "mock"))
            await asyncio.sleep(self.config.mock_update_interval)
    async def subscribe(self, tickers): self._subscribed.update(tickers)

class FinnhubWebSocketClient(BaseWebSocketClient):
    """Finnhub free WebSocket: 60 calls/min, real-time US stocks."""
    async def _connect(self):
        if not self.config.finnhub_api_key: raise ValueError("Finnhub API key required")
        url = self.config.finnhub_ws_url.format(api_key=self.config.finnhub_api_key)
        self.ws = await websockets.connect(url); self.connected = True; logger.info("Finnhub connected")
    async def _receive(self):
        async for msg in self.ws:
            if self._stop_event.is_set(): break
            data = json.loads(msg)
            if data.get("type") == "trade":
                for t in data.get("data", []):
                    self._notify(PriceTick(t.get("s"), t.get("p"), datetime.fromtimestamp(t.get("t",0)/1000), t.get("v"), source="finnhub"))
    async def subscribe(self, tickers):
        for t in tickers: await self.ws.send(json.dumps({"type": "subscribe", "symbol": t})); self._subscribed.add(t)

class WebSocketServer:
    """Server to broadcast price data to React Dashboard."""
    def __init__(self, host="localhost", port=8765):
        self.host, self.port = host, port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.cache: Dict[str, PriceTick] = {}
    async def start(self):
        logger.info(f"WebSocket server on {self.host}:{self.port}")
        async with websockets.serve(self._handle, self.host, self.port):
            await asyncio.Future()
    async def _handle(self, ws, path):
        self.clients.add(ws); logger.info(f"Client connected")
        try:
            if self.cache:
                await ws.send(json.dumps({"type": "snapshot", "data": {t: tick.to_dict() for t, tick in self.cache.items()}}))
            while True:
                try: msg = await asyncio.wait_for(ws.recv(), 30.0); await self._process(ws, msg)
                except asyncio.TimeoutError: await ws.send(json.dumps({"type": "heartbeat"}))
        except websockets.exceptions.ConnectionClosed: logger.info("Client disconnected")
        finally: self.clients.discard(ws)
    async def _process(self, ws, msg):
        try:
            data = json.loads(msg)
            if data.get("type") == "ping": await ws.send(json.dumps({"type": "pong"}))
        except: pass
    def broadcast(self, tick: PriceTick):
        self.cache[tick.ticker] = tick
        msg = json.dumps({"type": "tick", "data": tick.to_dict()})
        bad = {c for c in self.clients if not self._send(c, msg)}
        self.clients -= bad
    def _send(self, client, msg):
        try: asyncio.create_task(client.send(msg)); return True
        except: return False

class DataFeedManager:
    """Central manager routing data from providers to server."""
    def __init__(self, config=None):
        self.config = config or WebSocketConfig()
        self.server = WebSocketServer()
        self.provider: Optional[BaseWebSocketClient] = None
    def setup(self, provider: DataProvider):
        if provider == DataProvider.MOCK: self.provider = MockWebSocketClient(self.config)
        elif provider == DataProvider.FINNHUB: self.provider = FinnhubWebSocketClient(self.config)
        else: raise ValueError(f"Unknown provider: {provider}")
        self.provider.on_tick(self._on_tick)
        return self
    def _on_tick(self, tick: PriceTick): self.server.broadcast(tick)
    async def start(self):
        if not self.provider: self.setup(DataProvider.MOCK)
        await asyncio.gather(self.provider.run(), self.server.start())
    def stop(self):
        if self.provider: self.provider.stop()

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Financial Master - WebSocket Real-Time Feeds")
    print("="*60)
    
    # Mock mode (no API key needed)
    config = WebSocketConfig(primary_provider=DataProvider.MOCK)
    manager = DataFeedManager(config).setup(DataProvider.MOCK)
    
    # Or use Finnhub (get free API key at finnhub.io)
    # config = WebSocketConfig(
    #     primary_provider=DataProvider.FINNHUB,
    #     finnhub_api_key="your_free_api_key"
    # )
    # manager = DataFeedManager(config).setup(DataProvider.FINNHUB)
    
    print("\n✓ Starting WebSocket server...")
    print("  Provider: Mock (simulated data)")
    print("  Server: ws://localhost:8765")
    print("\nConnect from React Dashboard:")
    print('  const ws = new WebSocket("ws://localhost:8765")')
    print("\nPress Ctrl+C to stop\n")
    
    try:
        asyncio.run(manager.start())
    except KeyboardInterrupt:
        print("\n\nStopping...")
        manager.stop()
