"""Real-Time Data Integration - Production Pipeline
Connects live data feeds to your existing WebSocket system.
"""
import os
import asyncio
from typing import Dict, List, Callable, Optional
from datetime import datetime
import logging

from data_providers.polygon_provider import PolygonDataProvider, Trade, Quote
from websocket_real_time_feeds import DataFeedManager, DataProvider, WebSocketConfig

logger = logging.getLogger(__name__)

class RealtimeDataIntegration:
    """
    Production Real-Time Data Pipeline
    ==================================
    Bridges Polygon.io live data with your WebSocket system.
    
    Features:
    - Live trade streaming
    - Quote (bid/ask) streaming  
    - Automatic reconnection
    - Multi-symbol support
    - Price caching
    - Alert triggering
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        self.polygon = None
        self.feed_manager = None
        
        self.price_cache: Dict[str, Dict] = {}
        self.alert_handlers: List[Callable] = []
        self.subscribed_symbols: set = set()
        
        self._running = False
        self._reconnect_attempts = 0
        self._max_reconnect = 10
        
    async def start(self, symbols: List[str], feed_manager: DataFeedManager = None):
        """
        Start real-time data pipeline.
        
        Args:
            symbols: List of stock symbols to track
            feed_manager: Optional existing feed manager to integrate with
        """
        if not self.api_key:
            logger.warning("No Polygon API key - running in mock mode")
            return await self._start_mock(symbols, feed_manager)
        
        logger.info(f"Starting real-time data for {len(symbols)} symbols")
        
        self.subscribed_symbols = set(symbols)
        self.feed_manager = feed_manager
        
        # Initialize Polygon
        self.polygon = PolygonDataProvider(self.api_key)
        
        # Register callbacks
        self.polygon.on_trade(self._handle_trade)
        self.polygon.on_quote(self._handle_quote)
        
        # Connect and subscribe
        await self.polygon.connect()
        await self.polygon.subscribe_trades(symbols)
        await self.polygon.subscribe_quotes(symbols)
        
        self._running = True
        
        # Start monitoring
        asyncio.create_task(self._monitor_connection())
        
        logger.info("Real-time data pipeline active")
        
    async def _start_mock(self, symbols: List[str], feed_manager: DataFeedManager = None):
        """Start mock data for testing."""
        logger.info("Starting MOCK data feed")
        
        if feed_manager:
            # Use existing mock provider
            feed_manager.setup(DataProvider.MOCK)
            await feed_manager.start()
        else:
            # Create simple mock
            self._running = True
            while self._running:
                for symbol in symbols:
                    mock_trade = {
                        "symbol": symbol,
                        "price": 100.0 + (hash(symbol) % 20),
                        "timestamp": datetime.now().isoformat()
                    }
                    await self._handle_trade(mock_trade)
                await asyncio.sleep(2)
    
    async def _handle_trade(self, trade: Trade):
        """Handle incoming trade."""
        # Update price cache
        self.price_cache[trade.symbol] = {
            "price": trade.price,
            "timestamp": trade.timestamp,
            "source": "polygon"
        }
        
        # Forward to feed manager if connected
        if self.feed_manager:
            await self.feed_manager.broadcast({
                "type": "trade",
                "symbol": trade.symbol,
                "price": trade.price,
                "size": trade.size,
                "timestamp": trade.timestamp
            })
        
        # Check alerts
        await self._check_alerts(trade.symbol, trade.price)
        
        logger.debug(f"Trade: {trade.symbol} @ ${trade.price:.2f}")
    
    async def _handle_quote(self, quote: Quote):
        """Handle incoming quote."""
        # Update cache with spread
        if quote.symbol in self.price_cache:
            self.price_cache[quote.symbol].update({
                "bid": quote.bid_price,
                "ask": quote.ask_price,
                "spread": quote.ask_price - quote.bid_price
            })
        
        # Forward to feed manager
        if self.feed_manager:
            await self.feed_manager.broadcast({
                "type": "quote",
                "symbol": quote.symbol,
                "bid": quote.bid_price,
                "ask": quote.ask_price,
                "timestamp": quote.timestamp
            })
    
    async def _monitor_connection(self):
        """Monitor connection health and reconnect if needed."""
        while self._running:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            # Check if still receiving data
            last_update = max(
                (cache.get("timestamp", 0) for cache in self.price_cache.values()),
                default=0
            )
            
            time_since_update = datetime.now().timestamp() - (last_update / 1000)
            
            if time_since_update > 60:  # No data for 60 seconds
                logger.warning("No data received for 60s - attempting reconnect")
                await self._reconnect()
    
    async def _reconnect(self):
        """Attempt to reconnect."""
        if self._reconnect_attempts >= self._max_reconnect:
            logger.error("Max reconnect attempts reached - entering mock mode")
            await self.stop()
            await self._start_mock(list(self.subscribed_symbols), self.feed_manager)
            return
        
        self._reconnect_attempts += 1
        
        try:
            if self.polygon:
                await self.polygon.disconnect()
            
            await asyncio.sleep(2 ** self._reconnect_attempts)  # Exponential backoff
            
            self.polygon = PolygonDataProvider(self.api_key)
            await self.polygon.connect()
            await self.polygon.subscribe_trades(list(self.subscribed_symbols))
            
            self._reconnect_attempts = 0
            logger.info("Reconnected successfully")
            
        except Exception as e:
            logger.error(f"Reconnect failed: {e}")
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current cached price for symbol."""
        cache = self.price_cache.get(symbol)
        if cache:
            return cache.get("price")
        return None
    
    def get_price_cache(self) -> Dict:
        """Get full price cache."""
        return self.price_cache.copy()
    
    def add_symbol(self, symbol: str):
        """Add symbol to watchlist."""
        if symbol not in self.subscribed_symbols and self.polygon:
            asyncio.create_task(self.polygon.subscribe_trades([symbol]))
            self.subscribed_symbols.add(symbol)
    
    def remove_symbol(self, symbol: str):
        """Remove symbol from watchlist."""
        if symbol in self.subscribed_symbols and self.polygon:
            asyncio.create_task(self.polygon.unsubscribe([symbol]))
            self.subscribed_symbols.discard(symbol)
    
    def on_price_alert(self, callback: Callable[[str, float], None]):
        """Register price alert handler."""
        self.alert_handlers.append(callback)
    
    async def _check_alerts(self, symbol: str, price: float):
        """Check and trigger price alerts."""
        for handler in self.alert_handlers:
            try:
                await handler(symbol, price)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    async def stop(self):
        """Stop data pipeline."""
        self._running = False
        
        if self.polygon:
            await self.polygon.disconnect()
        
        if self.feed_manager:
            await self.feed_manager.stop()
        
        logger.info("Real-time data pipeline stopped")

# Integration with existing system
async def initialize_realtime_data(
    symbols: List[str] = None,
    feed_manager: DataFeedManager = None,
    use_live: bool = True
) -> RealtimeDataIntegration:
    """
    Initialize real-time data for Financial Master.
    
    Usage:
        data = await initialize_realtime_data(['AAPL', 'MSFT', 'TSLA'])
        price = data.get_current_price('AAPL')
    """
    symbols = symbols or ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    integration = RealtimeDataIntegration()
    
    if not use_live or not os.getenv('POLYGON_API_KEY'):
        logger.info("Running in DEMO mode with mock data")
    
    await integration.start(symbols, feed_manager)
    
    return integration

# Example usage:
# async def main():
#     data = await initialize_realtime_data(['AAPL', 'MSFT'])
#     
#     # Wait for some data
#     await asyncio.sleep(10)
#     
#     # Get current price
#     price = data.get_current_price('AAPL')
#     print(f"AAPL: ${price}")
#     
#     # Stop
#     await data.stop()
