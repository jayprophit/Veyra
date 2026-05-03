#!/usr/bin/env python3
"""Test Runner - Comprehensive module testing without API keys"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

print("=" * 70)
print("FINANCIAL MASTER - COMPREHENSIVE TEST CYCLE 1")
print("=" * 70)

passed = []
failed = []

def test(name, module_path, test_func):
    try:
        test_func()
        print(f"  ✓ {name}")
        passed.append(name)
        return True
    except Exception as e:
        print(f"  ✗ {name}: {str(e)[:60]}")
        failed.append((name, str(e)))
        return False

# Test Batch 1: Recently Fixed Modules
print("\n[1] RECENTLY FIXED MODULES:")

from datetime import datetime, date

# Mushroom Farming
def test_mushroom():
    from app.mushroom_farming.cultivation_economics import CultivationEconomics, CultivationBatch
    ce = CultivationEconomics()
    batch = CultivationBatch('B001', 'Oyster', 50.0, 10.0, 100.0, 15.0, datetime.now())
    ce.add_batch(batch)
    result = ce.get_summary()
    assert result['total_batches'] == 1

test("Mushroom Cultivation", "app.mushroom_farming", test_mushroom)

# AI Automation
def test_ai_auto():
    from app.ai_automation.robotics_roi import RoboticsROI, RobotDeployment
    roi = RoboticsROI()
    deploy = RobotDeployment('D001', 'industrial', 50000, 5000, 2000, 2000, 25, 20, datetime.now())
    roi.add_deployment(deploy)
    result = roi.get_portfolio_summary()
    assert 'total_deployments' in result

test("AI Robotics ROI", "app.ai_automation", test_ai_auto)

# Cybersecurity
def test_cyber():
    from app.cybersecurity.breach_analyzer import BreachAnalyzer, DataBreach
    ba = BreachAnalyzer()
    breach = DataBreach('BR001', 'Acme Corp', 100000, 150.0, datetime.now(), 'retail')
    ba.add(breach)
    result = ba.get_summary()
    assert result['total_breaches'] == 1

test("Breach Analyzer", "app.cybersecurity", test_cyber)

# Pattern Detection
def test_pattern():
    from app.pattern_detection.dark_pool_tracker import DarkPoolTracker, DarkPoolTrade
    dp = DarkPoolTracker()
    trade = DarkPoolTrade('T001', 'AAPL', 1000, 150.0, datetime.now(), 'DARK1', 'buy')
    dp.add(trade)
    result = dp.get_summary()
    assert result['total_trades'] == 1

test("Dark Pool Tracker", "app.pattern_detection", test_pattern)

# Wealth Engines
def test_wealth():
    from app.wealth_engines.dividend_engine import DividendEngine, DividendHolding
    de = DividendEngine()
    holding = DividendHolding('AAPL', 100, 0.82, 4, [])
    de.add(holding)
    result = de.get_summary()
    assert 'holdings' in result

test("Dividend Engine", "app.wealth_engines", test_wealth)

print("\n" + "=" * 70)
print(f"CYCLE 1 RESULTS: {len(passed)} passed, {len(failed)} failed")
if failed:
    print("\nFailed tests:")
    for name, err in failed:
        print(f"  - {name}: {err}")
print("=" * 70)
