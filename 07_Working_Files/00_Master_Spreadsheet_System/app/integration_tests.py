"""Integration Tests - Automated testing of all components."""

import unittest
import requests
import sqlite3
import asyncio
from datetime import datetime

class TestDatabase(unittest.TestCase):
    """Test database operations."""
    
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        from database_layer import DatabaseManager, DatabaseConfig
        self.db = DatabaseManager(DatabaseConfig(sqlite_path=':memory:'))
    
    def test_add_holding(self):
        self.db.add_holding("AAPL", 100, 150.0, "ISA")
        holdings = self.db.get_holdings()
        self.assertEqual(len(holdings), 1)
        self.assertEqual(holdings[0]['ticker'], "AAPL")
    
    def test_portfolio_value(self):
        self.db.add_holding("VUAG", 100, 85.0, "ISA")
        self.db.add_holding("AGGH", 50, 92.0, "GIA")
        self.db.update_price("VUAG", 90.0)
        self.db.update_price("AGGH", 91.0)
        
        summary = self.db.get_portfolio_value()
        self.assertGreater(summary['total'], 0)

class TestAPI(unittest.TestCase):
    """Test API endpoints (requires server running)."""
    
    BASE_URL = "http://localhost:8000"
    
    def test_health(self):
        try:
            r = requests.get(f"{self.BASE_URL}/api/health", timeout=5)
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()['status'], 'healthy')
        except requests.ConnectionError:
            self.skipTest("API server not running")
    
    def test_portfolio_summary(self):
        try:
            r = requests.get(f"{self.BASE_URL}/api/portfolio/summary", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.assertIn('total_value', data)
        except requests.ConnectionError:
            self.skipTest("API server not running")

class TestOllama(unittest.TestCase):
    """Test Ollama connection."""
    
    def test_connection(self):
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=5)
            self.assertEqual(r.status_code, 200)
        except requests.ConnectionError:
            self.skipTest("Ollama not running")

class TestComponents(unittest.TestCase):
    """Test individual components."""
    
    def test_tax_harvester(self):
        from tax_loss_harvesting import TaxLossHarvester
        conn = sqlite3.connect(':memory:')
        harvester = TaxLossHarvester(conn)
        # Should not crash even with empty DB
        opps = harvester.find_opportunities()
        self.assertIsInstance(opps, list)
    
    def test_retirement_planner(self):
        from retirement_monte_carlo import RetirementPlanner, RetirementScenario
        planner = RetirementPlanner()
        scenario = RetirementScenario(
            current_age=35, retirement_age=60,
            current_savings=200000, monthly_contribution=1500
        )
        result = planner.run_monte_carlo(scenario, num_simulations=100)
        self.assertGreaterEqual(result.success_rate, 0)
        self.assertLessEqual(result.success_rate, 1)

class TestAutomation(unittest.TestCase):
    """Test automation components."""
    
    def test_ollama_manager(self):
        from automation_controller import OllamaManager
        mgr = OllamaManager()
        self.assertIsInstance(mgr.available, list)
    
    def test_data_scraper(self):
        from data_scraper import Trading212Importer
        importer = Trading212Importer()
        # Test with minimal data
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Action,Time,Ticker,No. of shares,Price / share,Total (GBP)\n")
            f.write("Market buy,2024-01-01 10:00:00,AAPL,10,150.00,1500.00\n")
            temp_path = f.name
        
        try:
            result = importer.parse(temp_path)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['ticker'], 'AAPL')
        finally:
            os.unlink(temp_path)

def run_all_tests():
    """Run all integration tests."""
    print("="*60)
    print("Financial Master - Integration Tests")
    print("="*60)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestOllama))
    suite.addTests(loader.loadTestsFromTestCase(TestComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestAutomation))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
    print("="*60)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_all_tests()
