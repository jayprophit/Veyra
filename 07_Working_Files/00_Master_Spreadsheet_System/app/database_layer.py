"""Financial Master - Database Layer. Free SQLite + scalable PostgreSQL/TimescaleDB."""

import os, sqlite3, json, asyncio
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, date
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Database')

class DatabaseType(Enum):
    SQLITE = "sqlite"      # Free, file-based, zero cost
    POSTGRES = "postgres"  # Requires server, scalable
    TIMESCALE = "timescale"  # Time-series optimized Postgres

@dataclass
class DatabaseConfig:
    db_type: DatabaseType = DatabaseType.SQLITE
    # SQLite (free tier)
    sqlite_path: str = "./data/financial_master.db"
    # PostgreSQL (optional upgrade)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "finmaster"
    postgres_password: str = ""
    postgres_db: str = "financial_master"
    # Connection pooling
    min_connections: int = 1
    max_connections: int = 10

class DatabaseManager:
    """Unified database interface supporting SQLite (free) and PostgreSQL (scalable)."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.conn: Optional[Union[sqlite3.Connection, Any]] = None
        self._setup()
    
    def _setup(self):
        """Initialize database connection and schema."""
        if self.config.db_type == DatabaseType.SQLITE:
            self._init_sqlite()
        else:
            self._init_postgres()
        self._create_tables()
        logger.info(f"✓ Database ready: {self.config.db_type.value}")
    
    def _init_sqlite(self):
        """Initialize SQLite (free, zero cost)."""
        os.makedirs(os.path.dirname(self.config.sqlite_path), exist_ok=True)
        self.conn = sqlite3.connect(self.config.sqlite_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
    
    def _init_postgres(self):
        """Initialize PostgreSQL/TimescaleDB (scalable tier)."""
        try:
            import asyncpg
            # Async connection pool would be set up here
            logger.info("PostgreSQL mode (requires asyncpg)")
        except ImportError:
            logger.warning("asyncpg not installed, falling back to SQLite")
            self.config.db_type = DatabaseType.SQLITE
            self._init_sqlite()
    
    def _create_tables(self):
        """Create all required tables."""
        tables = [
            # Holdings table
            """CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                name TEXT,
                shares REAL NOT NULL,
                avg_cost REAL,
                current_price REAL,
                currency TEXT DEFAULT 'GBP',
                account_type TEXT CHECK(account_type IN ('GIA', 'ISA', 'SIPP', 'JISA')),
                sector TEXT,
                region TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            # Transactions table
            """CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                transaction_type TEXT CHECK(transaction_type IN ('BUY', 'SELL', 'DIVIDEND')),
                shares REAL,
                price REAL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'GBP',
                account_type TEXT,
                transaction_date DATE,
                executed_by TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            # Price history (for time-series analysis)
            """CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                price REAL NOT NULL,
                volume INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT DEFAULT 'manual'
            )""",
            # Tax records
            """CREATE TABLE IF NOT EXISTS tax_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tax_year TEXT NOT NULL,
                cgt_realized REAL DEFAULT 0,
                cgt_allowance_used REAL DEFAULT 0,
                isa_contributions REAL DEFAULT 0,
                isa_allowance REAL DEFAULT 20000,
                sipp_contributions REAL DEFAULT 0,
                dividend_income REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            # Agent decisions log
            """CREATE TABLE IF NOT EXISTS agent_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT UNIQUE,
                agent_name TEXT,
                action_type TEXT,
                risk_level TEXT,
                description TEXT,
                details TEXT,
                confidence REAL,
                status TEXT,
                approved_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            # Performance metrics
            """CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_value REAL,
                day_return REAL,
                cumulative_return REAL,
                benchmark_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            # ===== FUEL & MILEAGE TRACKER (From FinOS) =====
            # Vehicles registry
            """CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                registration TEXT,
                fuel_type TEXT CHECK(fuel_type IN ('petrol', 'diesel', 'electric', 'hybrid', 'lpg')),
                engine_size_cc INTEGER,
                year INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            # Mileage log for HMRC
            """CREATE TABLE IF NOT EXISTS mileage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                vehicle_id INTEGER,
                trip_date DATE NOT NULL,
                start_location TEXT NOT NULL,
                end_location TEXT NOT NULL,
                start_postcode TEXT,
                end_postcode TEXT,
                purpose TEXT NOT NULL,
                distance_miles REAL NOT NULL,
                passengers INTEGER DEFAULT 0,
                is_business INTEGER DEFAULT 1,
                amount_claimable REAL,
                passenger_allowance REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            )""",
            # Fuel purchase tracking
            """CREATE TABLE IF NOT EXISTS fuel_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                vehicle_id INTEGER,
                purchase_date DATE NOT NULL,
                odometer_reading INTEGER NOT NULL,
                litres REAL NOT NULL,
                price_per_litre REAL NOT NULL,
                total_cost REAL NOT NULL,
                fuel_type TEXT CHECK(fuel_type IN ('petrol', 'diesel', 'electric', 'lpg', 'hybrid')),
                is_full_tank INTEGER DEFAULT 0,
                mpg REAL,
                station TEXT,
                receipt_path TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            )""",
            # ===== BILLS & SUBSCRIPTIONS (From FinOS) =====
            # Subscriptions tracking
            """CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                provider TEXT NOT NULL,
                category TEXT CHECK(category IN ('entertainment', 'software', 'utilities', 'finance', 'health', 'other')),
                cost_monthly REAL NOT NULL DEFAULT 0,
                currency TEXT DEFAULT 'GBP',
                billing_cycle TEXT DEFAULT 'monthly',
                next_bill_date DATE,
                payment_method TEXT,
                is_active INTEGER DEFAULT 1,
                cancel_url TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            # Bills tracking
            """CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'GBP',
                due_date DATE,
                is_paid INTEGER DEFAULT 0,
                is_recurring INTEGER DEFAULT 0,
                recurrence_period TEXT CHECK(recurrence_period IN ('weekly', 'monthly', 'quarterly', 'yearly')),
                provider TEXT,
                payment_method TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
        ]
        
        for table_sql in tables:
            self.conn.execute(table_sql)
        self.conn.commit()
    
    # =========================================================================
    # HOLDINGS CRUD
    # =========================================================================
    
    def add_holding(self, ticker: str, shares: float, avg_cost: float, 
                    account_type: str = "GIA", **kwargs) -> int:
        """Add or update a holding."""
        cursor = self.conn.execute(
            """INSERT INTO holdings (ticker, shares, avg_cost, account_type, name, sector, region)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(ticker, account_type) DO UPDATE SET
               shares = excluded.shares,
               avg_cost = excluded.avg_cost,
               last_updated = CURRENT_TIMESTAMP""",
            (ticker, shares, avg_cost, account_type, 
             kwargs.get('name'), kwargs.get('sector'), kwargs.get('region'))
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_holdings(self, account_type: Optional[str] = None) -> List[Dict]:
        """Get all holdings or filter by account type."""
        if account_type:
            rows = self.conn.execute(
                "SELECT * FROM holdings WHERE account_type = ? ORDER BY ticker",
                (account_type,)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM holdings ORDER BY ticker").fetchall()
        return [dict(row) for row in rows]
    
    def update_price(self, ticker: str, price: float):
        """Update current price for a holding."""
        self.conn.execute(
            "UPDATE holdings SET current_price = ?, last_updated = CURRENT_TIMESTAMP WHERE ticker = ?",
            (price, ticker)
        )
        # Also log to price history
        self.conn.execute(
            "INSERT INTO price_history (ticker, price, source) VALUES (?, ?, ?)",
            (ticker, price, "update_price")
        )
        self.conn.commit()
    
    # =========================================================================
    # TRANSACTIONS
    # =========================================================================
    
    def record_transaction(self, ticker: str, transaction_type: str, amount: float,
                         shares: Optional[float] = None, price: Optional[float] = None,
                         account_type: str = "GIA", **kwargs) -> int:
        """Record a buy/sell/dividend transaction."""
        cursor = self.conn.execute(
            """INSERT INTO transactions 
               (ticker, transaction_type, shares, price, amount, account_type, 
                transaction_date, executed_by, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ticker, transaction_type, shares, price, amount, account_type,
             kwargs.get('date', date.today()), kwargs.get('agent'), kwargs.get('notes'))
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_transactions(self, start_date: Optional[date] = None, 
                        end_date: Optional[date] = None,
                        ticker: Optional[str] = None) -> List[Dict]:
        """Get transactions with optional filters."""
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        if start_date:
            query += " AND transaction_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= ?"
            params.append(end_date)
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
        query += " ORDER BY transaction_date DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    
    # =========================================================================
    # TAX TRACKING
    # =========================================================================
    
    def update_tax_year(self, tax_year: str, **kwargs) -> int:
        """Update tax records for a tax year (e.g., '2024-25')."""
        fields = []
        values = []
        for key in ['cgt_realized', 'cgt_allowance_used', 'isa_contributions', 
                    'isa_allowance', 'sipp_contributions', 'dividend_income']:
            if key in kwargs:
                fields.append(f"{key} = ?")
                values.append(kwargs[key])
        if not fields:
            return 0
        values.append(tax_year)
        
        cursor = self.conn.execute(
            f"""INSERT INTO tax_records (tax_year, {', '.join(kwargs.keys())})
                VALUES (?, {', '.join(['?' for _ in kwargs])})
                ON CONFLICT(tax_year) DO UPDATE SET
                {', '.join([f'{k} = excluded.{k}' for k in kwargs.keys()])},
                updated_at = CURRENT_TIMESTAMP""",
            [tax_year] + list(kwargs.values())
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_tax_summary(self, tax_year: str) -> Dict:
        """Get tax summary for a specific year."""
        row = self.conn.execute(
            "SELECT * FROM tax_records WHERE tax_year = ?", (tax_year,)
        ).fetchone()
        return dict(row) if row else {
            "tax_year": tax_year,
            "cgt_allowance_remaining": 3000,  # 2024-25 allowance
            "isa_allowance_remaining": 20000
        }
    
    # =========================================================================
    # FUEL & MILEAGE (From FinOS)
    # =========================================================================

    def add_vehicle(self, user_id: str, make: str, model: str, **kwargs) -> int:
        """Add a new vehicle."""
        cursor = self.conn.execute(
            """INSERT INTO vehicles (user_id, make, model, registration, fuel_type, engine_size_cc, year)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, make, model, kwargs.get('registration'), kwargs.get('fuel_type'),
             kwargs.get('engine_size_cc'), kwargs.get('year'))
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_vehicles(self, user_id: str) -> List[Dict]:
        """Get all vehicles for a user."""
        rows = self.conn.execute(
            """SELECT * FROM vehicles WHERE user_id = ? AND is_active = 1
               ORDER BY created_at DESC""",
            (user_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    def log_mileage(self, user_id: str, trip_date: str, start: str, end: str,
                    distance: float, purpose: str, **kwargs) -> int:
        """Log a business mileage trip."""
        cursor = self.conn.execute(
            """INSERT INTO mileage_log
                (user_id, vehicle_id, trip_date, start_location, end_location,
                 start_postcode, end_postcode, purpose, distance_miles,
                 passengers, is_business, amount_claimable, passenger_allowance, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, kwargs.get('vehicle_id'), trip_date, start, end,
             kwargs.get('start_postcode'), kwargs.get('end_postcode'), purpose, distance,
             kwargs.get('passengers', 0), 1, kwargs.get('amount_claimable', 0),
             kwargs.get('passenger_allowance', 0), kwargs.get('notes'))
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_mileage_summary(self, user_id: str, tax_year: str) -> Dict:
        """Get HMRC mileage summary for tax year."""
        start_year = int(tax_year.split('-')[0])
        year_start = f"{start_year}-04-06"
        year_end = f"{start_year+1}-04-05"

        row = self.conn.execute(
            """SELECT
                 COUNT(*) as total_trips,
                 COALESCE(SUM(distance_miles), 0) as total_miles,
                 COALESCE(SUM(amount_claimable), 0) as total_claimable,
                 COALESCE(SUM(passenger_allowance), 0) as total_passenger
               FROM mileage_log
               WHERE user_id = ? AND trip_date >= ? AND trip_date <= ? AND is_business = 1""",
            (user_id, year_start, year_end)
        ).fetchone()

        result = dict(row)
        total = float(result.get('total_miles', 0))
        return {
            "tax_year": tax_year,
            "total_trips": int(result.get('total_trips', 0)),
            "total_business_miles": round(total, 2),
            "miles_at_45p": round(min(total, 10000), 2),
            "miles_at_25p": round(max(0, total - 10000), 2),
            "total_claimable": round(float(result.get('total_claimable', 0)), 2),
            "total_passenger_allowance": round(float(result.get('total_passenger', 0)), 2),
            "ytd_progress_pct": round(min(100.0, (total / 10000) * 100), 1)
        }

    def log_fuel_purchase(self, user_id: str, vehicle_id: int, purchase_date: str,
                          odometer: int, litres: float, price_per_litre: float,
                          total_cost: float, **kwargs) -> int:
        """Log a fuel purchase."""
        # Calculate MPG if full tank
        mpg = None
        if kwargs.get('is_full_tank') and vehicle_id:
            prev = self.conn.execute(
                """SELECT odometer_reading FROM fuel_log
                   WHERE user_id = ? AND vehicle_id = ? AND is_full_tank = 1
                   ORDER BY purchase_date DESC LIMIT 1 OFFSET 1""",
                (user_id, vehicle_id)
            ).fetchone()
            if prev:
                miles = odometer - dict(prev)['odometer_reading']
                gallons = litres / 4.54609
                mpg = round(miles / gallons, 1) if gallons > 0 else None

        cursor = self.conn.execute(
            """INSERT INTO fuel_log
                (user_id, vehicle_id, purchase_date, odometer_reading, litres,
                 price_per_litre, total_cost, fuel_type, is_full_tank, mpg, station, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, vehicle_id, purchase_date, odometer, litres, price_per_litre,
             total_cost, kwargs.get('fuel_type'), kwargs.get('is_full_tank', False),
             mpg, kwargs.get('station'), kwargs.get('notes'))
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_yearly_mileage(self, user_id: str, year: int = None) -> List[Dict]:
        """Get monthly mileage breakdown for a year."""
        if year is None:
            year = date.today().year

        rows = self.conn.execute(
            """SELECT
                 strftime('%Y-%m', trip_date) as month,
                 COUNT(*) as trips,
                 SUM(distance_miles) as miles,
                 SUM(amount_claimable) as claimable
               FROM mileage_log
               WHERE user_id = ? AND strftime('%Y', trip_date) = ?
               GROUP BY month
               ORDER BY month""",
            (user_id, str(year))
        ).fetchall()
        return [dict(row) for row in rows]

    # =========================================================================
    # SUBSCRIPTIONS & BILLS (From FinOS)
    # =========================================================================

    def add_subscription(self, user_id: str, name: str, provider: str,
                        cost_monthly: float, **kwargs) -> int:
        """Add a subscription."""
        cursor = self.conn.execute(
            """INSERT INTO subscriptions
                (user_id, name, provider, category, cost_monthly, billing_cycle,
                 next_bill_date, payment_method, cancel_url, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, name, provider, kwargs.get('category'), cost_monthly,
             kwargs.get('billing_cycle', 'monthly'), kwargs.get('next_bill_date'),
             kwargs.get('payment_method'), kwargs.get('cancel_url'), kwargs.get('notes'))
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_subscriptions(self, user_id: str) -> List[Dict]:
        """Get all subscriptions for a user."""
        rows = self.conn.execute(
            """SELECT * FROM subscriptions WHERE user_id = ? AND is_active = 1
               ORDER BY cost_monthly DESC""",
            (user_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    def get_monthly_subscriptions_cost(self, user_id: str) -> float:
        """Calculate total monthly subscription cost."""
        row = self.conn.execute(
            """SELECT COALESCE(SUM(cost_monthly), 0) as total
               FROM subscriptions WHERE user_id = ? AND is_active = 1""",
            (user_id,)
        ).fetchone()
        return float(dict(row)['total']) if row else 0.0

    # =========================================================================
    # ANALYTICS QUERIES
    # =========================================================================

    def get_portfolio_value(self) -> Dict[str, float]:
        """Calculate current portfolio value by account."""
        query = """
            SELECT 
                account_type,
                SUM(shares * COALESCE(current_price, avg_cost)) as value,
                SUM(shares * avg_cost) as cost_basis
            FROM holdings
            WHERE shares > 0
            GROUP BY account_type
        """
        result = {"total": 0, "cost_basis": 0, "unrealized_pnl": 0}
        for row in self.conn.execute(query).fetchall():
            account, value, cost = row
            result[account] = {"value": value, "cost": cost, "pnl": value - cost}
            result["total"] += value
            result["cost_basis"] += cost
        result["unrealized_pnl"] = result["total"] - result["cost_basis"]
        return result
    
    def get_allocation(self) -> List[Dict]:
        """Get portfolio allocation by sector and region."""
        total = self.get_portfolio_value()["total"]
        if total == 0:
            return []
        query = """
            SELECT 
                sector,
                region,
                SUM(shares * COALESCE(current_price, avg_cost)) / ? * 100 as allocation_pct
            FROM holdings
            WHERE shares > 0
            GROUP BY sector, region
            ORDER BY allocation_pct DESC
        """
        return [dict(row) for row in self.conn.execute(query, (total,)).fetchall()]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Financial Master - Database Layer")
    print("="*60)
    
    # Use SQLite (free, zero cost)
    db = DatabaseManager(DatabaseConfig(db_type=DatabaseType.SQLITE))
    
    # Add sample holdings
    db.add_holding("VUAG", 100, 85.50, "ISA", name="Vanguard S&P 500", sector="Equity", region="US")
    db.add_holding("AGGH", 50, 92.30, "GIA", name="iShares Aggregate Bond", sector="Bonds", region="Global")
    db.add_holding("AYEM", 200, 78.45, "ISA", name="Vanguard Emerging Markets", sector="Equity", region="EM")
    
    # Update prices
    db.update_price("VUAG", 87.20)
    db.update_price("AGGH", 91.80)
    db.update_price("AYEM", 76.90)
    
    # Get portfolio summary
    print("\n📊 Portfolio Summary:")
    summary = db.get_portfolio_value()
    for account, data in summary.items():
        if isinstance(data, dict):
            print(f"  {account}: £{data['value']:,.2f} (P&L: £{data['pnl']:+,.2f})")
    print(f"\n  Total Value: £{summary['total']:,.2f}")
    print(f"  Unrealized P&L: £{summary['unrealized_pnl']:+,.2f}")
    
    # Get holdings
    print("\n📋 Holdings:")
    for h in db.get_holdings():
        value = h['shares'] * (h['current_price'] or h['avg_cost'])
        print(f"  {h['ticker']}: {h['shares']} shares @ £{h['current_price'] or h['avg_cost']:.2f} = £{value:,.2f} [{h['account_type']}]")
    
    db.close()
    print("\n✓ Database test complete")
    print("="*60)
