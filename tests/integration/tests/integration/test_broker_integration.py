"""
Integration Tests: Broker API Integration
===========================================
Tests real broker connections and trading workflows.
"""

import pytest
import asyncio
import os
from datetime import datetime

# Skip if no API keys
pytestmark = pytest.mark.skipif(
    not os.getenv('ALPACA_API_KEY'),
    reason="No Alpaca API key configured"
)

from brokers.alpaca_broker import AlpacaBroker, AlpacaOrder


class TestAlpacaPaperTrading:
    """Test Alpaca paper trading integration."""
    
    @pytest.fixture
    async def broker(self):
        """Create broker instance."""
        broker = AlpacaBroker(paper=True)
        yield broker
    
    @pytest.mark.asyncio
    async def test_account_connection(self, broker):
        """Test can connect to Alpaca and get account."""
        account = await broker.get_account()
        
        assert account is not None
        assert 'id' in account
        assert 'buying_power' in account
        assert 'cash' in account
        assert 'portfolio_value' in account
        
        print(f"Account: {account['id']}")
        print(f"Buying Power: ${account['buying_power']}")
    
    @pytest.mark.asyncio
    async def test_place_market_order(self, broker):
        """Test placing a market order (paper trading)."""
        order = AlpacaOrder(
            symbol='AAPL',
            qty=1,
            side='buy',
            type='market'
        )
        
        result = await broker.place_order(order)
        
        assert result is not None
        assert 'id' in result
        assert result['symbol'] == 'AAPL'
        assert float(result['qty']) == 1
        assert result['side'] == 'buy'
        
        # Cancel immediately to clean up
        await broker.cancel_order(result['id'])
    
    @pytest.mark.asyncio
    async def test_place_limit_order(self, broker):
        """Test placing a limit order."""
        # Get current price first
        bars = await broker.get_bars('AAPL', limit=1)
        if bars:
            current_price = bars[0]['c']
            limit_price = round(current_price * 0.95, 2)  # 5% below
            
            order = AlpacaOrder(
                symbol='AAPL',
                qty=1,
                side='buy',
                type='limit',
                limit_price=limit_price
            )
            
            result = await broker.place_order(order)
            
            assert result['type'] == 'limit'
            assert float(result['limit_price']) == limit_price
            
            # Cancel
            await broker.cancel_order(result['id'])
    
    @pytest.mark.asyncio
    async def test_get_positions(self, broker):
        """Test getting positions."""
        positions = await broker.get_positions()
        
        assert isinstance(positions, list)
        
        for pos in positions:
            assert 'symbol' in pos
            assert 'qty' in pos
            assert 'market_value' in pos
    
    @pytest.mark.asyncio
    async def test_get_orders(self, broker):
        """Test getting order history."""
        orders = await broker.get_orders()
        
        assert isinstance(orders, list)
        
        for order in orders:
            assert 'id' in order
            assert 'symbol' in order
            assert 'status' in order
    
    @pytest.mark.asyncio
    async def test_get_asset_info(self, broker):
        """Test getting asset information."""
        asset = await broker.get_asset('AAPL')
        
        assert asset is not None
        assert asset['symbol'] == 'AAPL'
        assert 'name' in asset
        assert 'exchange' in asset
        assert asset['tradable'] == True
    
    @pytest.mark.asyncio
    async def test_get_bars(self, broker):
        """Test getting historical bars."""
        bars = await broker.get_bars('AAPL', timeframe='1Day', limit=5)
        
        assert isinstance(bars, list)
        assert len(bars) <= 5
        
        if bars:
            bar = bars[0]
            assert 'o' in bar  # Open
            assert 'h' in bar  # High
            assert 'l' in bar  # Low
            assert 'c' in bar  # Close
            assert 'v' in bar  # Volume
    
    @pytest.mark.asyncio
    async def test_cancel_all_orders(self, broker):
        """Test canceling all open orders."""
        # Get all open orders
        orders = await broker.get_orders(status='open')
        
        for order in orders:
            result = await broker.cancel_order(order['id'])
            assert result == True


class TestMultiSymbolData:
    """Test multi-symbol operations."""
    
    @pytest.mark.asyncio
    async def test_multiple_symbol_quotes(self):
        """Test getting data for multiple symbols."""
        broker = AlpacaBroker(paper=True)
        
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        
        results = await asyncio.gather(
            *[broker.get_bars(sym, limit=1) for sym in symbols],
            return_exceptions=True
        )
        
        # At least 3 should succeed
        successful = [r for r in results if not isinstance(r, Exception)]
        assert len(successful) >= 3


class TestErrorHandling:
    """Test error handling for broker API."""
    
    @pytest.mark.asyncio
    async def test_invalid_symbol(self):
        """Test handling invalid symbol."""
        broker = AlpacaBroker(paper=True)
        
        with pytest.raises(Exception):
            await broker.get_asset('INVALID_SYMBOL_XYZ')
    
    @pytest.mark.asyncio
    async def test_invalid_order(self):
        """Test handling invalid order."""
        broker = AlpacaBroker(paper=True)
        
        # Try to sell more than we own
        order = AlpacaOrder(
            symbol='AAPL',
            qty=999999,  # Ridiculous amount
            side='sell',
            type='market'
        )
        
        # Should fail or be rejected
        result = await broker.place_order(order)
        assert result['status'] in ['rejected', 'pending', 'accepted']


class TestPolygonDataProvider:
    """Test Polygon.io data provider."""
    
    @pytest.fixture
    async def provider(self):
        """Create Polygon provider."""
        from data_providers.polygon_provider import PolygonDataProvider
        
        provider = PolygonDataProvider()
        yield provider
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv('POLYGON_API_KEY'),
        reason="No Polygon API key"
    )
    async def test_rest_api_last_trade(self, provider):
        """Test REST API for last trade."""
        trade = await provider.get_last_trade('AAPL')
        
        assert trade is not None
        assert 'last' in trade
        assert 'price' in trade['last']
        
        print(f"AAPL Last Price: ${trade['last']['price']}")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv('POLYGON_API_KEY'),
        reason="No Polygon API key"
    )
    async def test_rest_api_aggregates(self, provider):
        """Test getting aggregate bars."""
        from datetime import datetime, timedelta
        
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        bars = await provider.get_aggregates(
            'AAPL', 1, 'day', from_date, to_date
        )
        
        assert isinstance(bars, list)
        assert len(bars) > 0
        
        bar = bars[0]
        assert 'o' in bar
        assert 'h' in bar
        assert 'l' in bar
        assert 'c' in bar
        assert 'v' in bar
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv('POLYGON_API_KEY'),
        reason="No Polygon API key"
    )
    async def test_websocket_connection(self, provider):
        """Test WebSocket connection."""
        messages = []
        
        async def collect_trade(trade):
            messages.append(trade)
        
        provider.on_trade(collect_trade)
        
        await provider.connect()
        await provider.subscribe_trades(['AAPL'])
        
        # Wait for some messages
        await asyncio.sleep(5)
        
        await provider.disconnect()
        
        # Should have received at least one message
        assert len(messages) > 0
        
        trade = messages[0]
        assert trade.symbol == 'AAPL'
        assert trade.price > 0


# Run with: pytest tests/integration/test_broker_integration.py -v
# Or with live trading: ALPACA_API_KEY=xxx ALPACA_SECRET_KEY=yyy pytest tests/integration/test_broker_integration.py -v
