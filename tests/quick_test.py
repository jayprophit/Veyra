#!/usr/bin/env python3
"""Quick test of Financial Master modules - No API keys"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

print("=" * 60)
print("FINANCIAL MASTER - QUICK TEST SUITE")
print("=" * 60)

passed = 0
failed = 0
errors = []

def test(name, func):
    global passed, failed
    try:
        func()
        print(f"✓ {name}")
        passed += 1
        return True
    except Exception as e:
        print(f"✗ {name}: {e}")
        failed += 1
        errors.append((name, str(e)))
        return False

# Test 1: Database Layer
def test_database():
    from app.database_layer import DatabaseManager, DatabaseConfig
    config = DatabaseConfig()
    config.sqlite_path = ":memory:"
    db = DatabaseManager(config)
    assert db.conn is not None

test("Database Layer", test_database)

# Test 2: Mushroom Farming
def test_mushroom():
    from app.mushroom_farming.cultivation_economics import CultivationEconomics, CultivationBatch
    from datetime import datetime
    ce = CultivationEconomics()
    batch = CultivationBatch('B001', 'Oyster', 50.0, 10.0, 100.0, 15.0, datetime.now())
    ce.add_batch(batch)
    result = ce.get_summary()
    assert result['total_batches'] == 1

test("Mushroom Farming", test_mushroom)

# Test 3: AI Automation
def test_ai_automation():
    from app.ai_automation.robotics_roi import RoboticsROI, RobotDeployment
    from datetime import datetime
    roi = RoboticsROI()
    deploy = RobotDeployment('D001', 'industrial', 50000, 5000, 2000, 2000, 25, 20, datetime.now())
    roi.add_deployment(deploy)
    result = roi.get_portfolio_summary()
    assert 'total_deployments' in result

test("AI Automation", test_ai_automation)

# Test 4: Cybersecurity
def test_cybersecurity():
    from app.cybersecurity.breach_analyzer import BreachAnalyzer, DataBreach
    from datetime import datetime
    ba = BreachAnalyzer()
    breach = DataBreach('BR001', 'Acme Corp', 100000, 150.0, datetime.now(), 'retail')
    ba.add(breach)
    result = ba.get_summary()
    assert result['total_breaches'] == 1

test("Cybersecurity", test_cybersecurity)

# Test 5: Pattern Detection
def test_pattern_detection():
    from app.pattern_detection.dark_pool_tracker import DarkPoolTracker, DarkPoolTrade
    from datetime import datetime
    dp = DarkPoolTracker()
    trade = DarkPoolTrade('T001', 'AAPL', 1000, 150.0, datetime.now(), 'DARK1', 'buy')
    dp.add(trade)
    result = dp.get_summary()
    assert result['total_trades'] == 1

test("Pattern Detection", test_pattern_detection)

# Test 6: Wealth Engines
def test_wealth_engines():
    from app.wealth_engines.dividend_engine import DividendEngine, DividendHolding
    de = DividendEngine()
    holding = DividendHolding('AAPL', 100, 0.82, 4, [])
    de.add(holding)
    result = de.get_summary()
    assert 'holdings' in result

test("Wealth Engines", test_wealth_engines)

# Test 7: AI Models
def test_ai_models():
    from app.ai_models.pattern_recognizer import PatternRecognizer
    pr = PatternRecognizer()
    prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 110, 112, 111, 113, 115, 114]
    patterns = pr.detect_pattern(prices, 'TEST')
    result = pr.get_summary()
    assert 'total_patterns' in result

test("AI Models", test_ai_models)

# Test 8: Carbon Capture
def test_carbon_capture():
    from app.carbon_capture.point_source_capture import PointSourceCapture, CaptureFacility
    cc = PointSourceCapture()
    facility = CaptureFacility('F001', 'power_plant', 1000000, 50.0, 90.0)
    cc.add(facility)
    result = cc.get_summary()
    assert result['total_facilities'] == 1

test("Carbon Capture", test_carbon_capture)

# Test 9: Circular Economy
def test_circular_economy():
    from app.circular_economy.waste_to_energy import WasteToEnergy, WTEFacility
    we = WasteToEnergy()
    facility = WTEFacility('F001', 50.0, 100000, 200000, 80.0, 5000000)
    we.add(facility)
    result = we.get_summary()
    assert result['total_capacity_mw'] > 0

test("Circular Economy", test_circular_economy)

# Test 10: Climate Finance
def test_climate_finance():
    from app.climate_finance.green_bond_analyzer import GreenBondAnalyzer, GreenBond
    gb = GreenBondAnalyzer()
    bond = GreenBond('GB001', 'World Bank', 1000000, 3.5, 'solar_projects', 50000)
    gb.add(bond)
    result = gb.get_summary()
    assert result['total_principal'] > 0

test("Climate Finance", test_climate_finance)

print("=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
if errors:
    print("\nERRORS:")
    for name, err in errors:
        print(f"  - {name}: {err}")
print("=" * 60)
