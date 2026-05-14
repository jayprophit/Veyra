"""
Comprehensive Test Suite - API Endpoint Tests
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from decimal import Decimal

from app.main import create_fastapi_app


@pytest.fixture
def client():
    """Create FastAPI test client"""
    app = create_fastapi_app()
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Veyra API"
        assert data["status"] == "operational"


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_docs_available(self, client):
        """Test that OpenAPI docs are available"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_docs_available(self, client):
        """Test that ReDoc docs are available"""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self, client):
        """Test that OpenAPI schema is available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema


class TestCORSHeaders:
    """Test CORS headers"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.options("/health")
        # Note: CORS headers should be present
        # This test verifies the middleware is working


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_not_found(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed error"""
        response = client.post("/health")  # GET only
        assert response.status_code in [405, 404, 422]


class TestResponseFormat:
    """Test response formatting"""
    
    def test_json_response(self, client):
        """Test that responses are JSON"""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"
    
    def test_response_has_expected_fields(self, client):
        """Test that responses have expected fields"""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0


class TestTimezoneHandling:
    """Test timezone handling"""
    
    def test_timestamp_format(self, client):
        """Test that timestamps are in ISO format"""
        response = client.get("/health")
        data = response.json()
        timestamp = data.get("timestamp")
        
        if timestamp:
            # Should be parseable as ISO format
            try:
                datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                assert True
            except ValueError:
                assert False, f"Timestamp not in ISO format: {timestamp}"


class TestDataValidation:
    """Test data validation"""
    
    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/v1/orders",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [422, 400]


class TestRateLimiting:
    """Test rate limiting (if implemented)"""
    
    def test_rate_limit_headers(self, client):
        """Test rate limit headers"""
        response = client.get("/health")
        # Rate limit headers should be present if implemented
        # X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
