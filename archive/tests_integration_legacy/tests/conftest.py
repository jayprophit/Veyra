"""
Pytest Configuration and Fixtures
===================================
Shared fixtures for all test types.
"""

import pytest
import sys
import os
from datetime import date, datetime, timedelta
from typing import Generator

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend', 'app'))

try:
    from database_layer import DatabaseManager, DatabaseConfig
    from api.fuel_tracker import db as fuel_db
except ImportError:
    # Create mock classes for testing
    class DatabaseManager:
        def __init__(self, config):
            self.config = config
        def close(self):
            pass
    
    class DatabaseConfig:
        def __init__(self, db_type='sqlite', sqlite_path=':memory:'):
            self.db_type = db_type
            self.sqlite_path = sqlite_path


@pytest.fixture(scope="function")
def db() -> Generator[DatabaseManager, None, None]:
    """Create fresh database for each test."""
    # Use in-memory SQLite for tests
    config = DatabaseConfig(
        db_type='sqlite',
        sqlite_path=':memory:'
    )
    db = DatabaseManager(config)
    
    yield db
    
    # Cleanup
    db.close()


@pytest.fixture(scope="function")
def test_user_id() -> str:
    """Standard test user ID."""
    return "test_user_001"


@pytest.fixture(scope="function")
def sample_vehicle_data() -> dict:
    """Sample vehicle data for tests."""
    return {
        "make": "Ford",
        "model": "Focus",
        "registration": "AB66 XYZ",
        "fuel_type": "petrol",
        "engine_size_cc": 999,
        "year": 2016
    }


@pytest.fixture(scope="function")
def sample_mileage_entry() -> dict:
    """Sample mileage entry for tests."""
    return {
        "trip_date": date.today(),
        "start_location": "Home Office",
        "end_location": "Client Site",
        "start_postcode": "SW1A 1AA",
        "end_postcode": "M1 1AA",
        "purpose": "Client meeting",
        "distance_miles": 50.0,
        "passengers": 1,
        "notes": "Return journey"
    }


@pytest.fixture(scope="function")
def sample_fuel_purchase() -> dict:
    """Sample fuel purchase for tests."""
    return {
        "purchase_date": date.today(),
        "odometer_reading": 45000,
        "litres": 35.5,
        "price_per_litre": 1.45,
        "total_cost": 51.48,
        "fuel_type": "petrol",
        "is_full_tank": True,
        "station": "Shell Manchester",
        "notes": "Weekly fill-up"
    }


@pytest.fixture(scope="function")
def sample_subscription() -> dict:
    """Sample subscription data."""
    return {
        "name": "Netflix",
        "provider": "Netflix Inc",
        "cost_monthly": 15.99,
        "category": "entertainment",
        "billing_cycle": "monthly"
    }


@pytest.fixture(scope="session")
def test_data_dir() -> str:
    """Directory for test data files."""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


# Async support
@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# TRADING FIXTURES - Veyra
# ============================================================================

@pytest.fixture(scope="function")
def sample_trade() -> dict:
    """Sample trade for testing."""
    return {
        'ticker': 'AAPL',
        'quantity': 100,
        'price': 150.25,
        'trade_type': 'BUY',
        'timestamp': datetime.now(),
        'order_id': 'ORD-001'
    }


@pytest.fixture(scope="function")
def sample_portfolio() -> dict:
    """Sample portfolio for testing."""
    return {
        'user_id': 'test-user-1',
        'name': 'Main Portfolio',
        'cash_balance': 100000.00,
        'positions': {
            'AAPL': {'shares': 100, 'avg_cost': 150.00},
            'GOOGL': {'shares': 50, 'avg_cost': 2000.00},
        }
    }


@pytest.fixture(scope="function")
def sample_market_data() -> dict:
    """Sample market data for testing."""
    return {
        'ticker': 'AAPL',
        'price': 150.25,
        'bid': 150.20,
        'ask': 150.30,
        'volume': 1000000,
        'market_cap': 2000000000000,
        'timestamp': datetime.now(),
    }


@pytest.fixture(scope="function")
def sample_user_profile() -> dict:
    """Sample user profile."""
    return {
        'user_id': 'test-user-1',
        'email': 'test@example.com',
        'username': 'testuser',
        'full_name': 'Test User',
        'is_verified': True,
        'is_active': True,
        'created_at': datetime.now(),
    }


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def mock_auth_token() -> str:
    """Mock JWT token for testing."""
    # In production, use real JWT generation
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyLTEifQ.mock"


@pytest.fixture(scope="function")
def mock_auth_headers(mock_auth_token: str) -> dict:
    """Mock authorization headers."""
    return {
        'Authorization': f'Bearer {mock_auth_token}',
        'Content-Type': 'application/json',
    }


# ============================================================================
# ERROR RESPONSE FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def mock_error_responses() -> dict:
    """Mock API error responses."""
    return {
        'unauthorized': {'status': 401, 'detail': 'Not authenticated'},
        'forbidden': {'status': 403, 'detail': 'Forbidden'},
        'not_found': {'status': 404, 'detail': 'Not found'},
        'bad_request': {'status': 400, 'detail': 'Bad request'},
        'server_error': {'status': 500, 'detail': 'Internal server error'},
        'validation_error': {'status': 422, 'detail': 'Validation failed'},
    }
