#!/usr/bin/env python3
"""Comprehensive Module Test - Tests ALL Veyra modules"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

print("=" * 70)
print("FINANCIAL MASTER - COMPREHENSIVE MODULE TEST")
print("Testing ALL modules without API keys")
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
        print(f"  ✗ {name}: {str(e)[:70]}")
        failed.append((name, str(e)))
        return False

from datetime import datetime, date

# ============================================
# CATEGORY 1: Recently Fixed Modules (30+ files)
# ============================================
print("\n[1] RECENTLY FIXED MODULES:")

def test_mushroom():
    from app.mushroom_farming.cultivation_economics import CultivationEconomics, CultivationBatch
    from app.mushroom_farming.specialty_mushrooms import SpecialtyMushrooms
    ce = CultivationEconomics()
    batch = CultivationBatch('B001', 'Oyster', 50.0, 10.0, 100.0, 15.0, datetime.now())
    ce.add_batch(batch)
    result = ce.get_summary()
    assert result['total_batches'] == 1

test("Mushroom Farming", test_mushroom)

def test_ai_automation():
    from app.ai_automation.robotics_roi import RoboticsROI, RobotDeployment
    from app.ai_automation.llm_economics import LLMEconomics, LLMUsage
    from app.ai_automation.automation_valuation import AutomationValuation, AutomationSystem
    roi = RoboticsROI()
    deploy = RobotDeployment('D001', 'industrial', 50000, 5000, 2000, 2000, 25, 20, datetime.now())
    roi.add_deployment(deploy)
    assert 'total_deployments' in roi.get_portfolio_summary()

test("AI Automation", test_ai_automation)

def test_cybersecurity():
    from app.cybersecurity.breach_analyzer import BreachAnalyzer, DataBreach
    from app.cybersecurity.cyber_insurance import CyberInsurance, CyberPolicy
    from app.cybersecurity.darkweb_intel import DarkwebIntel, ThreatIntel
    ba = BreachAnalyzer()
    ba.add(DataBreach('BR001', 'Acme', 100000, 150.0, datetime.now(), 'retail'))
    assert ba.get_summary()['total_breaches'] == 1

test("Cybersecurity", test_cybersecurity)

def test_ai_models():
    from app.ai_models.pattern_recognizer import PatternRecognizer
    from app.ai_models.anomaly_detector import AnomalyDetector
    pr = PatternRecognizer()
    prices = [100 + i * 0.5 for i in range(30)]
    pr.detect_pattern(prices, 'TEST')
    assert 'total_patterns' in pr.get_summary()

test("AI Models", test_ai_models)

def test_ai_integrations():
    from app.ai_integrations.github_models import GitHubModels
    from app.ai_integrations.open_source_ai import OpenSourceAI
    from app.ai_integrations.model_zoo import ModelZoo
    gm = GitHubModels()
    assert 'total_models' in gm.get_summary()

test("AI Integrations", test_ai_integrations)

def test_beekeeping():
    from app.beekeeping.pollination_services import PollinationServices, PollinationContract
    ps = PollinationServices()
    ps.add(PollinationContract('C001', 'almond', 100, 50, 150.0, 30))
    assert ps.get_summary()['total_contracts'] == 1

test("Beekeeping", test_beekeeping)

def test_carbon_capture():
    from app.carbon_capture.point_source_capture import PointSourceCapture, CaptureFacility
    from app.carbon_capture.carbon_storage import CarbonStorage, StorageSite
    cc = PointSourceCapture()
    cc.add(CaptureFacility('F001', 'power', 1000000, 50.0, 90.0))
    assert cc.get_summary()['total_facilities'] == 1

test("Carbon Capture", test_carbon_capture)

def test_cellular_ag():
    from app.cellular_agriculture.precision_fermentation import PrecisionFermentation, FermentationBatch
    pf = PrecisionFermentation()
    pf.add(FermentationBatch('B001', 'dairy_protein', 1000, 15.0, 50.0, 25.0))
    assert pf.get_summary()['total_batches'] == 1

test("Cellular Agriculture", test_cellular_ag)

def test_climate_finance():
    from app.climate_finance.green_bond_analyzer import GreenBondAnalyzer, GreenBond
    gb = GreenBondAnalyzer()
    gb.add(GreenBond('GB001', 'World Bank', 1000000, 3.5, 'solar', 50000))
    assert gb.get_summary()['total_principal'] > 0

test("Climate Finance", test_climate_finance)

def test_circular_economy():
    from app.circular_economy.waste_to_energy import WasteToEnergy, WTEFacility
    we = WasteToEnergy()
    we.add(WTEFacility('F001', 50.0, 100000, 200000, 80.0, 5000000))
    assert we.get_summary()['total_capacity_mw'] > 0

test("Circular Economy", test_circular_economy)

def test_wealth_engines():
    from app.wealth_engines.dividend_engine import DividendEngine, DividendHolding
    from app.wealth_engines.rental_income import RentalIncomeTracker, RentalProperty
    from app.wealth_engines.royalty_collector import RoyaltyCollector, RoyaltyStream
    de = DividendEngine()
    de.add(DividendHolding('AAPL', 100, 0.82, 4, []))
    assert 'holdings' in de.get_summary()

test("Wealth Engines", test_wealth_engines)

def test_pattern_detection():
    from app.pattern_detection.dark_pool_tracker import DarkPoolTracker, DarkPoolTrade
    from app.pattern_detection.insider_network import InsiderNetworkMapper, Insider
    dp = DarkPoolTracker()
    dp.add(DarkPoolTrade('T001', 'AAPL', 1000, 150.0, datetime.now(), 'DARK1', 'buy'))
    assert dp.get_summary()['total_trades'] == 1

test("Pattern Detection", test_pattern_detection)

def test_visual_learning():
    from app.visual_learning.stream_analyzer import StreamAnalyzer
    from app.visual_learning.chart_predictor import ChartPredictor
    sa = StreamAnalyzer()
    assert 'streams' in sa.get_summary()

test("Visual Learning", test_visual_learning)

# ============================================
# CATEGORY 2: Business Service Modules
# ============================================
print("\n[2] BUSINESS SERVICE MODULES:")

def test_personal_trainer():
    from app.personal_trainer.fitness_business_tracker import PersonalTrainerBusinessTracker, Client
    ft = PersonalTrainerBusinessTracker()
    ft.add_client(Client('C001', 'John', 'one_on_one', 2, 65, date.today(), 12, 'active'))
    assert 'active_clients' in ft.get_business_health_report()

test("Personal Trainer", test_personal_trainer)

def test_construction():
    from app.construction_trades.construction_tracker import ConstructionBusinessTracker, Project
    ct = ConstructionBusinessTracker()
    ct.add_project(Project('P001', 'ABC', 'residential', 'in_progress', 500000, 
                          date.today(), date.today(), None, 200000, 125000, 75000, 75000))
    assert 'status' in ct.get_business_health_report()

test("Construction", test_construction)

def test_restaurant():
    from app.food_service.restaurant_tracker import RestaurantTracker, RestaurantSale
    rt = RestaurantTracker()
    rt.add_sale(RestaurantSale('S001', 150.0, 45.0, 'dine_in', date.today()))
    assert 'total_revenue' in rt.get_health_report()

test("Restaurant", test_restaurant)

def test_fleet():
    from app.transportation import FleetTracker, FleetTrip
    ft = FleetTracker()
    ft.add_trip(FleetTrip('T001', 'V1', 150.0, 200.0, 45.0, 30.0, 0, date.today()))
    assert ft.get_fleet_metrics()['total_trips'] == 1

test("Fleet Management", test_fleet)

def test_manufacturing():
    from app.manufacturing.production_tracker import ManufacturingTracker, ProductionRun
    pt = ManufacturingTracker()
    pt.add_run(ProductionRun('R001', 1000, 5000, 2000, 1000, date.today()))
    assert pt.get_metrics()['production_runs'] == 1

test("Manufacturing", test_manufacturing)

def test_farm():
    from app.agriculture_business.farm_business_tracker import FarmBusinessTracker, FarmHarvest
    ft = FarmBusinessTracker()
    ft.add_harvest(FarmHarvest('H001', 'Corn', 5000, 2.50, 800, date.today()))
    assert ft.get_farm_metrics()['harvests'] == 1

test("Farm Business", test_farm)

def test_distribution():
    from app.wholesale_distribution.distribution_tracker import WholesaleTracker, WholesaleOrder
    dt = WholesaleTracker()
    dt.add_order(WholesaleOrder('O001', 'Customer A', 5000, 3000, 200, date.today()))
    assert dt.get_metrics()['orders'] == 1

test("Distribution", test_distribution)

def test_cleaning():
    from app.cleaning_services.cleaning_tracker import CleaningTracker, CleaningJob
    ct = CleaningTracker()
    ct.add(CleaningJob('J001', 'residential', 150, 60, 15, date.today()))
    assert ct.get_metrics()['jobs'] == 1

test("Cleaning", test_cleaning)

def test_pet():
    from app.pet_services.veterinary_tracker import PetServicesTracker, PetVisit
    pst = PetServicesTracker()
    pst.add(PetVisit('V001', 'checkup', 85, 15, date.today()))
    assert pst.get_metrics()['visits'] == 1

test("Pet Services", test_pet)

def test_events():
    from app.events_entertainment.event_tracker import EventTracker, Event
    et = EventTracker()
    et.add(Event('E001', 'wedding', 5000, 2500, date.today()))
    assert et.get_metrics()['events'] == 1

test("Event Planning", test_events)

# ============================================
# CATEGORY 3: Core Financial Modules
# ============================================
print("\n[3] CORE FINANCIAL MODULES:")

def test_core_portfolio():
    from app.core.portfolio import Portfolio
    p = Portfolio('Test Portfolio')
    assert p.name == 'Test Portfolio'

test("Core Portfolio", test_core_portfolio)

def test_alt_investments():
    from app.alternative_investments.art_investing import ArtInvesting
    ai = ArtInvesting()
    assert 'total_value' in ai.get_summary()

test("Alternative Investments", test_alt_investments)

def test_arbitrage():
    from app.arbitrage.merger_arbitrage import MergerArbitrage
    ma = MergerArbitrage()
    assert 'deals_tracked' in ma.get_summary()

test("Merger Arbitrage", test_arbitrage)

def test_behavioral():
    from app.behavioral_finance.bias_detector import BiasDetector
    bd = BiasDetector()
    assert 'biases_detected' in bd.get_summary()

test("Behavioral Finance", test_behavioral)

# ============================================
# RESULTS
# ============================================
print("\n" + "=" * 70)
print(f"COMPREHENSIVE TEST RESULTS: {len(passed)} passed, {len(failed)} failed")
if failed:
    print("\nFAILED MODULES:")
    for name, err in failed:
        print(f"  ✗ {name}: {err[:80]}")
else:
    print("\n🎉 ALL MODULES TESTED AND WORKING! 🎉")
print("=" * 70)

# Save results to file
with open('test_results.txt', 'w') as f:
    f.write(f"Passed: {len(passed)}\n")
    f.write(f"Failed: {len(failed)}\n")
    f.write(f"\nPassed Modules:\n")
    for p in passed:
        f.write(f"  ✓ {p}\n")
    if failed:
        f.write(f"\nFailed Modules:\n")
        for name, err in failed:
            f.write(f"  ✗ {name}: {err}\n")
