"""
Live Data Integration Manager
=============================
Centralized manager for all real-time data feeds
Polygon.io, IEX Cloud, Alpha Vantage, Coinbase Pro
"""

import asyncio
import aiohttp
import websockets
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class PriceUpdate:
    """Real-time price update"""
    ticker: str
    price: float
    bid: float
    ask: float
    volume: int
    timestamp: datetime
    source: str


class LiveDataManager:
    """
    Unified live data feed manager
    
    Supports:
    - Polygon.io (stocks, options, crypto)
    - IEX Cloud (real-time US equities)
    - Alpha Vantage (forex, crypto)
    - Coinbase Pro (crypto)
    - WebSocket connections for real-time streaming
    """
    
    def __init__(self):
        self.api_keys = {
            'polygon': None,
            'iex': None,
            'alpha_vantage': None,
            'coinbase': None
        }
        
        self.price_cache: Dict[str, PriceUpdate] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.websocket_connections: Dict[str, any] = {}
        self.session: Optional[aiohttp.ClientSession] = None
    
    def set_api_keys(self, polygon: str = None, iex: str = None, 
                    alpha_vantage: str = None, coinbase: str = None):
        """Set API keys for data providers"""
        self.api_keys['polygon'] = polygon
        self.api_keys['iex'] = iex
        self.api_keys['alpha_vantage'] = alpha_vantage
        self.api_keys['coinbase'] = coinbase
        
        logger.info("API keys configured")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_polygon_quote(self, ticker: str) -> Optional[PriceUpdate]:
        """Fetch real-time quote from Polygon.io"""
        if not self.api_keys['polygon']:
            logger.warning("Polygon API key not set")
            return None
        
        url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}"
        
        try:
            async with self.session.get(
                url, 
                params={'apiKey': self.api_keys['polygon']}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ticker_data = data.get('ticker', {})
                    
                    return PriceUpdate(
                        ticker=ticker,
                        price=ticker_data.get('lastQuote', {}).get('p', 0),
                        bid=ticker_data.get('lastQuote', {}).get('P', 0),
                        ask=ticker_data.get('lastQuote', {}).get('p', 0),
                        volume=ticker_data.get('day', {}).get('v', 0),
                        timestamp=datetime.now(),
                        source='polygon'
                    )
                else:
                    logger.error(f"Polygon API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching Polygon data: {e}")
            return None
    
    async def fetch_iex_quote(self, ticker: str) -> Optional[PriceUpdate]:
        """Fetch real-time quote from IEX Cloud"""
        if not self.api_keys['iex']:
            logger.warning("IEX API key not set")
            return None
        
        url = f"https://cloud.iexapis.com/stable/stock/{ticker}/quote"
        
        try:
            async with self.session.get(
                url,
                params={'token': self.api_keys['iex']}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return PriceUpdate(
                        ticker=ticker,
                        price=data.get('latestPrice', 0),
                        bid=data.get('iexBidPrice', 0),
                        ask=data.get('iexAskPrice', 0),
                        volume=data.get('latestVolume', 0),
                        timestamp=datetime.now(),
                        source='iex'
                    )
                else:
                    logger.error(f"IEX API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching IEX data: {e}")
            return None
    
    async def fetch_alpha_vantage_quote(self, ticker: str) -> Optional[PriceUpdate]:
        """Fetch quote from Alpha Vantage"""
        if not self.api_keys['alpha_vantage']:
            logger.warning("Alpha Vantage API key not set")
            return None
        
        url = "https://www.alphavantage.co/query"
        
        try:
            async with self.session.get(
                url,
                params={
                    'function': 'GLOBAL_QUOTE',
                    'symbol': ticker,
                    'apikey': self.api_keys['alpha_vantage']
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data.get('Global Quote', {})
                    
                    return PriceUpdate(
                        ticker=ticker,
                        price=float(quote.get('05. price', 0)),
                        bid=float(quote.get('05. price', 0)) * 0.999,
                        ask=float(quote.get('05. price', 0)) * 1.001,
                        volume=int(quote.get('06. volume', 0)),
                        timestamp=datetime.now(),
                        source='alpha_vantage'
                    )
                else:
                    logger.error(f"Alpha Vantage API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data: {e}")
            return None
    
    async def fetch_coinbase_quote(self, product: str) -> Optional[PriceUpdate]:
        """Fetch crypto quote from Coinbase Pro"""
        url = f"https://api.exchange.coinbase.com/products/{product}/ticker"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return PriceUpdate(
                        ticker=product,
                        price=float(data.get('price', 0)),
                        bid=float(data.get('bid', 0)),
                        ask=float(data.get('ask', 0)),
                        volume=int(float(data.get('volume', 0))),
                        timestamp=datetime.now(),
                        source='coinbase'
                    )
                else:
                    logger.error(f"Coinbase API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching Coinbase data: {e}")
            return None
    
    async def get_best_quote(self, ticker: str) -> Optional[PriceUpdate]:
        """Get best available quote from any source"""
        
        # Try sources in order of preference
        sources = [
            ('polygon', self.fetch_polygon_quote),
            ('iex', self.fetch_iex_quote),
            ('alpha_vantage', self.fetch_alpha_vantage_quote)
        ]
        
        for source_name, fetch_func in sources:
            if self.api_keys.get(source_name):
                quote = await fetch_func(ticker)
                if quote:
                    self.price_cache[ticker] = quote
                    return quote
        
        # Fallback: Return cached data if available
        if ticker in self.price_cache:
            logger.warning(f"Using cached data for {ticker}")
            return self.price_cache[ticker]
        
        return None
    
    async def batch_fetch_quotes(self, tickers: List[str]) -> Dict[str, PriceUpdate]:
        """Fetch quotes for multiple tickers concurrently"""
        tasks = [self.get_best_quote(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        quotes = {}
        for ticker, result in zip(tickers, results):
            if isinstance(result, PriceUpdate):
                quotes[ticker] = result
            else:
                logger.warning(f"Failed to fetch quote for {ticker}: {result}")
        
        return quotes
    
    def subscribe(self, ticker: str, callback: Callable):
        """Subscribe to price updates for a ticker"""
        if ticker not in self.subscribers:
            self.subscribers[ticker] = []
        self.subscribers[ticker].append(callback)
        logger.info(f"Subscribed to {ticker}")
    
    def unsubscribe(self, ticker: str, callback: Callable):
        """Unsubscribe from price updates"""
        if ticker in self.subscribers and callback in self.subscribers[ticker]:
            self.subscribers[ticker].remove(callback)
    
    async def start_websocket_stream(self, tickers: List[str], provider: str = 'polygon'):
        """Start WebSocket stream for real-time updates"""
        try:
            # WebSocket URL based on provider
            ws_urls = {
                'polygon': 'wss://socket.polygon.io/stocks',
                'iex': 'wss://ws.iexcloud.com/ws',
                'alpha_vantage': 'wss://ws.alphavantage.co/stream',
                'coinbase': 'wss://ws-feed.exchange.coinbase.com'
            }
            
            if provider not in ws_urls:
                logger.error(f"Unsupported WebSocket provider: {provider}")
                return None
            
            import websockets
            ws_url = ws_urls[provider]
            
            # Connect to WebSocket
            logger.info(f"Connecting to WebSocket: {ws_url}")
            async with websockets.connect(ws_url) as websocket:
                logger.info(f"WebSocket connected for {len(tickers)} tickers via {provider}")
                
                # Subscribe to ticker data
                subscribe_msg = {
                    "action": "subscribe",
                    "params": {
                        "symbols": tickers,
                        "types": ["quote", "trade"]
                    }
                }
                
                await websocket.send(json.dumps(subscribe_msg))
                
                # Handle incoming messages
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        
                        # Process different message types
                        if 'type' in data:
                            if data['type'] == 'quote':
                                await self._process_quote_update(data)
                            elif data['type'] == 'trade':
                                await self._process_trade_update(data)
                            elif data['type'] == 'error':
                                logger.error(f"WebSocket error: {data}")
                                
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse WebSocket message: {e}")
                        
        except Exception as e:
            logger.error(f"WebSocket streaming error: {e}")
            raise
    
    async def run_price_monitor(self, tickers: List[str], interval_seconds: int = 5):
        """Run continuous price monitoring"""
        logger.info(f"Starting price monitor for {len(tickers)} tickers")
        
        while True:
            try:
                quotes = await self.batch_fetch_quotes(tickers)
                
                # Notify subscribers
                for ticker, quote in quotes.items():
                    if ticker in self.subscribers:
                        for callback in self.subscribers[ticker]:
                            try:
                                callback(quote)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Price monitor error: {e}")
                await asyncio.sleep(interval_seconds)


# Quick usage
def get_live_quote(ticker: str, api_key: str, provider: str = 'polygon') -> Dict:
    """Get single live quote"""
    import asyncio
    
    async def fetch():
        async with LiveDataManager() as manager:
            if provider == 'polygon':
                manager.set_api_keys(polygon=api_key)
                return await manager.fetch_polygon_quote(ticker)
            elif provider == 'iex':
                manager.set_api_keys(iex=api_key)
                return await manager.fetch_iex_quote(ticker)
            return None
    
    result = asyncio.run(fetch())
    
    if result:
        return {
            'ticker': result.ticker,
            'price': result.price,
            'bid': result.bid,
            'ask': result.ask,
            'volume': result.volume,
            'timestamp': result.timestamp.isoformat(),
            'source': result.source
        }
    return {'error': 'Failed to fetch quote'}


def batch_get_quotes(tickers: List[str], api_keys: Dict) -> Dict[str, Dict]:
    """Batch fetch quotes for multiple tickers"""
    import asyncio
    
    async def fetch_all():
        async with LiveDataManager() as manager:
            manager.set_api_keys(**api_keys)
            return await manager.batch_fetch_quotes(tickers)
    
    results = asyncio.run(fetch_all())
    
    return {
        ticker: {
            'price': quote.price,
            'bid': quote.bid,
            'ask': quote.ask,
            'volume': quote.volume,
            'source': quote.source
        }
        for ticker, quote in results.items()
    }
