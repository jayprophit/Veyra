"""
Hybrid Data Manager - Live + Mock with Clear Indicators
========================================================
Combines real market data with mock/simulated data for testing.
CLEARLY labels all data with source indicators.

Features:
- Real data prioritized when APIs available
- Mock data fallback with clear UI indicators
- Source tracking for every data point
- Transparent data lineage

Free tier sources:
- Yahoo Finance (no key needed)
- CoinGecko (crypto, no key)
- Alpha Vantage (25 calls/day free)
- Polygon (5 calls/min free)
"""

import asyncio
import aiohttp
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data source type with clear labels"""
    LIVE_POLYGON = "live_polygon"           # Real-time from Polygon.io
    LIVE_ALPACA = "live_alpaca"             # Real-time from Alpaca
    LIVE_YAHOO = "live_yahoo"               # Delayed from Yahoo Finance
    LIVE_COINGECKO = "live_coingecko"       # Real-time crypto
    LIVE_ALPHAVANTAGE = "live_alphavantage" # Delayed stock data
    LIVE_IBKR = "live_ibkr"                 # Real-time from IBKR
    LIVE_COINBASE = "live_coinbase"         # Real-time crypto
    CACHED = "cached"                       # Previously fetched data
    MOCK_SIMULATED = "mock_simulated"       # Computer-generated simulation
    MOCK_HISTORICAL = "mock_historical"     # Based on real historical patterns
    MOCK_TEST = "mock_test"                 # Pure test data


@dataclass
class DataPoint:
    """Single data point with full source tracking"""
    value: Any
    timestamp: datetime
    source: DataSource
    symbol: str
    field: str  # e.g., 'price', 'volume', 'bid', 'ask'
    
    # Metadata
    latency_ms: Optional[float] = None
    cached_at: Optional[datetime] = None
    freshness_seconds: Optional[int] = None
    
    # Source details
    api_endpoint: Optional[str] = None
    broker: Optional[str] = None
    
    # Quality indicators
    is_real: bool = field(init=False)
    is_delayed: bool = field(init=False)
    is_simulated: bool = field(init=False)
    
    def __post_init__(self):
        self.is_real = self.source.value.startswith('live_')
        self.is_delayed = self.source in [
            DataSource.LIVE_YAHOO,
            DataSource.LIVE_ALPHAVANTAGE
        ]
        self.is_simulated = self.source.value.startswith('mock_')
    
    def get_source_badge(self) -> str:
        """Get UI-friendly source badge"""
        badges = {
            DataSource.LIVE_POLYGON: "🟢 LIVE",
            DataSource.LIVE_ALPACA: "🟢 LIVE",
            DataSource.LIVE_IBKR: "🟢 LIVE",
            DataSource.LIVE_COINBASE: "🟢 LIVE",
            DataSource.LIVE_COINGECKO: "🟢 LIVE",
            DataSource.LIVE_YAHOO: "🟡 DELAYED",
            DataSource.LIVE_ALPHAVANTAGE: "🟡 DELAYED",
            DataSource.CACHED: "🟠 CACHED",
            DataSource.MOCK_SIMULATED: "🔵 SIMULATED",
            DataSource.MOCK_HISTORICAL: "🔵 SIMULATED",
            DataSource.MOCK_TEST: "⚪ TEST",
        }
        return badges.get(self.source, "❓ UNKNOWN")
    
    def get_tooltip(self) -> str:
        """Get detailed source information"""
        lines = [
            f"Source: {self.source.value.replace('_', ' ').title()}",
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}",
        ]
        
        if self.broker:
            lines.append(f"Broker: {self.broker}")
        
        if self.api_endpoint:
            lines.append(f"Endpoint: {self.api_endpoint}")
        
        if self.latency_ms:
            lines.append(f"Latency: {self.latency_ms:.1f}ms")
        
        if self.freshness_seconds:
            lines.append(f"Age: {self.freshness_seconds}s")
        
        return "\n".join(lines)


@dataclass
class HybridQuote:
    """Complete quote with all fields tracked separately"""
    symbol: str
    
    # Price fields
    price: DataPoint
    bid: Optional[DataPoint] = None
    ask: Optional[DataPoint] = None
    
    # Market data
    volume: Optional[DataPoint] = None
    open: Optional[DataPoint] = None
    high: Optional[DataPoint] = None
    low: Optional[DataPoint] = None
    close: Optional[DataPoint] = None
    
    # Change data
    change: Optional[DataPoint] = None
    change_percent: Optional[DataPoint] = None
    
    @property
    def is_fully_live(self) -> bool:
        """Check if all data is from live sources"""
        for field in [self.price, self.bid, self.ask, self.volume]:
            if field and not field.is_real:
                return False
        return True
    
    @property
    def primary_source(self) -> DataSource:
        """Get the primary data source"""
        return self.price.source
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with source metadata"""
        return {
            'symbol': self.symbol,
            'price': self._datapoint_to_dict(self.price),
            'bid': self._datapoint_to_dict(self.bid) if self.bid else None,
            'ask': self._datapoint_to_dict(self.ask) if self.ask else None,
            'volume': self._datapoint_to_dict(self.volume) if self.volume else None,
            'source_summary': {
                'primary': self.primary_source.value,
                'is_fully_live': self.is_fully_live,
                'has_simulated': any(
                    f.is_simulated if f else False
                    for f in [self.price, self.bid, self.ask, self.volume]
                )
            }
        }
    
    def _datapoint_to_dict(self, dp: DataPoint) -> Dict:
        """Convert datapoint to dict"""
        return {
            'value': dp.value,
            'source': dp.source.value,
            'badge': dp.get_source_badge(),
            'is_real': dp.is_real,
            'is_simulated': dp.is_simulated,
            'timestamp': dp.timestamp.isoformat()
        }


class HybridDataManager:
    """
    Hybrid data manager - combines live and mock data
    
    Strategy:
    1. Try live APIs first (if credentials available)
    2. Fall back to cached data
    3. Generate mock data as last resort
    4. ALWAYS label data source clearly
    """
    
    def __init__(
        self,
        polygon_key: Optional[str] = None,
        alpaca_key: Optional[str] = None,
        alpaca_secret: Optional[str] = None,
        alpha_vantage_key: Optional[str] = None
    ):
        # API Keys
        self.polygon_key = polygon_key
        self.alpaca_key = alpaca_key
        self.alpaca_secret = alpaca_secret
        self.alpha_vantage_key = alpha_vantage_key
        
        # Cache
        self._cache: Dict[str, DataPoint] = {}
        self._cache_ttl_seconds = 60
        
        # Session
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Mock data generator
        self._mock_prices: Dict[str, float] = {}
        
        logger.info("HybridDataManager initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def get_quote(
        self,
        symbol: str,
        prefer_live: bool = True,
        allow_mock: bool = True
    ) -> HybridQuote:
        """
        Get hybrid quote for symbol
        
        Args:
            symbol: Trading symbol
            prefer_live: Try live sources first
            allow_mock: Allow mock fallback
            
        Returns:
            HybridQuote with source tracking
        """
        start_time = datetime.now()
        
        # Try live sources in priority order
        if prefer_live:
            # 1. Try Polygon (most real-time)
            if self.polygon_key:
                quote = await self._fetch_polygon(symbol)
                if quote:
                    latency = (datetime.now() - start_time).total_seconds() * 1000
                    self._update_latency(quote, latency)
                    return quote
            
            # 2. Try Alpaca
            if self.alpaca_key and self.alpaca_secret:
                quote = await self._fetch_alpaca(symbol)
                if quote:
                    latency = (datetime.now() - start_time).total_seconds() * 1000
                    self._update_latency(quote, latency)
                    return quote
            
            # 3. Try Yahoo Finance (free, no key)
            quote = await self._fetch_yahoo(symbol)
            if quote:
                latency = (datetime.now() - start_time).total_seconds() * 1000
                self._update_latency(quote, latency)
                return quote
            
            # 4. Try Alpha Vantage
            if self.alpha_vantage_key:
                quote = await self._fetch_alpha_vantage(symbol)
                if quote:
                    latency = (datetime.now() - start_time).total_seconds() * 1000
                    self._update_latency(quote, latency)
                    return quote
        
        # Check cache
        cache_key = f"quote_{symbol}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            age = (datetime.now() - cached.timestamp).seconds
            if age < self._cache_ttl_seconds:
                # Return cached as new cached point
                return self._create_from_cached(symbol, cached, age)
        
        # Generate mock if allowed
        if allow_mock:
            quote = self._generate_mock_quote(symbol)
            logger.warning(f"Using MOCK data for {symbol}")
            return quote
        
        # Return empty quote
        return self._create_empty_quote(symbol)
    
    async def get_quotes(
        self,
        symbols: List[str],
        prefer_live: bool = True
    ) -> Dict[str, HybridQuote]:
        """Get quotes for multiple symbols"""
        tasks = [self.get_quote(sym, prefer_live) for sym in symbols]
        quotes = await asyncio.gather(*tasks, return_exceptions=True)
        
        result = {}
        for symbol, quote in zip(symbols, quotes):
            if isinstance(quote, Exception):
                logger.error(f"Error fetching {symbol}: {quote}")
                result[symbol] = self._generate_mock_quote(symbol)
            else:
                result[symbol] = quote
        
        return result
    
    async def _fetch_polygon(self, symbol: str) -> Optional[HybridQuote]:
        """Fetch from Polygon.io"""
        url = f"https://api.polygon.io/v2/last/trade/{symbol}"
        
        try:
            session = await self._get_session()
            async with session.get(
                url,
                params={'apiKey': self.polygon_key},
                timeout=5
            ) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                results = data.get('results', {})
                
                if not results:
                    return None
                
                timestamp = datetime.now()
                
                price = DataPoint(
                    value=Decimal(str(results.get('p', 0))),
                    timestamp=timestamp,
                    source=DataSource.LIVE_POLYGON,
                    symbol=symbol,
                    field='price',
                    api_endpoint='v2/last/trade'
                )
                
                volume = DataPoint(
                    value=int(results.get('v', 0)),
                    timestamp=timestamp,
                    source=DataSource.LIVE_POLYGON,
                    symbol=symbol,
                    field='volume',
                    api_endpoint='v2/last/trade'
                )
                
                quote = HybridQuote(symbol=symbol, price=price, volume=volume)
                self._cache[f"quote_{symbol}"] = price
                
                return quote
                
        except Exception as e:
            logger.warning(f"Polygon fetch failed for {symbol}: {e}")
            return None
    
    async def _fetch_alpaca(self, symbol: str) -> Optional[HybridQuote]:
        """Fetch from Alpaca"""
        url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest"
        
        try:
            session = await self._get_session()
            headers = {
                'APCA-API-KEY-ID': self.alpaca_key,
                'APCA-API-SECRET-KEY': self.alpaca_secret
            }
            
            async with session.get(url, headers=headers, timeout=5) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                quote_data = data.get('quote', {})
                
                if not quote_data:
                    return None
                
                timestamp = datetime.now()
                
                bid_price = Decimal(str(quote_data.get('bp', 0)))
                ask_price = Decimal(str(quote_data.get('ap', 0)))
                mid_price = (bid_price + ask_price) / 2 if bid_price and ask_price else bid_price or ask_price
                
                price = DataPoint(
                    value=mid_price,
                    timestamp=timestamp,
                    source=DataSource.LIVE_ALPACA,
                    symbol=symbol,
                    field='price',
                    api_endpoint='v2/stocks/quotes/latest',
                    broker='Alpaca'
                )
                
                bid = DataPoint(
                    value=bid_price,
                    timestamp=timestamp,
                    source=DataSource.LIVE_ALPACA,
                    symbol=symbol,
                    field='bid',
                    api_endpoint='v2/stocks/quotes/latest',
                    broker='Alpaca'
                )
                
                ask = DataPoint(
                    value=ask_price,
                    timestamp=timestamp,
                    source=DataSource.LIVE_ALPACA,
                    symbol=symbol,
                    field='ask',
                    api_endpoint='v2/stocks/quotes/latest',
                    broker='Alpaca'
                )
                
                quote = HybridQuote(
                    symbol=symbol,
                    price=price,
                    bid=bid,
                    ask=ask
                )
                
                self._cache[f"quote_{symbol}"] = price
                return quote
                
        except Exception as e:
            logger.warning(f"Alpaca fetch failed for {symbol}: {e}")
            return None
    
    async def _fetch_yahoo(self, symbol: str) -> Optional[HybridQuote]:
        """Fetch from Yahoo Finance (free, no key)"""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        
        try:
            session = await self._get_session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                chart = data.get('chart', {})
                result = chart.get('result', [{}])[0]
                meta = result.get('meta', {})
                
                timestamp = datetime.now()
                
                price = DataPoint(
                    value=Decimal(str(meta.get('regularMarketPrice', 0))),
                    timestamp=timestamp,
                    source=DataSource.LIVE_YAHOO,
                    symbol=symbol,
                    field='price',
                    api_endpoint='v8/finance/chart'
                )
                
                volume_val = meta.get('regularMarketVolume')
                volume = None
                if volume_val:
                    volume = DataPoint(
                        value=int(volume_val),
                        timestamp=timestamp,
                        source=DataSource.LIVE_YAHOO,
                        symbol=symbol,
                        field='volume',
                        api_endpoint='v8/finance/chart'
                    )
                
                quote = HybridQuote(symbol=symbol, price=price, volume=volume)
                self._cache[f"quote_{symbol}"] = price
                
                return quote
                
        except Exception as e:
            logger.warning(f"Yahoo fetch failed for {symbol}: {e}")
            return None
    
    async def _fetch_alpha_vantage(self, symbol: str) -> Optional[HybridQuote]:
        """Fetch from Alpha Vantage"""
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.alpha_vantage_key
        }
        
        try:
            session = await self._get_session()
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                quote_data = data.get('Global Quote', {})
                
                if not quote_data:
                    return None
                
                timestamp = datetime.now()
                
                price = DataPoint(
                    value=Decimal(quote_data.get('05. price', '0')),
                    timestamp=timestamp,
                    source=DataSource.LIVE_ALPHAVANTAGE,
                    symbol=symbol,
                    field='price',
                    api_endpoint='query (GLOBAL_QUOTE)'
                )
                
                volume_val = quote_data.get('06. volume')
                volume = None
                if volume_val:
                    volume = DataPoint(
                        value=int(volume_val),
                        timestamp=timestamp,
                        source=DataSource.LIVE_ALPHAVANTAGE,
                        symbol=symbol,
                        field='volume',
                        api_endpoint='query (GLOBAL_QUOTE)'
                    )
                
                quote = HybridQuote(symbol=symbol, price=price, volume=volume)
                self._cache[f"quote_{symbol}"] = price
                
                return quote
                
        except Exception as e:
            logger.warning(f"Alpha Vantage fetch failed for {symbol}: {e}")
            return None
    
    def _generate_mock_quote(self, symbol: str) -> HybridQuote:
        """Generate mock quote with clear indicators"""
        # Generate deterministic but realistic-looking price
        base_hash = hash(symbol) % 10000
        base_price = 50 + (base_hash % 450)  # $50-$500 range
        
        # Add small random variation
        variation = (datetime.now().microsecond % 100) / 100 - 0.5
        price_val = base_price * (1 + variation * 0.02)
        
        timestamp = datetime.now()
        
        price = DataPoint(
            value=Decimal(str(round(price_val, 2))),
            timestamp=timestamp,
            source=DataSource.MOCK_SIMULATED,
            symbol=symbol,
            field='price',
            is_real=False,
            is_simulated=True
        )
        
        # Generate bid/ask spread
        spread = price_val * 0.001  # 0.1% spread
        
        bid = DataPoint(
            value=Decimal(str(round(price_val - spread/2, 2))),
            timestamp=timestamp,
            source=DataSource.MOCK_SIMULATED,
            symbol=symbol,
            field='bid'
        )
        
        ask = DataPoint(
            value=Decimal(str(round(price_val + spread/2, 2))),
            timestamp=timestamp,
            source=DataSource.MOCK_SIMULATED,
            symbol=symbol,
            field='ask'
        )
        
        volume = DataPoint(
            value=int(1000000 + (base_hash * 100)),
            timestamp=timestamp,
            source=DataSource.MOCK_SIMULATED,
            symbol=symbol,
            field='volume'
        )
        
        return HybridQuote(
            symbol=symbol,
            price=price,
            bid=bid,
            ask=ask,
            volume=volume
        )
    
    def _create_from_cached(
        self,
        symbol: str,
        cached: DataPoint,
        age_seconds: int
    ) -> HybridQuote:
        """Create quote from cached data"""
        cached_point = DataPoint(
            value=cached.value,
            timestamp=cached.timestamp,
            source=DataSource.CACHED,
            symbol=symbol,
            field='price',
            freshness_seconds=age_seconds,
            cached_at=cached.timestamp
        )
        
        return HybridQuote(symbol=symbol, price=cached_point)
    
    def _create_empty_quote(self, symbol: str) -> HybridQuote:
        """Create empty quote"""
        price = DataPoint(
            value=Decimal('0'),
            timestamp=datetime.now(),
            source=DataSource.MOCK_TEST,
            symbol=symbol,
            field='price'
        )
        return HybridQuote(symbol=symbol, price=price)
    
    def _update_latency(self, quote: HybridQuote, latency_ms: float):
        """Update latency on all data points"""
        for field in [quote.price, quote.bid, quote.ask, quote.volume]:
            if field:
                field.latency_ms = latency_ms
    
    def get_data_source_summary(self) -> Dict[str, Any]:
        """Get summary of data sources currently in use"""
        sources = {source: 0 for source in DataSource}
        
        for cached in self._cache.values():
            sources[cached.source] += 1
        
        return {
            'total_cached': len(self._cache),
            'by_source': {
                k.value: v for k, v in sources.items() if v > 0
            },
            'live_sources_available': [
                'polygon' if self.polygon_key else None,
                'alpaca' if self.alpaca_key else None,
                'yahoo'  # Always available
            ]
        }
    
    async def close(self):
        """Close session"""
        if self._session and not self._session.closed:
            await self._session.close()


# Global instance
_hybrid_manager: Optional[HybridDataManager] = None


def get_hybrid_manager() -> HybridDataManager:
    """Get global hybrid data manager"""
    global _hybrid_manager
    if _hybrid_manager is None:
        import os
        _hybrid_manager = HybridDataManager(
            polygon_key=os.getenv('POLYGON_API_KEY'),
            alpaca_key=os.getenv('ALPACA_API_KEY'),
            alpaca_secret=os.getenv('ALPACA_SECRET_KEY'),
            alpha_vantage_key=os.getenv('ALPHA_VANTAGE_API_KEY')
        )
    return _hybrid_manager


# Example usage
async def test_hybrid():
    """Test hybrid data manager"""
    manager = HybridDataManager()
    
    # Get quote for AAPL
    quote = await manager.get_quote('AAPL')
    
    print(f"\n{'='*50}")
    print(f"Symbol: {quote.symbol}")
    print(f"Price: ${quote.price.value}")
    print(f"Source: {quote.price.get_source_badge()}")
    print(f"Is Real: {quote.price.is_real}")
    print(f"\nDetails:")
    print(quote.price.get_tooltip())
    
    if quote.bid and quote.ask:
        print(f"\nBid: ${quote.bid.value} {quote.bid.get_source_badge()}")
        print(f"Ask: ${quote.ask.value} {quote.ask.get_source_badge()}")
    
    print(f"\n{'='*50}")
    print(f"Summary: {quote.to_dict()['source_summary']}")
    
    await manager.close()


if __name__ == "__main__":
    asyncio.run(test_hybrid())
