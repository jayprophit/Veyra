#!/usr/bin/env python3
"""Test Runner - Cycle 2: Business & Service Modules"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

print("=" * 70)
print("FINANCIAL MASTER - COMPREHENSIVE TEST CYCLE 2")
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

print("\n[2] BUSINESS SERVICE MODULES:")

# Personal Trainer
def test_personal_trainer():
    from app.personal_trainer.fitness_business_tracker import FitnessTracker, Client
    ft = FitnessTracker()
    client = Client('C001', 'John Doe', 60, 10)
    ft.add_client(client)
    result = ft.get_business_summary()
    assert 'clients' in result

test("Personal Trainer", test_personal_trainer)

# Construction
def test_construction():
    from app.construction_trades.construction_tracker import ConstructionTracker, Project
    ct = ConstructionTracker()
    project = Project('P001', 'House Build', 500000, 350000, '2024-06-01')
    ct.add_project(project)
    result = ct.get_summary()
    assert result['projects'] == 1

test("Construction", test_construction)

# Restaurant
def test_restaurant():
    from app.food_service.restaurant_tracker import RestaurantTracker, DailySales
    rt = RestaurantTracker()
    sales = DailySales(date.today(), 5000, 1500)
    rt.add_sales(sales)
    result = rt.get_health_report()
    assert 'revenue' in result

test("Restaurant", test_restaurant)

# Fleet Management
def test_fleet():
    from app.transportation.fleet_tracker import FleetTracker, Trip
    ft = FleetTracker()
    trip = Trip('T001', 150, 45, 30)
    ft.add_trip(trip)
    result = ft.get_metrics()
    assert result['trips'] == 1

test("Fleet Management", test_fleet)

# Manufacturing
def test_manufacturing():
    from app.manufacturing.production_tracker import ProductionTracker, ProductionRun
    pt = ProductionTracker()
    run = ProductionRun('R001', 'Widget', 1000, 5000, 2000, 1000)
    pt.add_run(run)
    result = pt.get_metrics()
    assert result['runs'] == 1

test("Manufacturing", test_manufacturing)

# Farm Business
def test_farm():
    from app.agriculture_business.farm_business_tracker import FarmTracker, Harvest
    ft = FarmTracker()
    harvest = Harvest('H001', 'Corn', 5000, 2500, 800)
    ft.add_harvest(harvest)
    result = ft.get_metrics()
    assert result['harvests'] == 1

test("Farm Business", test_farm)

# Distribution
def test_distribution():
    from app.wholesale_distribution.distribution_tracker import DistributionTracker, Order
    dt = DistributionTracker()
    order = Order('O001', 5000, 3000, 200, 0.3)
    dt.add_order(order)
    result = dt.get_metrics()
    assert result['orders'] == 1

test("Distribution", test_distribution)

# Cleaning Services
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
print(f"CYCLE 2 RESULTS: {len(passed)} passed, {len(failed)} failed")
if failed:
    print("\nFailed tests:")
    for name, err in failed:
        print(f"  - {name}: {err}")
print("=" * 70)
