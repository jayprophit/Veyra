#!/usr/bin/env python3
"""Final Verification Test - All Fixed Modules"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

print("=" * 70)
print("VEYRA - FINAL VERIFICATION")
print("=" * 70)

passed = []
failed = []

def test(name, test_func):
    try:
        test_func()
        print(f"  ✓ {name}")
        passed.append(name)
        return True
    except Exception as e:
        print(f"  ✗ {name}: {str(e)[:60]}")
        failed.append((name, str(e)))
        return False

from datetime import datetime, date

print("\n[1] RECENTLY FIXED MODULES:")

# Mushroom Farming
def test_mushroom():
    from app.mushroom_farming.cultivation_economics import CultivationEconomics, CultivationBatch
    ce = CultivationEconomics()
    batch = CultivationBatch('B001', 'Oyster', 50.0, 10.0, 100.0, 15.0, datetime.now())
    ce.add_batch(batch)
    result = ce.get_summary()
    assert result['total_batches'] == 1

test("Mushroom Farming", test_mushroom)

# AI Automation
def test_ai_auto():
    from app.ai_automation.robotics_roi import RoboticsROI, RobotDeployment
    roi = RoboticsROI()
    deploy = RobotDeployment('D001', 'industrial', 50000, 5000, 2000, 2000, 25, 20, datetime.now())
    roi.add_deployment(deploy)
    result = roi.get_portfolio_summary()
    assert 'total_deployments' in result

test("AI Automation", test_ai_auto)

# Cybersecurity
def test_cyber():
    from app.cybersecurity.breach_analyzer import BreachAnalyzer, DataBreach
    ba = BreachAnalyzer()
    breach = DataBreach('BR001', 'Acme Corp', 100000, 150.0, datetime.now(), 'retail')
    ba.add(breach)
    result = ba.get_summary()
    assert result['total_breaches'] == 1

test("Cybersecurity", test_cyber)

# Pattern Detection
def test_pattern():
    from app.pattern_detection.dark_pool_tracker import DarkPoolTracker, DarkPoolTrade
    dp = DarkPoolTracker()
    trade = DarkPoolTrade('T001', 'AAPL', 1000, 150.0, datetime.now(), 'DARK1', 'buy')
    dp.add(trade)
    result = dp.get_summary()
    assert result['total_trades'] == 1

test("Pattern Detection", test_pattern)

# Wealth Engines
def test_wealth():
    from app.wealth_engines.dividend_engine import DividendEngine, DividendHolding
    de = DividendEngine()
    holding = DividendHolding('AAPL', 100, 0.82, 4, [])
    de.add(holding)
    result = de.get_summary()
    assert 'holdings' in result

test("Wealth Engines", test_wealth)

print("\n[2] BUSINESS MODULES:")

# Personal Trainer
def test_personal_trainer():
    from app.personal_trainer.fitness_business_tracker import PersonalTrainerBusinessTracker, Client
    ft = PersonalTrainerBusinessTracker()
    client = Client('C001', 'John Doe', 'one_on_one', 2, 65, date.today(), 12, 'active')
    ft.add_client(client)
    result = ft.get_business_health_report()
    assert 'active_clients' in result

test("Personal Trainer", test_personal_trainer)

# Construction
def test_construction():
    from app.construction_trades.construction_tracker import ConstructionBusinessTracker, Project
    ct = ConstructionBusinessTracker()
    project = Project('P001', 'ABC Corp', 'residential', 'in_progress', 500000, 
                    date.today(), date.today(), None, 200000, 125000, 75000, 75000)
    ct.add_project(project)
    result = ct.get_business_health_report()
    assert 'status' in result

test("Construction", test_construction)

# Restaurant
def test_restaurant():
    from app.food_service.restaurant_tracker import RestaurantTracker, RestaurantSale
    rt = RestaurantTracker()
    sale = RestaurantSale('S001', 150.0, 45.0, 'dine_in', date.today())
    rt.add_sale(sale)
    result = rt.get_health_report()
    assert 'total_revenue' in result

test("Restaurant", test_restaurant)

# Fleet - FIXED
def test_fleet():
    from app.transportation import FleetTracker, FleetTrip
    ft = FleetTracker()
    trip = FleetTrip('T001', 'V1', 150.0, 200.0, 45.0, 30.0, 0, date.today())
    ft.add_trip(trip)
    result = ft.get_fleet_metrics()
    assert result['total_trips'] == 1

test("Fleet Management", test_fleet)

# Manufacturing
def test_manufacturing():
    from app.manufacturing.production_tracker import ManufacturingTracker, ProductionRun
    pt = ManufacturingTracker()
    run = ProductionRun('R001', 1000, 5000, 2000, 1000, date.today())
    pt.add_run(run)
    result = pt.get_metrics()
    assert result['production_runs'] == 1

test("Manufacturing", test_manufacturing)

# Farm Business
def test_farm():
    from app.agriculture_business.farm_business_tracker import FarmBusinessTracker, FarmHarvest
    ft = FarmBusinessTracker()
    harvest = FarmHarvest('H001', 'Corn', 5000, 2.50, 800, date.today())
    ft.add_harvest(harvest)
    result = ft.get_farm_metrics()
    assert result['harvests'] == 1

test("Farm Business", test_farm)

# Distribution
def test_distribution():
    from app.wholesale_distribution.distribution_tracker import WholesaleTracker, WholesaleOrder
    dt = WholesaleTracker()
    order = WholesaleOrder('O001', 'Customer A', 5000, 3000, 200, date.today())
    dt.add_order(order)
    result = dt.get_metrics()
    assert result['orders'] == 1

test("Distribution", test_distribution)

# Cleaning
def test_cleaning():
    from app.cleaning_services.cleaning_tracker import CleaningTracker, CleaningJob
    ct = CleaningTracker()
    job = CleaningJob('J001', 'residential', 150, 60, 15, date.today())
    ct.add(job)
    result = ct.get_metrics()
    assert result['jobs'] == 1

test("Cleaning Services", test_cleaning)

# Pet Services
def test_pet():
    from app.pet_services.veterinary_tracker import PetServicesTracker, PetVisit
    pst = PetServicesTracker()
    visit = PetVisit('V001', 'checkup', 85, 15, date.today())
    pst.add(visit)
    result = pst.get_metrics()
    assert result['visits'] == 1

test("Pet Services", test_pet)

# Events
def test_events():
    from app.events_entertainment.event_tracker import EventTracker, Event
    et = EventTracker()
    event = Event('E001', 'wedding', 5000, 2500, date.today())
    et.add(event)
    result = et.get_metrics()
    assert result['events'] == 1

test("Event Planning", test_events)

print("\n" + "=" * 70)
print(f"FINAL RESULTS: {len(passed)} passed, {len(failed)} failed")
if failed:
    print("\nFailed:")
    for name, err in failed:
        print(f"  - {name}")
else:
    print("\n🎉 ALL TESTS PASSED! 🎉")
print("=" * 70)
