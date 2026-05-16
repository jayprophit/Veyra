"""
Comprehensive Test Suite - Database Tests
==========================================
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database.models import (
    Base, User, Portfolio, Position, Transaction, Order,
    OrderType, OrderStatus
)


@pytest.fixture
def db_engine():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """Create database session for testing"""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, db_session: Session):
        """Test user creation"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        retrieved_user = db_session.query(User).filter_by(username="testuser").first()
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.is_active is True
    
    def test_user_uniqueness(self, db_session: Session):
        """Test unique constraints on username and email"""
        user1 = User(username="test", email="test@example.com", password_hash="hash")
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(username="test", email="test2@example.com", password_hash="hash")
        db_session.add(user2)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
    
    def test_user_timestamps(self, db_session: Session):
        """Test created_at and updated_at timestamps"""
        user = User(username="test", email="test@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at <= user.updated_at


class TestPortfolioModel:
    """Test Portfolio model"""
    
    def test_create_portfolio(self, db_session: Session):
        """Test portfolio creation"""
        user = User(username="test", email="test@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        
        portfolio = Portfolio(
            user_id=user.id,
            name="Test Portfolio",
            cash_balance=Decimal("10000.00")
        )
        db_session.add(portfolio)
        db_session.commit()
        
        retrieved_portfolio = db_session.query(Portfolio).filter_by(name="Test Portfolio").first()
        assert retrieved_portfolio is not None
        assert retrieved_portfolio.user_id == user.id
    
    def test_portfolio_user_relationship(self, db_session: Session):
        """Test user-portfolio relationship"""
        user = User(username="test", email="test@example.com", password_hash="hash")
        portfolio = Portfolio(name="Portfolio 1")
        user.portfolios.append(portfolio)
        
        db_session.add(user)
        db_session.commit()
        
        retrieved_user = db_session.query(User).filter_by(username="test").first()
        assert len(retrieved_user.portfolios) == 1
        assert retrieved_user.portfolios[0].name == "Portfolio 1"


class TestPositionModel:
    """Test Position model"""
    
    def test_create_position(self, db_session: Session):
        """Test position creation"""
        user = User(username="test", email="test@example.com", password_hash="hash")
        portfolio = Portfolio(user=user, name="Portfolio")
        position = Position(
            portfolio=portfolio,
            symbol="AAPL",
            quantity=Decimal("100"),
            avg_cost=Decimal("150.00")
        )
        
        db_session.add(user)
        db_session.add(portfolio)
        db_session.add(position)
        db_session.commit()
        
        retrieved_position = db_session.query(Position).filter_by(symbol="AAPL").first()
        assert retrieved_position is not None
        assert retrieved_position.quantity == Decimal("100")


class TestTransactionModel:
    """Test Transaction model"""
    
    def test_create_transaction(self, db_session: Session):
        """Test transaction creation"""
        user = User(username="test", email="test@example.com", password_hash="hash")
        portfolio = Portfolio(user=user, name="Portfolio")
        transaction = Transaction(
            portfolio=portfolio,
            symbol="AAPL",
            transaction_type="buy",
            quantity=Decimal("100"),
            price=Decimal("150.00"),
            amount=Decimal("15000.00"),
            transaction_date=datetime.utcnow()
        )
        
        db_session.add(user)
        db_session.add(portfolio)
        db_session.add(transaction)
        db_session.commit()
        
        retrieved_transaction = db_session.query(Transaction).filter_by(symbol="AAPL").first()
        assert retrieved_transaction is not None
        assert retrieved_transaction.transaction_type == "buy"


class TestOrderModel:
    """Test Order model"""
    
    def test_create_order(self, db_session: Session):
        """Test order creation"""
        user = User(username="test", email="test@example.com", password_hash="hash")
        portfolio = Portfolio(user=user, name="Portfolio")
        order = Order(
            portfolio=portfolio,
            symbol="AAPL",
            order_type=OrderType.LIMIT,
            side="buy",
            quantity=Decimal("100"),
            price=Decimal("150.00")
        )
        
        db_session.add(user)
        db_session.add(portfolio)
        db_session.add(order)
        db_session.commit()
        
        retrieved_order = db_session.query(Order).filter_by(symbol="AAPL").first()
        assert retrieved_order is not None
        assert retrieved_order.order_status == OrderStatus.PENDING
    
    def test_order_status_update(self, db_session: Session):
        """Test order status updates"""
        user = User(username="test", email="test@example.com", password_hash="hash")
        portfolio = Portfolio(user=user, name="Portfolio")
        order = Order(
            portfolio=portfolio,
            symbol="AAPL",
            order_type=OrderType.MARKET,
            side="buy",
            quantity=Decimal("100")
        )
        
        db_session.add(user)
        db_session.add(portfolio)
        db_session.add(order)
        db_session.commit()
        
        order.order_status = OrderStatus.FILLED
        order.filled_quantity = Decimal("100")
        order.avg_filled_price = Decimal("150.00")
        order.filled_at = datetime.utcnow()
        db_session.commit()
        
        retrieved_order = db_session.query(Order).filter_by(id=order.id).first()
        assert retrieved_order.order_status == OrderStatus.FILLED
