#!/usr/bin/env python3
"""
Fuel & Mileage Tracker Demo
============================
Quick demo of the FinOS fuel tracker integration.

Usage:
    python fuel_demo.py --add-vehicle
    python fuel_demo.py --log-trip
    python fuel_demo.py --summary 2026-27
    python fuel_demo.py --fuel-up
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_layer import DatabaseManager
from datetime import date, datetime


def demo_add_vehicle(db: DatabaseManager, user_id: str = "demo_user"):
    """Add a demo vehicle."""
    print("\n🚗 Adding vehicle...")
    
    vehicle_id = db.add_vehicle(
        user_id=user_id,
        make="Ford",
        model="Focus",
        registration="AB66 XYZ",
        fuel_type="petrol",
        engine_size_cc=999,
        year=2016
    )
    
    print(f"✅ Vehicle added (ID: {vehicle_id})")
    
    # List vehicles
    vehicles = db.get_vehicles(user_id)
    print(f"\n📋 Your vehicles ({len(vehicles)} total):")
    for v in vehicles:
        print(f"  • {v['make']} {v['model']} ({v['registration']})")
    
    return vehicle_id


def demo_log_trip(db: DatabaseManager, vehicle_id: int, user_id: str = "demo_user"):
    """Log a demo business trip."""
    print("\n🛣️  Logging business trip...")
    
    # Simulate a 50-mile business trip
    distance = 50.0
    
    # Calculate HMRC claim (45p/mile for first 10k)
    claimable = distance * 0.45
    
    trip_id = db.log_mileage(
        user_id=user_id,
        trip_date=date.today().isoformat(),
        start="Home Office",
        end="Client Site - Manchester",
        distance=distance,
        purpose="Client meeting and site survey",
        vehicle_id=vehicle_id,
        start_postcode="SW1A 1AA",
        end_postcode="M1 1AA",
        amount_claimable=claimable,
        passenger_allowance=0,
        notes="Return journey same day"
    )
    
    print(f"✅ Trip logged (ID: {trip_id})")
    print(f"   Distance: {distance} miles")
    print(f"   Claimable: £{claimable:.2f}")
    print(f"   Rate: 45p/mile")


def demo_fuel_up(db: DatabaseManager, vehicle_id: int, user_id: str = "demo_user"):
    """Log a demo fuel purchase."""
    print("\n⛽ Logging fuel purchase...")
    
    purchase_id = db.log_fuel_purchase(
        user_id=user_id,
        vehicle_id=vehicle_id,
        purchase_date=date.today().isoformat(),
        odometer=45000,
        litres=35.5,
        price_per_litre=1.45,
        total_cost=51.48,
        fuel_type="petrol",
        is_full_tank=True,
        station="Shell Manchester"
    )
    
    print(f"✅ Fuel purchase logged (ID: {purchase_id})")
    print(f"   Litres: 35.5L")
    print(f"   Cost: £51.48")
    print(f"   Price/L: £1.45")


def demo_summary(db: DatabaseManager, tax_year: str, user_id: str = "demo_user"):
    """Show HMRC mileage summary."""
    print(f"\n📊 HMRC Mileage Summary - Tax Year {tax_year}")
    print("=" * 50)
    
    summary = db.get_mileage_summary(user_id, tax_year)
    
    print(f"Total trips: {summary['total_trips']}")
    print(f"Business miles: {summary['total_business_miles']:.1f}")
    print(f"  @ 45p/mile: {summary['miles_at_45p']:.1f} miles")
    print(f"  @ 25p/mile: {summary['miles_at_25p']:.1f} miles")
    print(f"\n💰 Amount claimable:")
    print(f"   Mileage: £{summary['total_claimable']:.2f}")
    print(f"   Passengers: £{summary['total_passenger_allowance']:.2f}")
    print(f"   TOTAL: £{summary['total_claimable'] + summary['total_passenger_allowance']:.2f}")
    print(f"\n📈 Progress: {summary['ytd_progress_pct']:.1f}% of 10,000 mile threshold")


def demo_subscriptions(db: DatabaseManager, user_id: str = "demo_user"):
    """Show subscription tracking demo."""
    print("\n💳 Subscription Tracking Demo")
    print("=" * 50)
    
    # Add some subscriptions
    subs = [
        ("Netflix", "Netflix Inc", 15.99, "entertainment"),
        ("Spotify", "Spotify", 10.99, "entertainment"),
        ("ChatGPT Plus", "OpenAI", 20.00, "software"),
        ("Adobe CC", "Adobe", 56.00, "software"),
    ]
    
    for name, provider, cost, category in subs:
        db.add_subscription(user_id, name, provider, cost, category=category)
    
    # Get summary
    subscriptions = db.get_subscriptions(user_id)
    total = db.get_monthly_subscriptions_cost(user_id)
    
    print(f"\n📋 Active subscriptions ({len(subscriptions)}):")
    for s in subscriptions:
        print(f"  • {s['name']}: £{s['cost_monthly']:.2f}/month ({s['category']})")
    
    print(f"\n💸 Total monthly cost: £{total:.2f}")
    print(f"   Yearly cost: £{total * 12:.2f}")


def main():
    print("=" * 60)
    print("🏦 Veyra - Fuel & Mileage Tracker Demo")
    print("      (FinOS Integration)")
    print("=" * 60)
    
    # Initialize database
    db = DatabaseManager()
    user_id = "demo_user"
    
    # Run all demos
    vehicle_id = demo_add_vehicle(db, user_id)
    demo_log_trip(db, vehicle_id, user_id)
    demo_fuel_up(db, vehicle_id, user_id)
    demo_summary(db, "2026-27", user_id)
    demo_subscriptions(db, user_id)
    
    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("=" * 60)
    print("\nYour database now contains:")
    print("  • 1 vehicle")
    print("  • 1 business trip")
    print("  • 1 fuel purchase")
    print("  • 4 subscriptions")
    print("\nUse the API to query this data:")
    print("  GET /api/fuel/vehicles?user_id=demo_user")
    print("  GET /api/fuel/mileage?user_id=demo_user")
    print("  GET /api/fuel/summary/2026-27?user_id=demo_user")


if __name__ == "__main__":
    main()
