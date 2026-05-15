# Veyra Database Schema

## Overview

Comprehensive database schema for the Veyra financial platform, covering authentication, trading, market data, AI/ML, and analytics.

## Technology Stack

- **Primary Database**: PostgreSQL 15+
- **Cache Layer**: Redis 7+
- **Vector Database**: Qdrant (for AI embeddings)
- **ORM**: SQLAlchemy (Python)
- **Migrations**: Alembic

## Core Tables

### 1. Authentication & Authorization

#### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    avatar_url TEXT,
    tier VARCHAR(20) DEFAULT 'free', -- free, pro, enterprise
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_tier (tier)
);
```

#### sessions
```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    device_info TEXT,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_token (token),
    INDEX idx_expires_at (expires_at)
);
```

#### oauth_providers
```sql
CREATE TABLE oauth_providers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- google, github, etc.
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, provider_user_id),
    INDEX idx_user_id (user_id)
);
```

#### api_keys
```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    permissions JSONB, -- {"read": true, "trade": false}
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_key_hash (key_hash)
);
```

### 2. Trading & Portfolio Management

#### portfolios
```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    is_paper_trading BOOLEAN DEFAULT TRUE,
    broker_id VARCHAR(50), -- alpaca, ibkr, etc.
    broker_account_id VARCHAR(100),
    cash_balance DECIMAL(12, 2) DEFAULT 0.00,
    total_value DECIMAL(12, 2) DEFAULT 0.00,
    day_pnl DECIMAL(12, 2) DEFAULT 0.00,
    total_pnl DECIMAL(12, 2) DEFAULT 0.00,
    day_pnl_pct DECIMAL(5, 2) DEFAULT 0.00,
    total_pnl_pct DECIMAL(5, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_broker_account_id (broker_account_id)
);
```

#### positions
```sql
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    asset_type VARCHAR(20) DEFAULT 'stock', -- stock, etf, option, crypto, forex
    quantity DECIMAL(12, 4) DEFAULT 0.00,
    avg_cost DECIMAL(12, 4) DEFAULT 0.00,
    current_price DECIMAL(12, 4),
    market_value DECIMAL(12, 2) DEFAULT 0.00,
    cost_basis DECIMAL(12, 2) DEFAULT 0.00,
    unrealized_pnl DECIMAL(12, 2) DEFAULT 0.00,
    unrealized_pnl_pct DECIMAL(5, 2) DEFAULT 0.00,
    day_change DECIMAL(12, 2) DEFAULT 0.00,
    day_change_pct DECIMAL(5, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_portfolio_id (portfolio_id),
    INDEX idx_symbol (symbol),
    UNIQUE(portfolio_id, symbol)
);
```

#### transactions
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    position_id INTEGER REFERENCES positions(id) ON DELETE SET NULL,
    symbol VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL, -- buy, sell, dividend, split, deposit, withdrawal
    quantity DECIMAL(12, 4) DEFAULT 0.00,
    price DECIMAL(12, 4),
    amount DECIMAL(12, 2),
    commission DECIMAL(10, 2) DEFAULT 0.00,
    fees DECIMAL(10, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    notes TEXT,
    external_transaction_id VARCHAR(100),
    transaction_date TIMESTAMP NOT NULL,
    settled_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_portfolio_id (portfolio_id),
    INDEX idx_symbol (symbol),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_external_transaction_id (external_transaction_id)
);
```

#### orders
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    order_type VARCHAR(20) NOT NULL, -- market, limit, stop, stop_limit, trailing_stop
    order_status VARCHAR(20) DEFAULT 'pending', -- pending, submitted, partially_filled, filled, cancelled, rejected
    side VARCHAR(10) NOT NULL, -- buy, sell
    quantity DECIMAL(12, 4) NOT NULL,
    price DECIMAL(12, 4),
    stop_price DECIMAL(12, 4),
    trailing_percent DECIMAL(5, 2),
    time_in_force VARCHAR(20) DEFAULT 'day', -- day, gtc, ioc, fok
    filled_quantity DECIMAL(12, 4) DEFAULT 0.00,
    avg_filled_price DECIMAL(12, 4),
    remaining_quantity DECIMAL(12, 4),
    commission DECIMAL(10, 2) DEFAULT 0.00,
    external_order_id VARCHAR(100) UNIQUE,
    broker_order_id VARCHAR(100),
    submitted_at TIMESTAMP,
    filled_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_portfolio_id (portfolio_id),
    INDEX idx_symbol (symbol),
    INDEX idx_order_status (order_status),
    INDEX idx_external_order_id (external_order_id)
);
```

#### order_fills
```sql
CREATE TABLE order_fills (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    fill_id VARCHAR(100) UNIQUE,
    quantity DECIMAL(12, 4) NOT NULL,
    price DECIMAL(12, 4) NOT NULL,
    commission DECIMAL(10, 2) DEFAULT 0.00,
    fill_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_fill_timestamp (fill_timestamp)
);
```

### 3. Market Data

#### securities
```sql
CREATE TABLE securities (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    asset_type VARCHAR(20) NOT NULL, -- stock, etf, option, crypto, forex, future
    exchange VARCHAR(50),
    currency VARCHAR(3) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    shares_outstanding BIGINT,
    ipo_date DATE,
    delisted_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_asset_type (asset_type),
    INDEX idx_exchange (exchange)
);
```

#### market_data_daily
```sql
CREATE TABLE market_data_daily (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(12, 4),
    high DECIMAL(12, 4),
    low DECIMAL(12, 4),
    close DECIMAL(12, 4),
    adjusted_close DECIMAL(12, 4),
    volume BIGINT,
    dividends DECIMAL(12, 4) DEFAULT 0.00,
    splits DECIMAL(10, 4) DEFAULT 1.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date),
    INDEX idx_symbol_date (symbol, date),
    INDEX idx_date (date)
);
```

#### market_data_intraday
```sql
CREATE TABLE market_data_intraday (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(12, 4),
    high DECIMAL(12, 4),
    low DECIMAL(12, 4),
    close DECIMAL(12, 4),
    volume BIGINT,
    vwap DECIMAL(12, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_timestamp (symbol, timestamp),
    INDEX idx_timestamp (timestamp)
);
```

#### market_data_realtime
```sql
-- This table is used for caching real-time data in Redis
-- Schema: key = "quote:{symbol}", value = JSON with price, change, volume, etc.
-- TTL: 5 seconds
```

### 4. Watchlists & Alerts

#### watchlists
```sql
CREATE TABLE watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

#### watchlist_items
```sql
CREATE TABLE watchlist_items (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER REFERENCES watchlists(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    notes TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(watchlist_id, symbol),
    INDEX idx_watchlist_id (watchlist_id),
    INDEX idx_symbol (symbol)
);
```

#### alerts
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE SET NULL,
    symbol VARCHAR(20),
    alert_type VARCHAR(50) NOT NULL, -- price_above, price_below, percent_change, volume_spike, news_sentiment
    condition VARCHAR(50) NOT NULL, -- gt, lt, gte, lte, eq
    target_value DECIMAL(12, 4) NOT NULL,
    current_value DECIMAL(12, 4),
    is_active BOOLEAN DEFAULT TRUE,
    triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMP,
    notification_channels JSONB, -- ["email", "push", "sms", "telegram"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_symbol (symbol),
    INDEX idx_is_active (is_active)
);
```

### 5. Analytics & Performance

#### portfolio_performance
```sql
CREATE TABLE portfolio_performance (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_value DECIMAL(12, 2),
    daily_return DECIMAL(8, 4),
    cumulative_return DECIMAL(8, 4),
    benchmark_return DECIMAL(8, 4),
    volatility DECIMAL(8, 4),
    sharpe_ratio DECIMAL(8, 4),
    max_drawdown DECIMAL(8, 4),
    beta DECIMAL(8, 4),
    alpha DECIMAL(8, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, date),
    INDEX idx_portfolio_date (portfolio_id, date),
    INDEX idx_date (date)
);
```

#### trade_analytics
```sql
CREATE TABLE trade_analytics (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    period VARCHAR(20) NOT NULL, -- daily, weekly, monthly, yearly
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate DECIMAL(5, 2),
    avg_win DECIMAL(12, 2),
    avg_loss DECIMAL(12, 2),
    profit_factor DECIMAL(8, 2),
    total_commission DECIMAL(12, 2),
    net_pnl DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_portfolio_period (portfolio_id, period),
    INDEX idx_date_range (start_date, end_date)
);
```

### 6. Risk Management

#### risk_metrics
```sql
CREATE TABLE risk_metrics (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    calculated_at TIMESTAMP NOT NULL,
    var_95 DECIMAL(12, 2), -- Value at Risk 95%
    var_99 DECIMAL(12, 2), -- Value at Risk 99%
    expected_shortfall DECIMAL(12, 2),
    beta DECIMAL(8, 4),
    delta DECIMAL(8, 4),
    gamma DECIMAL(8, 4),
    theta DECIMAL(8, 4),
    vega DECIMAL(8, 4),
    portfolio_volatility DECIMAL(8, 4),
    correlation_matrix JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_portfolio_calculated (portfolio_id, calculated_at)
);
```

#### position_limits
```sql
CREATE TABLE position_limits (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(20),
    limit_type VARCHAR(50) NOT NULL, -- max_position_size, max_loss, max_exposure
    limit_value DECIMAL(12, 2) NOT NULL,
    current_value DECIMAL(12, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_portfolio_id (portfolio_id),
    INDEX idx_symbol (symbol)
);
```

### 7. AI/ML Features

#### predictions
```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL, -- price_direction, volatility, trend, sentiment
    prediction_horizon VARCHAR(20) NOT NULL, -- 1d, 1w, 1m
    predicted_value DECIMAL(12, 4),
    confidence DECIMAL(5, 2),
    features JSONB,
    prediction_timestamp TIMESTAMP NOT NULL,
    target_timestamp TIMESTAMP NOT NULL,
    actual_value DECIMAL(12, 4),
    accuracy DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_prediction_timestamp (prediction_timestamp),
    INDEX idx_target_timestamp (target_timestamp),
    INDEX idx_model_id (model_id)
);
```

#### model_training_data
```sql
CREATE TABLE model_training_data (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- price, sentiment, news, fundamentals
    symbol VARCHAR(20),
    start_date DATE,
    end_date DATE,
    data_point_count INTEGER,
    features JSONB,
    labels JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_id (model_id),
    INDEX idx_symbol (symbol)
);
```

#### ai_insights
```sql
CREATE TABLE ai_insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE SET NULL,
    insight_type VARCHAR(50) NOT NULL, -- portfolio_rebalance, risk_alert, opportunity
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    confidence DECIMAL(5, 2),
    action_items JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_portfolio_id (portfolio_id),
    INDEX idx_is_read (is_read)
);
```

### 8. News & Sentiment

#### news_articles
```sql
CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,
    url TEXT UNIQUE,
    source VARCHAR(100),
    author VARCHAR(255),
    published_at TIMESTAMP NOT NULL,
    symbols JSONB, -- ["AAPL", "MSFT"]
    sentiment_score DECIMAL(5, 2), -- -1.0 to 1.0
    sentiment_label VARCHAR(20), -- positive, negative, neutral
    relevance_score DECIMAL(5, 2),
    embedding VECTOR(1536), -- For semantic search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_published_at (published_at),
    INDEX idx_symbols (symbols),
    INDEX idx_sentiment (sentiment_score)
);
```

#### earnings_calendar
```sql
CREATE TABLE earnings_calendar (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    fiscal_quarter VARCHAR(10),
    earnings_date DATE NOT NULL,
    eps_estimate DECIMAL(10, 2),
    eps_actual DECIMAL(10, 2),
    revenue_estimate DECIMAL(15, 2),
    revenue_actual DECIMAL(15, 2),
    surprise_pct DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_earnings_date (earnings_date)
);
```

### 9. Notifications

#### notifications
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- order_filled, alert_triggered, insight_generated, news
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
);
```

#### notification_preferences
```sql
CREATE TABLE notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    email_enabled BOOLEAN DEFAULT TRUE,
    push_enabled BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    telegram_enabled BOOLEAN DEFAULT FALSE,
    order_filled BOOLEAN DEFAULT TRUE,
    alert_triggered BOOLEAN DEFAULT TRUE,
    insight_generated BOOLEAN DEFAULT TRUE,
    news_alerts BOOLEAN DEFAULT FALSE,
    daily_summary BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

### 10. Settings & Preferences

#### user_settings
```sql
CREATE TABLE user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    theme VARCHAR(20) DEFAULT 'dark', -- light, dark, system
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    currency VARCHAR(3) DEFAULT 'USD',
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    time_format VARCHAR(10) DEFAULT '24h', -- 12h, 24h
    default_portfolio_id INTEGER REFERENCES portfolios(id),
    risk_tolerance VARCHAR(20) DEFAULT 'moderate', -- conservative, moderate, aggressive
    investment_goals JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

### 11. Audit & Logging

#### audit_logs
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);
```

#### error_logs
```sql
CREATE TABLE error_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL, -- debug, info, warning, error, critical
    service VARCHAR(50),
    error_code VARCHAR(50),
    message TEXT NOT NULL,
    stack_trace TEXT,
    context JSONB,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level (level),
    INDEX idx_service (service),
    INDEX idx_created_at (created_at)
);
```

## Redis Data Structures

### Real-time Quotes
```
Key: quote:{symbol}
Type: Hash
Fields:
  - price: DECIMAL
  - change: DECIMAL
  - change_pct: DECIMAL
  - volume: BIGINT
  - high: DECIMAL
  - low: DECIMAL
  - open: DECIMAL
  - timestamp: TIMESTAMP
TTL: 5 seconds
```

### User Sessions
```
Key: session:{token}
Type: Hash
Fields:
  - user_id: INTEGER
  - expires_at: TIMESTAMP
  - device_info: JSON
TTL: 24 hours
```

### Rate Limiting
```
Key: ratelimit:{user_id}:{endpoint}
Type: String
Value: request_count
TTL: 60 seconds
```

### WebSocket Connections
```
Key: ws:{user_id}
Type: Set
Values: connection_ids
TTL: 1 hour
```

## Indexes Strategy

### Primary Indexes
- All primary keys are indexed automatically
- Foreign keys are indexed for join performance

### Composite Indexes
- (portfolio_id, symbol) for positions
- (symbol, date) for market data
- (user_id, created_at) for notifications
- (portfolio_id, calculated_at) for risk metrics

### Partial Indexes
- Create partial indexes for active records only
- Example: CREATE INDEX idx_active_alerts ON alerts(user_id) WHERE is_active = true

## Partitioning Strategy

### Market Data Partitioning
- Partition `market_data_daily` by date ranges (monthly or quarterly)
- Partition `market_data_intraday` by date ranges (daily)

### Transaction Log Partitioning
- Partition `transactions` by date ranges (monthly)
- Partition `audit_logs` by date ranges (monthly)

## Data Retention Policy

### Market Data
- Daily data: Keep indefinitely
- Intraday data: Keep 90 days
- Real-time cache: 5 seconds (Redis)

### Logs
- Audit logs: Keep 1 year
- Error logs: Keep 90 days
- Application logs: Keep 30 days

### Notifications
- Read notifications: Archive after 90 days
- Unread notifications: Keep indefinitely

## Migration Strategy

Use Alembic for database migrations:

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Backup Strategy

### Daily Backups
- Full database backup at 2 AM UTC
- Keep 7 daily backups

### Weekly Backups
- Full backup on Sunday
- Keep 4 weekly backups

### Monthly Backups
- Full backup on 1st of month
- Keep 12 monthly backups

### Point-in-Time Recovery
- Enable WAL (Write-Ahead Logging)
- Keep WAL logs for 7 days

## Security Considerations

### Encryption at Rest
- Enable TDE (Transparent Data Encryption)
- Encrypt sensitive fields (password_hash, api_keys, tokens)

### Row-Level Security
- Implement RLS policies for multi-tenant isolation
- Users can only access their own data

### Audit Logging
- Log all data access modifications
- Track who accessed what and when

## Performance Optimization

### Connection Pooling
- Use connection pooling (PgBouncer)
- Pool size: 20-50 connections

### Query Optimization
- Use EXPLAIN ANALYZE for slow queries
- Add appropriate indexes
- Use prepared statements

### Caching Strategy
- Cache frequently accessed data in Redis
- Cache user sessions, market data, calculations

### Materialized Views
- Create materialized views for complex aggregations
- Refresh periodically (hourly/daily)

## Monitoring

### Database Metrics
- Connection count
- Query performance
- Lock contention
- Disk usage
- Replication lag

### Alerts
- High CPU usage (>80%)
- High memory usage (>80%)
- Slow queries (>1s)
- Connection pool exhaustion
- Replication lag (>10s)
