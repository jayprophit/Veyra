# Data Layer Documentation

## Overview

The Veyra data layer provides the foundation for storing, processing, and retrieving financial data. This document describes the data architecture, storage systems, and data flow patterns.

## Architecture

### Data Storage Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Caching Layer                        │
│                    (Redis)                               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Time-Series Database                  │
│                    (TimescaleDB)                          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Relational Database                   │
│                    (PostgreSQL)                          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Archival Storage                     │
│                    (Parquet/Delta Lake)                 │
└─────────────────────────────────────────────────────────┘
```

## Components

### Caching Layer (Redis)

**Purpose:** High-performance caching for frequently accessed data

**Use Cases:**
- Session storage
- Real-time market data caching
- API rate limiting
- Pub/Sub messaging
- Leaderboards

**Configuration:**
```yaml
redis:
  host: localhost
  port: 6379
  password: ${REDIS_PASSWORD}
  database: 0
  ttl: 300  # 5 minutes default TTL
```

**Data Patterns:**
- **Key-Value:** Simple key-value pairs
- **Hashes:** Structured data objects
- **Lists:** Ordered collections
- **Sets:** Unique collections
- **Sorted Sets:** Ranked collections

### Time-Series Database (TimescaleDB)

**Purpose:** Optimized storage and querying of time-series data

**Use Cases:**
- Historical market data
- Price history
- Volume data
- Technical indicators
- Performance metrics

**Schema:**
```sql
-- Market data hypertable
CREATE TABLE market_data (
  time TIMESTAMPTZ NOT NULL,
  symbol TEXT NOT NULL,
  price NUMERIC,
  volume BIGINT,
  bid NUMERIC,
  ask NUMERIC
);

-- Create hypertable
SELECT create_hypertable('market_data', 'time');

-- Create index on symbol
CREATE INDEX idx_market_data_symbol ON market_data (symbol, time DESC);
```

**Query Examples:**
```sql
-- Get latest price for a symbol
SELECT * FROM market_data
WHERE symbol = 'AAPL'
ORDER BY time DESC
LIMIT 1;

-- Get hourly aggregation
SELECT
  time_bucket('1 hour', time) AS hour,
  avg(price) AS avg_price,
  max(price) AS max_price,
  min(price) AS min_price
FROM market_data
WHERE symbol = 'AAPL'
GROUP BY hour
ORDER BY hour DESC;
```

### Relational Database (PostgreSQL)

**Purpose:** Structured data storage with ACID compliance

**Use Cases:**
- User accounts
- Portfolio data
- Order history
- Authentication data
- Configuration data

**Schema:**
```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolios table
CREATE TABLE portfolios (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Holdings table
CREATE TABLE holdings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  portfolio_id UUID REFERENCES portfolios(id),
  symbol TEXT NOT NULL,
  quantity NUMERIC NOT NULL,
  avg_cost NUMERIC NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Archival Storage (Parquet/Delta Lake)

**Purpose:** Long-term storage of historical data for analytics

**Use Cases:**
- Backtesting data
- Historical analysis
- Data warehousing
- Machine learning training data

**Format:**
- **Parquet:** Columnar storage format for efficient compression
- **Delta Lake:** ACID transactions on data lakes

**Storage Location:**
- AWS S3
- Azure Blob Storage
- Google Cloud Storage

## Data Flow

### Real-time Data Ingestion

```
Market Data Source → API Gateway → Market Data Service → Redis → TimescaleDB
```

### Historical Data Processing

```
Data Source → Ingestion Pipeline → Processing → TimescaleDB → Archival Storage
```

### Query Flow

```
Application → API Gateway → Service → Redis (cache miss) → Database → Redis (cache)
```

## Data Models

### Market Data

```typescript
interface MarketData {
  timestamp: Date;
  symbol: string;
  price: number;
  volume: number;
  bid: number;
  ask: number;
}
```

### Portfolio

```typescript
interface Portfolio {
  id: string;
  userId: string;
  name: string;
  holdings: Holding[];
  totalValue: number;
  performance: Performance;
}

interface Holding {
  symbol: string;
  quantity: number;
  avgCost: number;
  currentPrice: number;
  currentValue: number;
  pnl: number;
  pnlPercent: number;
}
```

### Order

```typescript
interface Order {
  id: string;
  userId: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop';
  quantity: number;
  price?: number;
  status: 'pending' | 'filled' | 'cancelled' | 'rejected';
  createdAt: Date;
  filledAt?: Date;
}
```

## Data Retention

### Retention Policies

- **Real-time data:** 30 days in Redis
- **Market data:** 5 years in TimescaleDB
- **Order history:** 7 years in PostgreSQL (regulatory requirement)
- **Archival data:** Indefinite in object storage

### Data Archival

Automated archival process:
1. Data older than retention period is identified
2. Data is exported to Parquet format
3. Data is uploaded to object storage
4. Database records are deleted
5. Metadata is retained for retrieval

## Performance Optimization

### Indexing Strategy

- **Primary indexes:** On frequently queried columns
- **Composite indexes:** On multi-column queries
- **Partial indexes:** On filtered data
- **GIN indexes:** For JSON data

### Query Optimization

- Use appropriate indexes
- Limit result sets
- Use connection pooling
- Implement query caching
- Optimize JOIN operations

### Caching Strategy

- Cache frequently accessed data
- Use appropriate TTL values
- Implement cache invalidation
- Monitor cache hit rates

## Data Security

### Encryption

- **At rest:** AES-256 encryption
- **In transit:** TLS 1.3
- **Key management:** AWS KMS or equivalent

### Access Control

- Role-based access control (RBAC)
- Least privilege principle
- Audit logging
- Regular access reviews

### Backup Strategy

- **Daily backups:** Full database backups
- **Incremental backups:** Every 6 hours
- **Point-in-time recovery:** 7-day retention
- **Cross-region replication:** For disaster recovery

## Monitoring

### Metrics

- Database connection pool usage
- Query latency
- Cache hit rates
- Storage utilization
- Backup status

### Alerts

- High query latency
- Low cache hit rates
- Storage capacity warnings
- Backup failures
- Replication lag

## Best Practices

1. **Use appropriate data types** for optimal storage and performance
2. **Implement proper indexing** for frequently queried data
3. **Use connection pooling** to manage database connections
4. **Implement caching** to reduce database load
5. **Monitor performance** and optimize queries regularly
6. **Backup regularly** and test restore procedures
7. **Use transactions** for data consistency
8. **Implement data validation** at the application layer
9. **Document data models** and relationships
10. **Plan for scalability** from the beginning

## Migration

### Schema Migrations

Use version-controlled migration scripts:

```sql
-- migrations/001_create_users_table.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Data Migration

For large-scale data migrations:
1. Plan the migration strategy
2. Test with a subset of data
3. Use batch processing
4. Monitor performance
5. Have rollback plan ready

## Resources

- [TimescaleDB Documentation](https://docs.timescale.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/docs/)
- [Parquet Documentation](https://parquet.apache.org/)
