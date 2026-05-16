"""
Database Session Management
============================
SQLAlchemy session and connection management
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from typing import Generator
import logging

from app.database.models import Base
from app.config.settings import get_db_url, is_testing

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database engine and session factory"""
        db_url = get_db_url()
        logger.info(f"Initializing database: {db_url.split('://')[0]}")
        
        # Configure engine based on database type
        if is_testing() or "sqlite" in db_url:
            # Use StaticPool for SQLite and testing
            self.engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            # Use QueuePool for production databases
            self.engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                echo=False
            )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables
        self._create_tables()
        logger.info("✓ Database initialized")
    
    def _create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.debug("Database tables created/verified")
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
    
    def reset(self):
        """Drop and recreate all tables (for testing)"""
        if is_testing():
            Base.metadata.drop_all(bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
            logger.warning("Database tables reset (testing only)")
        else:
            raise RuntimeError("Cannot reset database outside of testing")


# Global database manager instance
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get or initialize database manager"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get session"""
    db = get_db_manager().get_session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database"""
    get_db_manager()


def close_db():
    """Close database"""
    if _db_manager:
        _db_manager.close()
