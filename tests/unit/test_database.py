"""
Unit Tests: Database Layer
===========================
Test all DatabaseManager methods.
"""

import pytest
from datetime import date, datetime


class TestVehicles:
    """Test vehicle management."""
    
    def test_add_vehicle(self, db, test_user_id, sample_vehicle_data):
        """Test adding a vehicle."""
        vid = db.add_vehicle(
            user_id=test_user_id,
            make=sample_vehicle_data["make"],
            model=sample_vehicle_data["model"],
            **{k: v for k, v in sample_vehicle_data.items() if k not in ["make", "model"]}
        )
        
        assert vid is not None
        assert isinstance(vid, int)
        assert vid > 0
    
    def test_get_vehicles_empty(self, db, test_user_id):
        """Test getting vehicles when none exist."""
        vehicles = db.get_vehicles(test_user_id)
        assert vehicles == []
    
    def test_get_vehicles_with_data(self, db, test_user_id, sample_vehicle_data):
        """Test getting vehicles after adding some."""
        # Add vehicle
        db.add_vehicle(
            test_user_id,
            sample_vehicle_data["make"],
            sample_vehicle_data["model"],
            **{k: v for k, v in sample_vehicle_data.items() if k not in ["make", "model"]}
        )
        
        vehicles = db.get_vehicles(test_user_id)
        assert len(vehicles) == 1
        assert vehicles[0]["make"] == "Ford"
        assert vehicles[0]["model"] == "Focus"
    
    def test_vehicle_fields(self, db, test_user_id, sample_vehicle_data):
        """Test all vehicle fields are stored correctly."""
        db.add_vehicle(
            test_user_id,
            sample_vehicle_data["make"],
            sample_vehicle_data["model"],
            **{k: v for k, v in sample_vehicle_data.items() if k not in ["make", "model"]}
        )
        
        vehicles = db.get_vehicles(test_user_id)
        vehicle = vehicles[0]
        
        assert vehicle["registration"] == "AB66 XYZ"
        assert vehicle["fuel_type"] == "petrol"
        assert vehicle["engine_size_cc"] == 999
        assert vehicle["year"] == 2016
        assert vehicle["is_active"] == 1


class TestMileage:
    """Test mileage logging."""
    
    def test_log_mileage(self, db, test_user_id, sample_mileage_entry):
        """Test logging a mileage entry."""
        entry_id = db.log_mileage(
            user_id=test_user_id,
            trip_date=sample_mileage_entry["trip_date"].isoformat(),
            start=sample_mileage_entry["start_location"],
            end=sample_mileage_entry["end_location"],
            distance=sample_mileage_entry["distance_miles"],
            purpose=sample_mileage_entry["purpose"],
            **{k: v for k, v in sample_mileage_entry.items() 
               if k not in ["trip_date", "start_location", "end_location", "distance_miles", "purpose"]}
        )
        
        assert entry_id is not None
        assert isinstance(entry_id, int)
    
    def test_mileage_claim_calculation(self, db, test_user_id):
        """Test that 50 miles at 45p = £22.50."""
        db.log_mileage(
            test_user_id,
            date.today().isoformat(),
            "Home",
            "Office",
            50.0,
            "Business trip",
            amount_claimable=22.50,
            passenger_allowance=2.50
        )
        
        summary = db.get_mileage_summary(test_user_id, f"{date.today().year}-{str(date.today().year+1)[-2:]}")
        
        assert summary["total_business_miles"] == 50.0
        assert summary["total_claimable"] == 22.50
        assert summary["total_passenger_allowance"] == 2.50
    
    def test_tiered_rate_calculation(self, db, test_user_id):
        """Test HMRC tiered rates (45p then 25p after 10k)."""
        # Log 10,050 miles
        for i in range(201):  # 201 trips × 50 miles = 10,050
            db.log_mileage(
                test_user_id,
                date.today().isoformat(),
                "A",
                "B",
                50.0,
                "Trip",
                amount_claimable=22.50 if i < 200 else 12.50  # Last 50 miles at 25p
            )
        
        summary = db.get_mileage_summary(test_user_id, f"{date.today().year}-{str(date.today().year+1)[-2:]}")
        
        assert summary["total_business_miles"] == 10050.0
        assert summary["miles_at_45p"] == 10000.0
        assert summary["miles_at_25p"] == 50.0


class TestSubscriptions:
    """Test subscription tracking."""
    
    def test_add_subscription(self, db, test_user_id, sample_subscription):
        """Test adding a subscription."""
        sub_id = db.add_subscription(
            user_id=test_user_id,
            name=sample_subscription["name"],
            provider=sample_subscription["provider"],
            cost_monthly=sample_subscription["cost_monthly"],
            category=sample_subscription["category"]
        )
        
        assert sub_id is not None
        assert isinstance(sub_id, int)
    
    def test_get_monthly_cost(self, db, test_user_id):
        """Test monthly cost calculation."""
        # Add subscriptions
        db.add_subscription(test_user_id, "Netflix", "Netflix", 15.99, category="entertainment")
        db.add_subscription(test_user_id, "Spotify", "Spotify", 10.99, category="entertainment")
        db.add_subscription(test_user_id, "Adobe", "Adobe", 56.00, category="software")
        
        total = db.get_monthly_subscriptions_cost(test_user_id)
        
        assert total == 82.98  # 15.99 + 10.99 + 56.00
    
    def test_get_subscriptions_sorted(self, db, test_user_id):
        """Test subscriptions sorted by cost."""
        db.add_subscription(test_user_id, "Cheap", "Provider", 5.00)
        db.add_subscription(test_user_id, "Expensive", "Provider", 50.00)
        db.add_subscription(test_user_id, "Medium", "Provider", 25.00)
        
        subs = db.get_subscriptions(test_user_id)
        
        assert len(subs) == 3
        assert subs[0]["cost_monthly"] == 50.00  # Highest first
        assert subs[1]["cost_monthly"] == 25.00
        assert subs[2]["cost_monthly"] == 5.00


class TestHoldings:
    """Test portfolio holdings."""
    
    def test_add_holding(self, db):
        """Test adding a holding."""
        holding_id = db.add_holding(
            ticker="AAPL",
            shares=10.0,
            avg_cost=150.0,
            account_type="ISA"
        )
        
        assert holding_id is not None
        assert isinstance(holding_id, int)
    
    def test_get_holdings(self, db):
        """Test getting holdings."""
        db.add_holding("AAPL", 10.0, 150.0, account_type="ISA")
        db.add_holding("MSFT", 5.0, 250.0, account_type="GIA")
        
        holdings = db.get_holdings()
        
        assert len(holdings) == 2
        tickers = [h["ticker"] for h in holdings]
        assert "AAPL" in tickers
        assert "MSFT" in tickers
    
    def test_update_price(self, db):
        """Test price updates."""
        db.add_holding("AAPL", 10.0, 150.0)
        db.update_price("AAPL", 175.0)
        
        holdings = db.get_holdings()
        aapl = [h for h in holdings if h["ticker"] == "AAPL"][0]
        
        assert aapl["current_price"] == 175.0


class TestTransactions:
    """Test transaction recording."""
    
    def test_record_transaction(self, db):
        """Test recording a buy transaction."""
        tx_id = db.record_transaction(
            ticker="AAPL",
            transaction_type="BUY",
            amount=1500.0,
            shares=10.0,
            price=150.0,
            account_type="ISA"
        )
        
        assert tx_id is not None
    
    def test_get_transactions(self, db):
        """Test getting transactions."""
        db.record_transaction("AAPL", "BUY", 1500.0, shares=10.0, price=150.0)
        db.record_transaction("MSFT", "BUY", 1250.0, shares=5.0, price=250.0)
        
        transactions = db.get_transactions()
        
        assert len(transactions) == 2
    
    def test_filter_by_ticker(self, db):
        """Test filtering transactions by ticker."""
        db.record_transaction("AAPL", "BUY", 1500.0, shares=10.0, price=150.0)
        db.record_transaction("MSFT", "BUY", 1250.0, shares=5.0, price=250.0)
        
        aapl_txs = db.get_transactions(ticker="AAPL")
        
        assert len(aapl_txs) == 1
        assert aapl_txs[0]["ticker"] == "AAPL"


class TestTaxRecords:
    """Test tax tracking."""
    
    def test_update_tax_year(self, db):
        """Test updating tax records."""
        record_id = db.update_tax_year(
            "2024-25",
            cgt_realized=5000.0,
            isa_contributions=15000.0
        )
        
        assert record_id is not None
    
    def test_get_tax_summary(self, db):
        """Test getting tax summary."""
        db.update_tax_year("2024-25", cgt_realized=5000.0)
        
        summary = db.get_tax_summary("2024-25")
        
        assert summary["tax_year"] == "2024-25"
        assert summary["cgt_realized"] == 5000.0


# Run with: pytest tests/unit/test_database.py -v
