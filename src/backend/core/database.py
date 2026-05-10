"""
Database Configuration and Session Management
Uses SQLAlchemy for ORM with Alembic for migrations
"""
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import inspect

logger = logging.getLogger(__name__)

# SQLAlchemy Base for all models
Base = declarative_base()

# Global database engine and session factory
_engine: AsyncEngine = None
_async_session_factory = None


async def init_db() -> None:
    """
    Initialize database connection and create tables
    Called on application startup
    """
    from src.backend.core.config import settings

    global _engine, _async_session_factory

    try:
        logger.info(f"🔌 Connecting to database: {settings.DATABASE_URL}")

        # Create async engine
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            future=True
        )

        # Create session factory
        _async_session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )

        # Check connection
        async with _engine.begin() as conn:
            # Create all tables from models
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Database initialized successfully")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}", exc_info=e)
        raise


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection
    Usage in FastAPI:
        async def my_endpoint(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_transaction():
    """
    Context manager for manual transaction control
    Usage:
        async with get_db_transaction() as session:
            ...
    """
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized")

    session = _async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def close_db() -> None:
    """Close database connection"""
    global _engine
    if _engine:
        await _engine.dispose()
        logger.info("✅ Database connection closed")


async def health_check() -> bool:
    """
    Check database connectivity
    Returns True if healthy, False otherwise
    """
    try:
        async with _engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def get_db_stats() -> dict:
    """Get database statistics"""
    if _engine is None:
        return {"status": "not initialized"}

    try:
        async with _engine.begin() as conn:
            tables = await conn.run_sync(
                lambda connection: inspect(connection).get_table_names()
            )
        return {
            "status": "connected",
            "tables": len(tables),
            "table_names": tables
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
