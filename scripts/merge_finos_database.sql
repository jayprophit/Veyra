-- ================================================================
-- FinOS Database Schema Extensions for Veyra
-- Merge these tables into your existing database
-- ================================================================

-- Enable required extensions (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================================
-- 1. VEHICLES & FUEL TRACKING (From FinOS fuel_tracker.py)
-- ================================================================

CREATE TABLE IF NOT EXISTS vehicles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    make            TEXT NOT NULL,
    model           TEXT NOT NULL,
    registration    TEXT,
    fuel_type       TEXT CHECK (fuel_type IN ('petrol', 'diesel', 'electric', 'hybrid', 'lpg')),
    engine_size_cc  INTEGER,
    year            INTEGER,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vehicles_user ON vehicles(user_id);

-- Mileage log for HMRC Self Assessment
CREATE TABLE IF NOT EXISTS mileage_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vehicle_id          UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    trip_date           DATE NOT NULL,
    start_location      TEXT NOT NULL,
    end_location        TEXT NOT NULL,
    start_postcode      TEXT,
    end_postcode        TEXT,
    purpose             TEXT NOT NULL,  -- Business purpose
    distance_miles      DECIMAL(10,2) NOT NULL CHECK (distance_miles > 0),
    passengers          INTEGER DEFAULT 0 CHECK (passengers >= 0),
    is_business         BOOLEAN DEFAULT TRUE,
    amount_claimable    DECIMAL(10,2),  -- Calculated HMRC amount
    passenger_allowance DECIMAL(10,2),  -- Additional passenger amount
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mileage_user ON mileage_log(user_id);
CREATE INDEX IF NOT EXISTS idx_mileage_date ON mileage_log(trip_date);
CREATE INDEX IF NOT EXISTS idx_mileage_vehicle ON mileage_log(vehicle_id);

-- Fuel purchase tracking
CREATE TABLE IF NOT EXISTS fuel_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vehicle_id          UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    purchase_date       DATE NOT NULL,
    odometer_reading    INTEGER NOT NULL CHECK (odometer_reading > 0),
    litres              DECIMAL(10,3) NOT NULL CHECK (litres > 0),
    price_per_litre     DECIMAL(10,3) NOT NULL CHECK (price_per_litre > 0),
    total_cost          DECIMAL(10,2) NOT NULL CHECK (total_cost > 0),
    fuel_type           TEXT NOT NULL CHECK (fuel_type IN ('petrol', 'diesel', 'electric', 'lpg', 'hybrid')),
    is_full_tank        BOOLEAN DEFAULT FALSE,
    mpg                 DECIMAL(5,2),   -- Calculated MPG
    station             TEXT,
    receipt_path        TEXT,           -- Path to receipt in MinIO/S3
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fuel_user ON fuel_log(user_id);
CREATE INDEX IF NOT EXISTS idx_fuel_vehicle ON fuel_log(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_fuel_date ON fuel_log(purchase_date);

-- Materialized view for yearly HMRC mileage summary
CREATE MATERIALIZED VIEW IF NOT EXISTS yearly_mileage_summary AS
SELECT 
    user_id,
    DATE_TRUNC('year', trip_date) AS tax_year,
    COUNT(*) AS total_trips,
    SUM(distance_miles) AS total_business_miles,
    SUM(amount_claimable) AS total_claimable,
    SUM(passenger_allowance) AS total_passenger_allowance
FROM mileage_log
WHERE is_business = TRUE
GROUP BY user_id, DATE_TRUNC('year', trip_date);

CREATE UNIQUE INDEX IF NOT EXISTS idx_yearly_mileage_summary 
ON yearly_mileage_summary(user_id, tax_year);

-- Function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_mileage_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY yearly_mileage_summary;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- 2. BILLS & SUBSCRIPTIONS (From FinOS schema)
-- ================================================================

CREATE TABLE IF NOT EXISTS subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    provider        TEXT NOT NULL,
    category        TEXT CHECK (category IN ('entertainment', 'software', 'utilities', 'finance', 'health', 'other')),
    cost_monthly    DECIMAL(10,2) NOT NULL CHECK (cost_monthly >= 0),
    currency        TEXT DEFAULT 'GBP',
    billing_cycle   TEXT DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'yearly', 'quarterly')),
    next_bill_date  DATE,
    payment_method  TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    cancel_url      TEXT,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_next_bill ON subscriptions(next_bill_date);

-- Bills (one-time or recurring)
CREATE TABLE IF NOT EXISTS bills (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    category        TEXT,
    amount          DECIMAL(10,2) NOT NULL,
    currency        TEXT DEFAULT 'GBP',
    due_date        DATE,
    is_paid         BOOLEAN DEFAULT FALSE,
    is_recurring    BOOLEAN DEFAULT FALSE,
    recurrence_period TEXT CHECK (recurrence_period IN ('weekly', 'monthly', 'quarterly', 'yearly')),
    provider        TEXT,
    payment_method  TEXT,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bills_user ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_due_date ON bills(due_date);

-- ================================================================
-- 3. ENHANCED HOLDINGS (Add FinOS fields)
-- ================================================================

-- Add new columns to existing holdings table (if they don't exist)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='holdings' AND column_name='avg_cost') THEN
        ALTER TABLE holdings ADD COLUMN avg_cost DECIMAL(20,8);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='holdings' AND column_name='exchange') THEN
        ALTER TABLE holdings ADD COLUMN exchange TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='holdings' AND column_name='notes') THEN
        ALTER TABLE holdings ADD COLUMN notes TEXT;
    END IF;
END $$;

-- Add new asset types if not exists
ALTER TABLE holdings DROP CONSTRAINT IF EXISTS holdings_asset_type_check;
ALTER TABLE holdings ADD CONSTRAINT holdings_asset_type_check 
    CHECK (asset_type IN ('stock','crypto','etf','bond','commodity',
                         'real_estate','cash','pension','isa','lisa','other'));

-- ================================================================
-- 4. DUST CONVERSIONS (Crypto micro-asset optimization)
-- ================================================================

CREATE TABLE IF NOT EXISTS dust_conversions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_asset    TEXT NOT NULL,
    source_amount   DECIMAL(20,8) NOT NULL,
    target_asset    TEXT NOT NULL DEFAULT 'BTC',
    target_amount   DECIMAL(20,8),
    exchange        TEXT,
    fees_paid       DECIMAL(20,8),
    conversion_date TIMESTAMPTZ DEFAULT NOW(),
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_dust_user ON dust_conversions(user_id);

-- ================================================================
-- 5. TAX SUBMISSIONS TRACKING (HMRC MTD)
-- ================================================================

CREATE TABLE IF NOT EXISTS tax_submissions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tax_year            TEXT NOT NULL,  -- e.g., '2026-27'
    submission_type     TEXT NOT NULL CHECK (submission_type IN ('self_assessment', 'vat', 'corporation_tax')),
    period_start        DATE,
    period_end          DATE,
    submission_date     TIMESTAMPTZ,
    hmrc_reference      TEXT,
    status              TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'accepted', 'rejected', 'amended')),
    total_income        DECIMAL(15,2),
    total_expenses      DECIMAL(15,2),
    taxable_amount      DECIMAL(15,2),
    tax_due             DECIMAL(15,2),
    xml_payload         TEXT,  -- MTD XML submission
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tax_user ON tax_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_tax_year ON tax_submissions(tax_year);

-- ================================================================
-- 6. TRIGGERS FOR UPDATED_AT
-- ================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
DO $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN 
        SELECT table_name 
        FROM information_schema.columns 
        WHERE column_name = 'updated_at' 
        AND table_schema = 'public'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS trg_%I_updated_at ON %I',
                     table_record.table_name, table_record.table_name);
        EXECUTE format('CREATE TRIGGER trg_%I_updated_at 
                       BEFORE UPDATE ON %I 
                       FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()',
                     table_record.table_name, table_record.table_name);
    END LOOP;
END $$;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT 'Migration complete' as status, 
       (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public') as total_tables;
