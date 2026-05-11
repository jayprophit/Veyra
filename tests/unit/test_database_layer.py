"""
Unit Tests - Database Layer
===========================
Comprehensive tests for all database operations.
"""

import pytest
import sqlite3
from datetime import datetime, date
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))

from database_layer import DatabaseManager


class TestDatabaseManager:
    """Test suite for DatabaseManager."""
    
    @pytest.fixture
    def db(self):
        """Create a fresh database instance for each test."""
        # Use in-memory database for testing
        manager = DatabaseManager()
        manager.db_path = ':memory:'
        manager.conn = sqlite3.connect(':memory:', check_same_thread=False)
        manager.conn.row_factory = sqlite3.Row
        manager._init_db()
        yield manager
        manager.conn.close()
    
    def test_initialization(self, db):
        """Test database initializes correctly."""
        assert db.conn is not None
        
        # Check tables exist
        cursor = db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'portfolio' in tables
        assert 'tax_events' in tables
        assert 'fuel_log' in tables
    
    def test_add_holding(self, db):
        """Test adding a new holding."""
        db.add_holding('AAPL', 'Apple Inc.', 10, 150.0, 'USD')
        
        holdings = db.get_holdings()
        assert len(holdings) == 1
        assert holdings[0]['symbol'] == 'AAPL'
        assert holdings[0]['shares'] == 10
    
    def test_update_holding(self, db):
        """Test updating an existing holding."""
        db.add_holding('MSFT', 'Microsoft', 5, 200.0)
        db.update_holding('MSFT', shares=15)
        
        holdings = db.get_holdings()
        msft = next(h for h in holdings if h['symbol'] == 'MSFT')
        assert msft['shares'] == 15
    
    def test_delete_holding(self, db):
        """Test deleting a holding."""
        db.add_holding('TSLA', 'Tesla', 3, 300.0)
        db.delete_holding('TSLA')
        
        holdings = db.get_holdings()
        assert len(holdings) == 0
    
    def test_add_fuel_purchase(self, db):
        """Test logging fuel purchase."""
        db.add_fuel_purchase(
            vehicle_id=1,
            date='2024-06-15',
            distance=100.5,
            amount=50.0,
            purpose='Business travel'
        )
        
        fuel_logs = db.get_fuel_logs(vehicle_id=1)
        assert len(fuel_logs) == 1
        assert fuel_logs[0]['distance'] == 100.5
    
    def test_calculate_hmrc_mileage(self, db):
        """Test HMRC mileage calculation."""
        # Add some mileage data
        db.add_fuel_purchase(1, '2024-01-15', 10000, 5000.0, 'Business')
        db.add_fuel_purchase(1, '2024-06-15', 15000, 5000.0, 'Business')
        
        result = db.calculate_hmrc_mileage(1, 2024)
        
        # First 10,000 miles at 45p, rest at 25p
        assert result['claimable_miles'] == 5000
        assert result['claimable_amount'] == 5000 * 0.45  # All at 45p
    
    def test_add_tax_event(self, db):
        """Test adding international tax event."""
        db.add_tax_event(
            user_id='user_123',
            event_type='SALE',
            symbol='AAPL',
            quantity=10,
            proceeds=1850.0,
            cost_basis=1500.0,
            date='2024-06-15',
            jurisdiction='UK'
        )
        
        events = db.get_tax_events(user_id='user_123')
        assert len(events) == 1
        assert events[0]['symbol'] == 'AAPL'
        assert events[0]['gain_loss'] == 350.0  # 1850 - 1500
    
    def test_save_exchange_rate(self, db):
        """Test saving and retrieving exchange rates."""
        db.save_exchange_rate('USD', 'GBP', 0.79, '2024-06-15')
        
        rate = db.get_exchange_rate('USD', 'GBP', '2024-06-15')
        assert rate == 0.79
    
    def test_concurrent_access(self, db):
        """Test thread safety of database operations."""
        import threading
        
        results = []
        
        def add_holding():
            try:
                db.add_holding('GOOGL', 'Google', 2, 2500.0)
                results.append('success')
            except Exception as e:
                results.append(f'error: {e}')
        
        # Run multiple threads
        threads = [threading.Thread(target=add_holding) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should succeed (SQLite handles concurrency)
        assert all('success' in r for r in results)
    
    def test_get_portfolio_summary(self, db):
        """Test portfolio summary calculation."""
        db.add_holding('AAPL', 'Apple', 10, 150.0, 'USD')
        db.add_holding('MSFT', 'Microsoft', 5, 200.0, 'USD')
        
        summary = db.get_portfolio_summary()
        
        assert summary['total_holdings'] == 2
        assert summary['total_cost_basis'] == 2500.0  # (10*150) + (5*200)
    
    def test_error_handling(self, db):
        """Test database error handling."""
        # Try invalid operation
        with pytest.raises(Exception):
            db.conn.execute("INVALID SQL SYNTAX")
    
    def test_backup_restore(self, db):
        """Test database backup functionality."""
        # Add data
        db.add_holding('AAPL', 'Apple', 10, 150.0)
        
        # Create backup
        backup_path = db.backup_database()
        assert os.path.exists(backup_path)
        
        # Clean up
        os.remove(backup_path)


class TestDatabasePerformance:
    """Performance tests for database operations."""
    
    @pytest.fixture
    def db(self):
        manager = DatabaseManager()
        manager.db_path = ':memory:'
        manager.conn = sqlite3.connect(':memory:', check_same_thread=False)
        manager.conn.row_factory = sqlite3.Row
        manager._init_db()
        return manager
    
    def test_bulk_insert_performance(self, db):
        """Test performance of bulk inserts."""
        import time
        
        start = time.time()
        
        # Insert 1000 records
        for i in range(1000):
            db.add_holding(f'STOCK{i}', f'Company {i}', 10, 100.0)
        
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0
        
        holdings = db.get_holdings()
        assert len(holdings) == 1000
    
    def test_query_performance(self, db):
        """Test query performance with large dataset."""
        # Populate database
        for i in range(10000):
            db.add_holding(f'STOCK{i}', f'Company {i}', 10, 100.0)
        
        start = time.time()
        
        # Query should be fast with index
        result = db.get_holdings()
        
        elapsed = time.time() - start
        
        # Query 10k records should be < 1 second
        assert elapsed < 1.0
        assert len(result) == 10000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
