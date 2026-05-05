"""
Integration Tests for Authentication System
==========================================
Comprehensive integration tests for authentication, authorization, and security.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from httpx import AsyncClient
import jwt
from src.backend.app.auth.auth_service import AuthService, AuthConfig, UserRole, Permission
from src.backend.app.main import app


class TestAuthenticationIntegration:
    """Integration tests for authentication system."""
    
    @pytest.fixture
    async def auth_service(self):
        """Create auth service for testing."""
        config = AuthConfig(
            secret_key="test-secret-key-for-integration-tests",
            access_token_expire_minutes=30,
            redis_url="redis://localhost:6379/1"
        )
        return AuthService(config)
    
    @pytest.fixture
    async def test_client(self):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_user_registration_and_login(self, auth_service, test_client):
        """Test complete user registration and login flow."""
        # Register user
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "role": "trader"
        }
        
        response = await test_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Login user
        login_data = {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        response = await test_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        # Verify token
        payload = auth_service.verify_token(tokens["access_token"])
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "trader"
    
    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, auth_service, test_client):
        """Test token refresh mechanism."""
        # Login and get tokens
        login_data = {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        response = await test_client.post("/api/v1/auth/login", json=login_data)
        tokens = response.json()
        
        # Use refresh token to get new access token
        refresh_data = {
            "refresh_token": tokens["refresh_token"]
        }
        
        response = await test_client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        new_tokens = response.json()
        assert "access_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]
    
    @pytest.mark.asyncio
    async def test_permission_based_access(self, auth_service, test_client):
        """Test role-based permission system."""
        # Create admin user
        admin_data = {
            "email": "admin@example.com",
            "username": "admin",
            "password": "AdminPass123!",
            "role": "admin"
        }
        
        response = await test_client.post("/api/v1/auth/register", json=admin_data)
        assert response.status_code == 201
        
        # Login as admin
        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": "admin@example.com",
            "password": "AdminPass123!"
        })
        admin_tokens = login_response.json()
        
        # Access admin endpoint with admin token
        headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}
        response = await test_client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 200
        
        # Create regular user
        user_data = {
            "email": "user@example.com",
            "username": "user",
            "password": "UserPass123!",
            "role": "viewer"
        }
        
        await test_client.post("/api/v1/auth/register", json=user_data)
        user_login = await test_client.post("/api/v1/auth/login", json={
            "email": "user@example.com",
            "password": "UserPass123!"
        })
        user_tokens = user_login.json()
        
        # Try to access admin endpoint with user token
        user_headers = {"Authorization": f"Bearer {user_tokens['access_token']}"}
        response = await test_client.get("/api/v1/admin/users", headers=user_headers)
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, auth_service, test_client):
        """Test API rate limiting."""
        # Login to get token
        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Make rapid requests to trigger rate limit
        responses = []
        for i in range(105):  # Exceed rate limit of 100
            response = await test_client.get("/api/v1/portfolio", headers=headers)
            responses.append(response)
            if response.status_code == 429:
                break
        
        # Should hit rate limit
        assert any(r.status_code == 429 for r in responses)
        
        # Check rate limit headers
        rate_limited_response = next(r for r in responses if r.status_code == 429)
        assert "Retry-After" in rate_limited_response.headers
    
    @pytest.mark.asyncio
    async def test_api_key_authentication(self, auth_service, test_client):
        """Test API key authentication."""
        # Generate API key for user
        api_key = auth_service.generate_api_key("test-user", "test-key")
        
        # Use API key to access endpoint
        headers = {"X-API-Key": api_key}
        response = await test_client.get("/api/v1/portfolio", headers=headers)
        assert response.status_code == 200
        
        # Test invalid API key
        invalid_headers = {"X-API-Key": "invalid-key"}
        response = await test_client.get("/api/v1/portfolio", headers=invalid_headers)
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_account_lockout(self, auth_service, test_client):
        """Test account lockout after failed attempts."""
        # Make multiple failed login attempts
        for i in range(6):  # Exceed max attempts
            response = await test_client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "wrong-password"
            })
            if i < 5:
                assert response.status_code == 401
            else:
                assert response.status_code == 423  # Locked
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, auth_service, test_client):
        """Test handling of concurrent authenticated requests."""
        # Login to get token
        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Make concurrent requests
        async def make_request():
            return await test_client.get("/api/v1/portfolio", headers=headers)
        
        tasks = [make_request() for _ in range(50)]
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)
    
    @pytest.mark.asyncio
    async def test_token_expiration(self, auth_service, test_client):
        """Test token expiration handling."""
        # Create expired token
        user = auth_service._get_user_by_email("test@example.com")
        expired_token = jwt.encode(
            {
                "sub": user.id,
                "exp": datetime.utcnow() - timedelta(minutes=1),
                "type": "access"
            },
            auth_service.config.secret_key,
            algorithm=auth_service.config.algorithm
        )
        
        # Try to use expired token
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await test_client.get("/api/v1/portfolio", headers=headers)
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_end_to_end_trading_flow():
    """Test complete end-to-end trading flow with authentication."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login user
        user_data = {
            "email": "trader@example.com",
            "username": "trader",
            "password": "TraderPass123!",
            "role": "trader"
        }
        
        await client.post("/api/v1/auth/register", json=user_data)
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "trader@example.com",
            "password": "TraderPass123!"
        })
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Get portfolio
        portfolio_response = await client.get("/api/v1/portfolio", headers=headers)
        assert portfolio_response.status_code == 200
        
        # Place trade
        trade_data = {
            "symbol": "AAPL",
            "side": "buy",
            "quantity": 10,
            "order_type": "market"
        }
        
        trade_response = await client.post("/api/v1/trading/orders", json=trade_data, headers=headers)
        assert trade_response.status_code == 201
        
        # Get order status
        order_id = trade_response.json()["order_id"]
        order_response = await client.get(f"/api/v1/trading/orders/{order_id}", headers=headers)
        assert order_response.status_code == 200
        
        # Cancel order
        cancel_response = await client.delete(f"/api/v1/trading/orders/{order_id}", headers=headers)
        assert cancel_response.status_code == 200
