"""
Performance Tests: API Load Testing
====================================
Test API performance under load.
"""

import pytest
import asyncio
import time
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))
from api_server import app

client = TestClient(app)


class TestAPIPerformance:
    """Test API endpoint performance."""
    
    def test_health_check_performance(self):
        """Test health check responds within 100ms."""
        start = time.time()
        response = client.get("/api/health")
        elapsed = (time.time() - start) * 1000  # ms
        
        assert response.status_code == 200
        assert elapsed < 100, f"Health check took {elapsed}ms, expected <100ms"
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests."""
        import concurrent.futures
        
        def make_request():
            return client.get("/api/health")
        
        start = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed = time.time() - start
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)
        
        # Should complete within 5 seconds
        assert elapsed < 5, f"50 requests took {elapsed}s, expected <5s"
        
        print(f"50 concurrent requests completed in {elapsed:.2f}s")
    
    def test_fuel_api_performance(self):
        """Test fuel API endpoints performance."""
        # Test vehicle list
        start = time.time()
        response = client.get("/api/fuel/vehicles?user_id=perf_test")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 200, f"Vehicle list took {elapsed}ms, expected <200ms"
        
        # Test mileage summary
        start = time.time()
        response = client.get("/api/fuel/summary/2026-27?user_id=perf_test")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 300, f"Mileage summary took {elapsed}ms, expected <300ms"


class TestDatabasePerformance:
    """Test database operation performance."""
    
    @pytest.fixture
    def db(self):
        from database_layer import DatabaseManager, DatabaseConfig
        config = DatabaseConfig(db_type='sqlite', sqlite_path=':memory:')
        db = DatabaseManager(config)
        yield db
        db.close()
    
    def test_bulk_insert_performance(self, db):
        """Test bulk insert operations."""
        import time
        
        start = time.time()
        
        # Insert 1000 vehicles
        for i in range(1000):
            db.add_vehicle(
                user_id="bulk_test",
                make="Ford",
                model=f"Model_{i}",
                registration=f"REG{i}"
            )
        
        elapsed = time.time() - start
        
        # Should complete within 10 seconds
        assert elapsed < 10, f"1000 inserts took {elapsed}s, expected <10s"
        
        # Verify
        vehicles = db.get_vehicles("bulk_test")
        assert len(vehicles) == 1000
        
        print(f"1000 inserts completed in {elapsed:.2f}s")
    
    def test_query_performance(self, db):
        """Test query performance with large dataset."""
        # Setup
        for i in range(1000):
            db.add_vehicle("query_test", "Ford", f"Model_{i}")
        
        # Query test
        start = time.time()
        vehicles = db.get_vehicles("query_test")
        elapsed = time.time() - start
        
        # Should complete within 500ms
        assert elapsed < 0.5, f"Query took {elapsed}s, expected <0.5s"
        assert len(vehicles) == 1000


class TestMemoryUsage:
    """Test memory usage under load."""
    
    def test_memory_stability(self):
        """Test memory doesn't grow unbounded."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make many requests
        for _ in range(100):
            client.get("/api/health")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be less than 50MB
        assert memory_growth < 50, f"Memory grew by {memory_growth}MB, expected <50MB"


# Run with: pytest tests/performance/test_api_load.py -v
# Note: Some tests may require psutil: pip install psutil
