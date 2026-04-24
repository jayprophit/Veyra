"""
Unit Tests: API Layer
=====================
Test FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from api_server import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test /api/health returns healthy."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_system_status(self):
        """Test /api/system/status returns system info."""
        response = client.get("/api/system/status")
        assert response.status_code == 200
        data = response.json()
        assert data["api_running"] is True
        assert "database_connected" in data


class TestFuelTrackerAPI:
    """Test fuel tracker endpoints."""
    
    def test_list_vehicles_empty(self):
        """Test listing vehicles for new user."""
        response = client.get("/api/fuel/vehicles?user_id=test_empty")
        assert response.status_code == 200
        data = response.json()
        assert "vehicles" in data
        assert len(data["vehicles"]) == 0
    
    def test_add_vehicle(self):
        """Test adding a vehicle."""
        vehicle_data = {
            "make": "Ford",
            "model": "Focus",
            "registration": "AB66 XYZ",
            "fuel_type": "petrol",
            "engine_size_cc": 999,
            "year": 2016
        }
        
        response = client.post(
            "/api/fuel/vehicles?user_id=test_add",
            json=vehicle_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert "vehicle_id" in data
    
    def test_log_mileage(self):
        """Test logging mileage."""
        from datetime import date
        
        mileage_data = {
            "trip_date": date.today().isoformat(),
            "start_location": "Home",
            "end_location": "Office",
            "purpose": "Business meeting",
            "distance_miles": 50.0,
            "passengers": 0
        }
        
        response = client.post(
            "/api/fuel/mileage?user_id=test_mileage",
            json=mileage_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "logged"
        assert "claimable_gbp" in data
        assert data["claimable_gbp"] == 22.50  # 50 miles × 45p
    
    def test_mileage_tiered_rates(self):
        """Test tiered rates (45p then 25p)."""
        from datetime import date
        
        user_id = "test_tiered"
        
        # First trip - should be 45p
        mileage_data = {
            "trip_date": date.today().isoformat(),
            "start_location": "A",
            "end_location": "B",
            "purpose": "Business",
            "distance_miles": 50.0,
            "passengers": 0
        }
        
        response = client.post(
            f"/api/fuel/mileage?user_id={user_id}",
            json=mileage_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rate_applied"] == "45p"
        assert data["claimable_gbp"] == 22.50
        
        # Add trips to exceed 10k miles
        for i in range(200):
            client.post(
                f"/api/fuel/mileage?user_id={user_id}",
                json={
                    "trip_date": date.today().isoformat(),
                    "start_location": "A",
                    "end_location": "B",
                    "purpose": "Business",
                    "distance_miles": 50.0,
                    "passengers": 0
                }
            )
        
        # Next trip should be 25p
        response = client.post(
            f"/api/fuel/mileage?user_id={user_id}",
            json=mileage_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rate_applied"] == "25p"
        assert data["claimable_gbp"] == 12.50


class TestPortfolioAPI:
    """Test portfolio endpoints."""
    
    def test_get_holdings(self):
        """Test getting holdings."""
        response = client.get("/api/holdings")
        assert response.status_code == 200
        # Response format depends on auth, may return 401 without token
    
    def test_get_portfolio_summary(self):
        """Test getting portfolio summary."""
        response = client.get("/api/portfolio")
        # May require auth
        assert response.status_code in [200, 401]


class TestTaxAPI:
    """Test tax endpoints."""
    
    def test_get_tax_summary(self):
        """Test getting tax summary."""
        response = client.get("/api/tax/summary?tax_year=2024-25")
        assert response.status_code in [200, 401]


class TestErrorHandling:
    """Test API error handling."""
    
    def test_invalid_endpoint(self):
        """Test 404 for invalid endpoint."""
        response = client.get("/api/invalid_endpoint")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Test 405 for invalid method."""
        response = client.delete("/api/health")
        assert response.status_code == 405


# Run with: pytest tests/unit/test_api.py -v
