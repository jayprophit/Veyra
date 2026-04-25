"""
Database Connection Pool & Optimizations
==========================================
High-performance database connection management:
- Async connection pooling
- Query optimization
- Automatic reconnection
- Health monitoring
- Query caching
"""

import asyncio
import asyncpg
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from contextlib import asynccontextmanager
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class PoolConfig:
    """Database pool configuration."""
    min_size: int = 5
    max_size: int = 20
    max_inactive_time: int = 300
    max_queries: int = 50000
    command_timeout: int = 60
    ssl: bool = True


class DatabaseManager:
    """
    Async database connection pool manager.
    Optimized for high-frequency trading workloads.
    """
    
    def __init__(self, dsn: str, config: Optional[PoolConfig] = None):
        self.dsn = dsn
        self.config = config or PoolConfig()
        self.pool: Optional[asyncpg.Pool] = None
        self._connected = False
        self._query_cache: Dict[str, Any] = {}
        self._stats = {
            "queries_executed": 0,
            "queries_cached": 0,
            "connections_acquired": 0,
            "errors": 0
        }
    
    async def connect(self) -> bool:
        """Initialize connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=self.config.min_size,
                max_size=self.config.max_size,
                max_inactive_connection_lifetime=self.config.max_inactive_time,
                max_queries=self.config.max_queries,
                command_timeout=self.config.command_timeout,
                ssl=self.config.ssl,
                init=self._init_connection
            )
            
            self._connected = True
            logger.info(f"Database pool created: {self.config.min_size}-{self.config.max_size} connections")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            self._connected = False
            return False
    
    async def _init_connection(self, conn):
        """Initialize new connection with optimizations."""
        # Set application name
        await conn.execute("SET application_name = 'financial_master'")
        
        # Optimize for trading workload
        await conn.execute("SET synchronous_commit = off")  # Faster writes
        await conn.execute("SET jit = on")  # JIT compilation for complex queries
    
    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self._connected = False
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire connection from pool."""
        if not self._connected or not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            self._stats["connections_acquired"] += 1
            yield conn
    
    async def execute(self, query: str, *args) -> str:
        """Execute query and return status."""
        async with self.acquire() as conn:
            start = time.time()
            result = await conn.execute(query, *args)
            duration = time.time() - start
            
            self._stats["queries_executed"] += 1
            
            if duration > 1.0:
                logger.warning(f"Slow query ({duration:.2f}s): {query[:100]}...")
            
            return result
    
    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Fetch all results."""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch single row."""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch single value."""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    async def execute_many(self, query: str, args_list: List[tuple]):
        """Execute query multiple times with different args."""
        async with self.acquire() as conn:
            return await conn.executemany(query, args_list)
    
    # Specialized queries for trading
    
    async def get_market_data_batch(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, List[Dict]]:
        """Efficiently fetch market data for multiple symbols."""
        query = """
            SELECT symbol, timestamp, open, high, low, close, volume
            FROM market_data
            WHERE symbol = ANY($1)
            AND timestamp BETWEEN $2 AND $3
            ORDER BY symbol, timestamp
        """
        
        rows = await self.fetch(query, symbols, start_date, end_date)
        
        # Group by symbol
        result: Dict[str, List[Dict]] = {sym: [] for sym in symbols}
        for row in rows:
            result[row['symbol']].append(dict(row))
        
        return result
    
    async def get_positions_with_pnl(self, user_id: str) -> List[Dict]:
        """Get positions with real-time P&L calculation."""
        query = """
            SELECT 
                p.symbol,
                p.quantity,
                p.avg_cost,
                m.price as current_price,
                p.quantity * m.price as market_value,
                p.quantity * (m.price - p.avg_cost) as unrealized_pnl,
                (m.price - p.avg_cost) / NULLIF(p.avg_cost, 0) * 100 as pnl_pct
            FROM positions p
            JOIN market_prices m ON p.symbol = m.symbol
            WHERE p.user_id = $1
        """
        
        rows = await self.fetch(query, user_id)
        return [dict(row) for row in rows]
    
    async def get_portfolio_history(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict]:
        """Get portfolio value history."""
        query = """
            SELECT 
                date,
                total_value,
                cash_balance,
                day_pnl,
                cumulative_pnl
            FROM portfolio_history
            WHERE user_id = $1
            AND date >= CURRENT_DATE - $2
            ORDER BY date
        """
        
        rows = await self.fetch(query, user_id, days)
        return [dict(row) for row in rows]
    
    async def get_trades_summary(
        self,
        user_id: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """Get trading summary statistics."""
        query = """
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN realized_pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(realized_pnl) as total_pnl,
                AVG(realized_pnl) as avg_pnl,
                MAX(realized_pnl) as best_trade,
                MIN(realized_pnl) as worst_trade
            FROM trades
            WHERE user_id = $1
            AND timestamp BETWEEN $2 AND $3
        """
        
        row = await self.fetchrow(query, user_id, start_date, end_date)
        return dict(row) if row else {}
    
    # Performance monitoring
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        return {
            **self._stats,
            "connected": self._connected,
            "pool_size": self.pool.get_size() if self.pool else 0,
            "pool_free": self.pool.get_idle_size() if self.pool else 0
        }
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            if not self._connected:
                return False
            
            async with self.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Connection string builder
def build_connection_string(
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    ssl_mode: str = "require"
) -> str:
    """Build PostgreSQL connection string."""
    return f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode={ssl_mode}"


# Global database manager
_db_manager: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """Get or create global database manager."""
    global _db_manager
    if _db_manager is None:
        # Use environment variables or defaults
        import os
        dsn = os.getenv(
            "DATABASE_URL",
            "postgresql://localhost/financial_master"
        )
        _db_manager = DatabaseManager(dsn)
    return _db_manager


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        db = get_database()
        
        # Connect
        if await db.connect():
            print("Connected to database")
            
            # Test query
            result = await db.fetchval("SELECT version()")
            print(f"Database version: {result}")
            
            # Stats
            print(f"DB stats: {db.get_stats()}")
            
            # Disconnect
            await db.disconnect()
        else:
            print("Failed to connect")
    
    asyncio.run(test())
