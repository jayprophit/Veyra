"""
Live Data Manager - Real Data First
====================================
Prioritizes live data from brokers and APIs.
Falls back to mock data ONLY when APIs unavailable.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import aiohttp

logger = logging.getLogger(__name__)


class DataSource(Enum):
    LIVE = "live"
    CACHED = "cached"
    MOCK = "mock"


@dataclass
class PriceData:
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    source: DataSource
    bid: Optional[float] = None
    ask: Optional[float] = None


@dataclass
class MarketData:
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: Optional[float] = None


class LiveDataManager:
    """
    Central manager for all live data connections.
    Uses real APIs first, caches results, falls back to mock only when needed.
    """
    
    def __init__(self):
        # API Configuration from environment
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
        self.alpaca_base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        self.polygon_base_url = 'https://api.polygon.io'
        
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY')
        
        # Data sources priority
        self.data_sources = ['polygon', 'alpaca', 'yahoo', 'alpha_vantage']
        
        # Cache
        self.price_cache: Dict[str, PriceData] = {}
        self.cache_ttl = 30  # seconds
        
        # WebSocket connections
        self.ws_subscribers: Dict[str, List[Callable]] = {}
        
        # State
        self._running = False
        self._last_prices: Dict[str, float] = {}
        
        logger.info("LiveDataManager initialized")
    
    @property
    def has_live_credentials(self) -> bool:
        """Check if any live API credentials are configured."""
        return any([
            self.polygon_api_key,
            self.alpaca_api_key,
            self.alpha_vantage_key
        ])
    
    async def get_quote(self, symbol: str, prefer_live: bool = True) -> Optional[PriceData]:
        """
        Get real-time quote for a symbol.
        Tries live APIs first, then cache, then mock as last resort.
        """
        # Check cache first if not preferring live
        if not prefer_live and symbol in self.price_cache:
            cached = self.price_cache[symbol]
            if datetime.now() - cached.timestamp < timedelta(seconds=self.cache_ttl):
                return cached
        
        # Try live sources in priority order
        if self.polygon_api_key:
            try:
                data = await self._fetch_polygon_quote(symbol)
                if data:
                    return data
            except Exception as e:
                logger.warning(f"Polygon fetch failed for {symbol}: {e}")
        
        if self.alpaca_api_key:
            try:
                data = await self._fetch_alpaca_quote(symbol)
                if data:
                    return data
            except Exception as e:
                logger.warning(f"Alpaca fetch failed for {symbol}: {e}")
        
        if self.alpha_vantage_key:
            try:
                data = await self._fetch_alpha_vantage_quote(symbol)
                if data:
                    return data
            except Exception as e:
                logger.warning(f"Alpha Vantage fetch failed for {symbol}: {e}")
        
        # Use cached data even if stale
        if symbol in self.price_cache:
            cached = self.price_cache[symbol]
            cached.source = DataSource.CACHED
            logger.info(f"Using cached data for {symbol}")
            return cached
        
        # Last resort: mock data with warning
        logger.warning(f"No live data available for {symbol}, using MOCK data")
        return self._generate_mock_quote(symbol)
    
    async def get_quotes(self, symbols: List[str]) -> Dict[str, PriceData]:
        """Get quotes for multiple symbols efficiently."""
        results = {}
        
        # Fetch in parallel
        tasks = [self.get_quote(sym) for sym in symbols]
        quotes = await asyncio.gather(*tasks, return_exceptions=True)
        
        for symbol, quote in zip(symbols, quotes):
            if isinstance(quote, Exception):
                logger.error(f"Error fetching {symbol}: {quote}")
                results[symbol] = self._generate_mock_quote(symbol)
            elif quote:
                results[symbol] = quote
            else:
                results[symbol] = self._generate_mock_quote(symbol)
        
        return results
    
    async def _fetch_polygon_quote(self, symbol: str) -> Optional[PriceData]:
        """Fetch quote from Polygon.io."""
        url = f"{self.polygon_base_url}/v2/last/trade/{symbol}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'apiKey': self.polygon_api_key}) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                trade = data.get('results', {})
                
                price = trade.get('p', 0)
                prev_price = self._last_prices.get(symbol, price)
                change = price - prev_price
                
                self._last_prices[symbol] = price
                
                quote = PriceData(
                    symbol=symbol,
                    price=price,
                    change=change,
                    change_percent=(change / prev_price * 100) if prev_price else 0,
                    volume=trade.get('v', 0),
                    timestamp=datetime.now(),
                    source=DataSource.LIVE
                )
                
                self.price_cache[symbol] = quote
                return quote
    
    async def _fetch_alpaca_quote(self, symbol: str) -> Optional[PriceData]:
        """Fetch quote from Alpaca."""
        url = f"{self.alpaca_base_url}/v2/stocks/{symbol}/quotes/latest"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'APCA-API-KEY-ID': self.alpaca_api_key,
                'APCA-API-SECRET-KEY': self.alpaca_secret
            }
            
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                quote = data.get('quote', {})
                
                bid = quote.get('bp', 0)
                ask = quote.get('ap', 0)
                price = (bid + ask) / 2 if bid and ask else bid or ask or 0
                
                prev_price = self._last_prices.get(symbol, price)
                change = price - prev_price
                
                self._last_prices[symbol] = price
                
                result = PriceData(
                    symbol=symbol,
                    price=price,
                    change=change,
                    change_percent=(change / prev_price * 100) if prev_price else 0,
                    volume=quote.get('v', 0),
                    timestamp=datetime.now(),
                    source=DataSource.LIVE,
                    bid=bid,
                    ask=ask
                )
                
                self.price_cache[symbol] = result
                return result
    
    async def _fetch_alpha_vantage_quote(self, symbol: str) -> Optional[PriceData]:
        """Fetch quote from Alpha Vantage (free tier)."""
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.alpha_vantage_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                quote = data.get('Global Quote', {})
                
                if not quote:
                    return None
                
                price = float(quote.get('05. price', 0))
                change = float(quote.get('09. change', 0))
                change_percent = float(quote.get('10. change percent', '0').replace('%', ''))
                volume = int(quote.get('06. volume', 0))
                
                result = PriceData(
                    symbol=symbol,
                    price=price,
                    change=change,
                    change_percent=change_percent,
                    volume=volume,
                    timestamp=datetime.now(),
                    source=DataSource.LIVE
                )
                
                self.price_cache[symbol] = result
                return result
    
    def _generate_mock_quote(self, symbol: str) -> PriceData:
        """Generate realistic mock data as fallback."""
        # Generate realistic-looking mock data based on symbol hash
        base_price = 100 + (hash(symbol) % 200)
        variation = (hash(symbol + str(datetime.now().minute)) % 10) - 5
        
        price = base_price + variation
        change = variation
        change_percent = (change / (price - change)) * 100 if price != change else 0
        
        return PriceData(
            symbol=symbol,
            price=price,
            change=change,
            change_percent=change_percent,
            volume=1000000 + (hash(symbol) % 5000000),
            timestamp=datetime.now(),
            source=DataSource.MOCK
        )
    
    async def start_live_feed(self, symbols: List[str], callback: Callable[[PriceData], Any]):
        """
        Start live price feed for symbols.
        Calls callback with each price update.
        """
        self._running = True
        
        logger.info(f"Starting live feed for {len(symbols)} symbols")
        
        while self._running:
            try:
                # Fetch all quotes
                quotes = await self.get_quotes(symbols)
                
                # Call callback for each
                for symbol, quote in quotes.items():
                    try:
                        await callback(quote)
                    except Exception as e:
                        logger.error(f"Callback error for {symbol}: {e}")
                
                # Wait before next update
                await asyncio.sleep(5)  # 5-second refresh
                
            except Exception as e:
                logger.error(f"Live feed error: {e}")
                await asyncio.sleep(10)  # Longer wait on error
    
    def stop_live_feed(self):
        """Stop the live feed."""
        self._running = False
        logger.info("Live feed stopped")
    
    async def get_historical_data(self, symbol: str, days: int = 30) -> List[MarketData]:
        """Get historical OHLCV data."""
        if self.polygon_api_key:
            return await self._fetch_polygon_historical(symbol, days)
        
        # Return mock historical data
        return self._generate_mock_historical(symbol, days)
    
    async def _fetch_polygon_historical(self, symbol: str, days: int) -> List[MarketData]:
        """Fetch historical data from Polygon."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        url = f"{self.polygon_base_url}/v2/aggs/ticker/{symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'apiKey': self.polygon_api_key}) as resp:
                if resp.status != 200:
                    return []
                
                data = await resp.json()
                results = data.get('results', [])
                
                return [
                    MarketData(
                        symbol=symbol,
                        open=r.get('o', 0),
                        high=r.get('h', 0),
                        low=r.get('l', 0),
                        close=r.get('c', 0),
                        volume=r.get('v', 0),
                        vwap=r.get('vw')
                    )
                    for r in results
                ]
    
    def _generate_mock_historical(self, symbol: str, days: int) -> List[MarketData]:
        """Generate mock historical data."""
        base_price = 100 + (hash(symbol) % 200)
        results = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            variation = (hash(symbol + str(date)) % 20) - 10
            
            close = base_price + variation
            open_price = close - (hash(symbol + str(date) + 'o') % 10 - 5)
            high = max(open_price, close) + (hash(symbol + str(date) + 'h') % 5)
            low = min(open_price, close) - (hash(symbol + str(date) + 'l') % 5)
            
            results.append(MarketData(
                symbol=symbol,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=1000000 + (hash(symbol + str(date)) % 5000000)
            ))
        
        return list(reversed(results))
    
    def get_data_source_stats(self) -> Dict[str, Any]:
        """Get statistics about data sources used."""
        sources = {'live': 0, 'cached': 0, 'mock': 0}
        
        for quote in self.price_cache.values():
            sources[quote.source.value] += 1
        
        return {
            'total_symbols': len(self.price_cache),
            'by_source': sources,
            'has_live_credentials': self.has_live_credentials,
            'cache_size': len(self.price_cache),
            'data_sources_available': [
                s for s in ['polygon', 'alpaca', 'alpha_vantage']
                if getattr(self, f'{s}_api_key')
            ]
        }


# Global instance
live_data = LiveDataManager()


# Convenience functions for easy access
async def get_live_price(symbol: str) -> Optional[float]:
    """Get live price for a symbol."""
    quote = await live_data.get_quote(symbol)
    return quote.price if quote else None


async def get_live_prices(symbols: List[str]) -> Dict[str, float]:
    """Get live prices for multiple symbols."""
    quotes = await live_data.get_quotes(symbols)
    return {sym: q.price for sym, q in quotes.items()}


def is_live_data_available() -> bool:
    """Check if live data is available."""
    return live_data.has_live_credentials
