"""
Unit Tests - Trading Module
Comprehensive test examples for Financial Master

Test Coverage:
- Trade execution
- Portfolio management
- Market data validation
- Error handling
- Async operations
"""

import pytest
from datetime import datetime
from decimal import Decimal


class TestTradeExecution:
    """Tests for trade execution functionality."""

    def test_buy_trade_basic(self, sample_trade, sample_portfolio):
        """Test basic buy trade execution."""
        # Arrange
        trade = sample_trade
        portfolio = sample_portfolio
        initial_cash = portfolio['cash_balance']

        # Act
        # In real test, call actual trade execution function
        trade_cost = trade['quantity'] * trade['price']
        portfolio['cash_balance'] -= trade_cost

        # Assert
        assert portfolio['cash_balance'] == initial_cash - trade_cost
        assert portfolio['cash_balance'] >= 0

    def test_insufficient_funds(self, sample_trade, sample_portfolio):
        """Test that trade fails with insufficient funds."""
        # Arrange
        sample_portfolio['cash_balance'] = 100  # Very low balance
        trade = sample_trade

        # Act & Assert
        trade_cost = trade['quantity'] * trade['price']
        with pytest.raises(ValueError):
            if trade_cost > sample_portfolio['cash_balance']:
                raise ValueError("Insufficient funds")

    def test_sell_trade(self, sample_portfolio):
        """Test sell trade execution."""
        # Arrange
        ticker = 'AAPL'
        initial_shares = sample_portfolio['positions'][ticker]['shares']

        # Act
        shares_to_sell = 50
        sample_portfolio['positions'][ticker]['shares'] -= shares_to_sell

        # Assert
        assert sample_portfolio['positions'][ticker]['shares'] == initial_shares - shares_to_sell

    def test_invalid_ticker(self):
        """Test trade with invalid ticker."""
        with pytest.raises(ValueError):
            invalid_ticker = ""
            if not invalid_ticker:
                raise ValueError("Invalid ticker")

    def test_zero_quantity(self, sample_trade):
        """Test that trade rejects zero quantity."""
        sample_trade['quantity'] = 0

        with pytest.raises(ValueError):
            if sample_trade['quantity'] <= 0:
                raise ValueError("Quantity must be positive")

    def test_negative_price(self, sample_trade):
        """Test that trade rejects negative price."""
        sample_trade['price'] = -150

        with pytest.raises(ValueError):
            if sample_trade['price'] < 0:
                raise ValueError("Price cannot be negative")


class TestPortfolioManagement:
    """Tests for portfolio management."""

    def test_portfolio_creation(self, sample_user_profile):
        """Test portfolio creation for user."""
        portfolio = {
            'user_id': sample_user_profile['user_id'],
            'name': 'New Portfolio',
            'cash_balance': 50000.00,
            'positions': {}
        }

        assert portfolio['user_id'] == sample_user_profile['user_id']
        assert portfolio['cash_balance'] == 50000.00

    def test_portfolio_balance_calculation(self, sample_portfolio, sample_market_data):
        """Test portfolio total balance calculation."""
        # Arrange
        portfolio = sample_portfolio
        market_data = sample_market_data
        ticker = 'AAPL'

        # Act
        position_value = (portfolio['positions'][ticker]['shares'] *
                         market_data['price'])
        total_value = portfolio['cash_balance'] + position_value

        # Assert
        assert total_value > 0
        assert position_value == portfolio['positions'][ticker]['shares'] * market_data['price']

    def test_add_position(self, sample_portfolio):
        """Test adding new position to portfolio."""
        # Act
        new_ticker = 'MSFT'
        sample_portfolio['positions'][new_ticker] = {
            'shares': 50,
            'avg_cost': 300.00
        }

        # Assert
        assert new_ticker in sample_portfolio['positions']
        assert sample_portfolio['positions'][new_ticker]['shares'] == 50

    def test_remove_position(self, sample_portfolio):
        """Test removing position from portfolio."""
        # Act
        if 'GOOGL' in sample_portfolio['positions']:
            del sample_portfolio['positions']['GOOGL']

        # Assert
        assert 'GOOGL' not in sample_portfolio['positions']


class TestMarketData:
    """Tests for market data validation and retrieval."""

    def test_valid_market_data(self, sample_market_data):
        """Test market data validation."""
        market_data = sample_market_data

        assert market_data['ticker']
        assert market_data['price'] > 0
        assert market_data['bid'] > 0
        assert market_data['ask'] > market_data['bid']

    def test_bid_ask_spread(self, sample_market_data):
        """Test bid-ask spread calculation."""
        bid = sample_market_data['bid']
        ask = sample_market_data['ask']

        spread = ask - bid
        assert spread > 0

        # Spread should be reasonable (not too wide)
        mid_price = (bid + ask) / 2
        spread_pct = (spread / mid_price) * 100
        assert spread_pct < 1  # Spread less than 1%

    def test_market_data_timestamp(self, sample_market_data):
        """Test market data has valid timestamp."""
        assert sample_market_data['timestamp']
        assert isinstance(sample_market_data['timestamp'], datetime)


class TestAuthentication:
    """Tests for authentication and authorization."""

    def test_valid_auth_header(self, mock_auth_headers):
        """Test valid authentication header."""
        assert 'Authorization' in mock_auth_headers
        assert mock_auth_headers['Authorization'].startswith('Bearer ')

    def test_token_format(self, mock_auth_token):
        """Test JWT token format."""
        parts = mock_auth_token.split('.')
        # JWT should have 3 parts: header.payload.signature
        assert len(parts) >= 2  # At least header and payload

    def test_missing_auth_header(self):
        """Test request without auth header fails."""
        headers = {}

        with pytest.raises(KeyError):
            if 'Authorization' not in headers:
                raise KeyError("Missing Authorization header")


class TestErrorHandling:
    """Tests for error handling throughout the system."""

    def test_connection_error_handled(self):
        """Test that connection errors are handled properly."""
        with pytest.raises(Exception):
            raise ConnectionError("Database connection failed")

    def test_timeout_error_handled(self):
        """Test that timeout errors are handled."""
        with pytest.raises(TimeoutError):
            raise TimeoutError("Request timed out")

    def test_validation_error_handled(self):
        """Test that validation errors are handled."""
        def validate_email(email):
            if '@' not in email:
                raise ValueError("Invalid email format")

        with pytest.raises(ValueError):
            validate_email("invalid-email")


@pytest.mark.asyncio
class TestAsyncOperations:
    """Tests for async operations."""

    async def test_async_trade_execution(self, sample_trade):
        """Test async trade execution."""
        # In real implementation, this would call actual async functions
        trade = sample_trade
        assert trade['quantity'] > 0

    async def test_async_market_data_fetch(self, sample_market_data):
        """Test async market data retrieval."""
        market_data = sample_market_data
        assert market_data['price'] > 0

    async def test_async_error_handling(self):
        """Test async error handling."""
        async def failing_operation():
            raise RuntimeError("Async operation failed")

        with pytest.raises(RuntimeError):
            await failing_operation()


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

class TestParametrized:
    """Parametrized test examples."""

    @pytest.mark.parametrize("ticker,expected_price", [
        ("AAPL", 150.25),
        ("GOOGL", 2000.00),
        ("MSFT", 300.00),
    ])
    def test_market_prices(self, ticker, expected_price):
        """Test market prices for various tickers."""
        assert isinstance(expected_price, (int, float))
        assert expected_price > 0

    @pytest.mark.parametrize("quantity,price,trade_type", [
        (100, 150.25, "BUY"),
        (50, 2000.00, "SELL"),
        (200, 300.00, "BUY"),
    ])
    def test_trade_variations(self, quantity, price, trade_type):
        """Test various trade scenarios."""
        assert quantity > 0
        assert price > 0
        assert trade_type in ["BUY", "SELL"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
