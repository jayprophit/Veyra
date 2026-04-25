"""
Integration Tests - API Layer
=============================
End-to-end tests for all API endpoints.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))

from api_server import app


client = TestClient(app)


class TestPortfolioAPI:
    """Integration tests for portfolio endpoints."""
    
    def test_get_portfolio(self):
        """Test GET /api/portfolio returns portfolio data."""
        response = client.get('/api/portfolio')
        assert response.status_code == 200
        
        data = response.json()
        assert 'holdings' in data
        assert 'total_value' in data
    
    def test_add_holding(self):
        """Test POST /api/portfolio adds new holding."""
        payload = {
            'symbol': 'TEST',
            'name': 'Test Company',
            'shares': 100,
            'price': 50.0
        }
        
        response = client.post('/api/portfolio', json=payload)
        assert response.status_code == 200
        
        # Verify it was added
        get_response = client.get('/api/portfolio')
        holdings = get_response.json()['holdings']
        assert any(h['symbol'] == 'TEST' for h in holdings)
    
    def test_update_holding(self):
        """Test PUT /api/portfolio/{symbol} updates holding."""
        # First add a holding
        client.post('/api/portfolio', json={
            'symbol': 'UPDATE_TEST',
            'shares': 10,
            'price': 100.0
        })
        
        # Update it
        response = client.put('/api/portfolio/UPDATE_TEST', json={
            'shares': 20
        })
        assert response.status_code == 200
        
        # Verify update
        portfolio = client.get('/api/portfolio').json()
        holding = next(h for h in portfolio['holdings'] if h['symbol'] == 'UPDATE_TEST')
        assert holding['shares'] == 20
    
    def test_delete_holding(self):
        """Test DELETE /api/portfolio/{symbol} removes holding."""
        # Add and then delete
        client.post('/api/portfolio', json={
            'symbol': 'DELETE_TEST',
            'shares': 5,
            'price': 50.0
        })
        
        response = client.delete('/api/portfolio/DELETE_TEST')
        assert response.status_code == 200
        
        # Verify deletion
        portfolio = client.get('/api/portfolio').json()
        assert not any(h['symbol'] == 'DELETE_TEST' for h in portfolio['holdings'])


class TestTaxAPI:
    """Integration tests for tax endpoints."""
    
    def test_get_tax_summary(self):
        """Test GET /api/tax/summary returns tax data."""
        response = client.get('/api/tax/summary')
        assert response.status_code == 200
        
        data = response.json()
        assert 'tax_year' in data
        assert 'total_gains' in data
    
    def test_add_tax_event(self):
        """Test POST /api/tax/events adds tax event."""
        payload = {
            'symbol': 'AAPL',
            'event_type': 'SALE',
            'quantity': 10,
            'proceeds': 1850.0,
            'cost_basis': 1500.0,
            'date': '2024-06-15',
            'jurisdiction': 'UK'
        }
        
        response = client.post('/api/tax/events', json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data['gain_loss'] == 350.0
    
    def test_international_tax_calculation(self):
        """Test international multi-jurisdiction tax calculation."""
        # Add UK event
        client.post('/api/tax/events', json={
            'symbol': 'AAPL',
            'event_type': 'SALE',
            'quantity': 10,
            'proceeds': 1850.0,
            'cost_basis': 1500.0,
            'date': '2024-06-15',
            'jurisdiction': 'UK'
        })
        
        # Add US event
        client.post('/api/tax/events', json={
            'symbol': 'MSFT',
            'event_type': 'SALE',
            'quantity': 5,
            'proceeds': 1100.0,
            'cost_basis': 1000.0,
            'date': '2024-06-15',
            'jurisdiction': 'US'
        })
        
        response = client.get('/api/tax/international/summary')
        assert response.status_code == 200
        
        data = response.json()
        assert 'jurisdictions' in data
        assert len(data['jurisdictions']) >= 2


class TestFuelAPI:
    """Integration tests for fuel tracking endpoints."""
    
    def test_log_mileage(self):
        """Test POST /api/fuel/log records mileage."""
        payload = {
            'vehicle_id': 1,
            'date': '2024-06-15',
            'distance': 100.5,
            'amount': 50.0,
            'purpose': 'Business meeting'
        }
        
        response = client.post('/api/fuel/log', json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'logged'
    
    def test_get_mileage_summary(self):
        """Test GET /api/fuel/summary returns HMRC data."""
        # Log some mileage first
        client.post('/api/fuel/log', json={
            'vehicle_id': 1,
            'date': '2024-01-15',
            'distance': 5000.0,
            'purpose': 'Business'
        })
        
        response = client.get('/api/fuel/summary?vehicle_id=1&year=2024')
        assert response.status_code == 200
        
        data = response.json()
        assert 'total_miles' in data
        assert 'claimable_amount' in data


class TestOperationsAPI:
    """Integration tests for operations endpoints."""
    
    def test_get_system_health(self):
        """Test GET /api/ops/health returns system status."""
        response = client.get('/api/ops/health')
        assert response.status_code == 200
        
        data = response.json()
        assert 'status' in data
        assert data['status'] in ['healthy', 'degraded', 'critical']
    
    def test_get_costs(self):
        """Test GET /api/ops/costs returns FinOps data."""
        response = client.get('/api/ops/costs')
        assert response.status_code == 200
        
        data = response.json()
        assert 'total_current_month' in data
        assert 'breakdown' in data
    
    def test_deployment_status(self):
        """Test GET /api/ops/deploy/status."""
        response = client.get('/api/ops/deploy/status')
        assert response.status_code == 200
        
        data = response.json()
        assert 'status' in data
        assert 'version' in data


class TestBrokerAPI:
    """Integration tests for broker connections."""
    
    def test_get_broker_status(self):
        """Test GET /api/broker/status returns connection status."""
        response = client.get('/api/broker/status')
        assert response.status_code == 200
        
        data = response.json()
        assert 'alpaca' in data
        assert 'polygon' in data
    
    def test_get_stock_quote(self):
        """Test GET /api/broker/quote/{symbol}."""
        response = client.get('/api/broker/quote/AAPL')
        assert response.status_code in [200, 503]  # 503 if broker not connected
        
        if response.status_code == 200:
            data = response.json()
            assert 'symbol' in data
            assert 'price' in data
    
    @pytest.mark.skip(reason="Requires live broker connection")
    def test_submit_order(self):
        """Test POST /api/broker/order (paper trading)."""
        payload = {
            'symbol': 'AAPL',
            'qty': 1,
            'side': 'buy',
            'type': 'market',
            'time_in_force': 'day'
        }
        
        response = client.post('/api/broker/order', json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'accepted'


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality."""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket endpoint accepts connections."""
        async with AsyncClient(app=app, base_url='http://test') as client:
            # WebSocket test would go here
            # Note: Requires actual WebSocket client library
            pass
    
    def test_websocket_stats(self):
        """Test GET /api/ws/stats returns connection stats."""
        response = client.get('/api/ws/stats')
        assert response.status_code == 200
        
        data = response.json()
        assert 'total_connections' in data
        assert 'active_connections' in data


class TestErrorHandling:
    """Tests for API error handling."""
    
    def test_404_error(self):
        """Test 404 for non-existent endpoint."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_422_validation_error(self):
        """Test 422 for invalid input."""
        # Missing required field
        response = client.post('/api/portfolio', json={
            'symbol': 'TEST'
            # Missing 'shares' and 'price'
        })
        assert response.status_code == 422
    
    def test_database_error_handling(self):
        """Test graceful handling of database errors."""
        # This would require mocking database failure
        pass


@pytest.fixture(scope='module')
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
