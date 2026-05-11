#!/usr/bin/env python3
"""Complete Module Test - ALL Veyra modules"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

print("=" * 70)
print("FINANCIAL MASTER - COMPLETE MODULE VERIFICATION")
print("=" * 70)

passed = []
failed = []

def test(name, test_func):
    try:
        test_func()
        print(f"  [OK] {name}")
        passed.append(name)
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {str(e)[:70]}")
        failed.append((name, str(e)))
        return False

from datetime import datetime, date

# Test ALL modules
print("\n[1] RECENTLY FIXED MODULES:")

test("Mushroom Farming", lambda: __import__('app.mushroom_farming.cultivation_economics', fromlist=['CultivationEconomics']))
test("AI Automation", lambda: __import__('app.ai_automation.robotics_roi', fromlist=['RoboticsROI']))
test("Cybersecurity", lambda: __import__('app.cybersecurity.breach_analyzer', fromlist=['BreachAnalyzer']))
test("AI Models", lambda: __import__('app.ai_models.pattern_recognizer', fromlist=['PatternRecognizer']))
test("AI Integrations", lambda: __import__('app.ai_integrations.github_models', fromlist=['GitHubModels']))
test("Beekeeping", lambda: __import__('app.beekeeping.pollination_services', fromlist=['PollinationServices']))
test("Carbon Capture", lambda: __import__('app.carbon_capture.point_source_capture', fromlist=['PointSourceCapture']))
test("Cellular Agriculture", lambda: __import__('app.cellular_agriculture.precision_fermentation', fromlist=['PrecisionFermentation']))
test("Climate Finance", lambda: __import__('app.climate_finance.green_bond_analyzer', fromlist=['GreenBondAnalyzer']))
test("Circular Economy", lambda: __import__('app.circular_economy.waste_to_energy', fromlist=['WasteToEnergy']))
test("Wealth Engines", lambda: __import__('app.wealth_engines.dividend_engine', fromlist=['DividendEngine']))
test("Pattern Detection", lambda: __import__('app.pattern_detection.dark_pool_tracker', fromlist=['DarkPoolTracker']))
test("Visual Learning", lambda: __import__('app.visual_learning.stream_analyzer', fromlist=['StreamAnalyzer']))

print("\n[2] BUSINESS SERVICE MODULES:")

test("Personal Trainer", lambda: __import__('app.personal_trainer.fitness_business_tracker', fromlist=['PersonalTrainerBusinessTracker']))
test("Construction", lambda: __import__('app.construction_trades.construction_tracker', fromlist=['ConstructionBusinessTracker']))
test("Restaurant", lambda: __import__('app.food_service.restaurant_tracker', fromlist=['RestaurantTracker']))
test("Fleet Management", lambda: __import__('app.transportation.fleet_tracker', fromlist=['FleetTracker']))
test("Manufacturing", lambda: __import__('app.manufacturing.production_tracker', fromlist=['ManufacturingTracker']))
test("Farm Business", lambda: __import__('app.agriculture_business.farm_business_tracker', fromlist=['FarmBusinessTracker']))
test("Distribution", lambda: __import__('app.wholesale_distribution.distribution_tracker', fromlist=['WholesaleTracker']))
test("Cleaning", lambda: __import__('app.cleaning_services.cleaning_tracker', fromlist=['CleaningTracker']))
test("Pet Services", lambda: __import__('app.pet_services.veterinary_tracker', fromlist=['PetServicesTracker']))
test("Event Planning", lambda: __import__('app.events_entertainment.event_tracker', fromlist=['EventTracker']))

print("\n[3] CORE FINANCIAL MODULES:")

test("Core Portfolio", lambda: __import__('app.core.portfolio', fromlist=['Portfolio']))
test("Alternative Investments", lambda: __import__('app.alternative_investments.commodity_tracker', fromlist=['CommodityTracker']))
test("Merger Arbitrage", lambda: __import__('app.arbitrage.merger_arbitrage', fromlist=['MergerArbitrage']))
test("Behavioral Finance", lambda: __import__('app.behavioral_finance.bias_detector', fromlist=['CognitiveBiasDetector']))

# Results
print("\n" + "=" * 70)
print(f"RESULTS: {len(passed)} passed, {len(failed)} failed")
if failed:
    print("\nFAILED:")
    for name, err in failed:
        print(f"  - {name}")
else:
    print("\n*** ALL MODULES VERIFIED SUCCESSFULLY! ***")
print("=" * 70)
