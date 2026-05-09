"""
Database Models - Financial Master
===================================
SQLAlchemy ORM models for data persistence

Models:
- User: Platform users
- Portfolio: User portfolios
- Position: Stock/asset positions
- Transaction: Trading transactions
- Order: Trading orders
- Watchlist: User watchlists
- Alert: Price/risk alerts
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()


class OrderStatus(PyEnum):
    PENDING = "pending"
    FILLED = "filled"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class OrderType(PyEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Portfolio(Base):
    """User portfolio model"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    cash_balance = Column(DECIMAL(12, 2), default=0.0)
    total_value = Column(DECIMAL(12, 2), default=0.0)
    day_pnl = Column(DECIMAL(12, 2), default=0.0)
    total_pnl = Column(DECIMAL(12, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Portfolio {self.name}>"


class Position(Base):
    """Stock/asset position model"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    quantity = Column(DECIMAL(12, 4), default=0.0)
    avg_cost = Column(DECIMAL(12, 4), default=0.0)
    current_price = Column(DECIMAL(12, 4))
    market_value = Column(DECIMAL(12, 2), default=0.0)
    unrealized_pnl = Column(DECIMAL(12, 2), default=0.0)
    unrealized_pnl_pct = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")
    transactions = relationship("Transaction", back_populates="position", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Position {self.symbol} x{self.quantity}>"


class Transaction(Base):
    """Trading transaction (buy/sell) model"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    position_id = Column(Integer, ForeignKey("positions.id"), index=True)
    symbol = Column(String(20), nullable=False, index=True)
    transaction_type = Column(String(10), nullable=False)  # buy, sell, dividend, etc
    quantity = Column(DECIMAL(12, 4), default=0.0)
    price = Column(DECIMAL(12, 4))
    amount = Column(DECIMAL(12, 2))
    commission = Column(DECIMAL(10, 2), default=0.0)
    notes = Column(Text)
    transaction_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    position = relationship("Position", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction {self.symbol} {self.transaction_type} x{self.quantity}>"


class Order(Base):
    """Trading order model"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    order_type = Column(Enum(OrderType), nullable=False)
    order_status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(DECIMAL(12, 4), nullable=False)
    price = Column(DECIMAL(12, 4))
    stop_price = Column(DECIMAL(12, 4))
    filled_quantity = Column(DECIMAL(12, 4), default=0.0)
    avg_filled_price = Column(DECIMAL(12, 4))
    time_in_force = Column(String(20), default="day")
    external_order_id = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    filled_at = Column(DateTime)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="orders")
    
    def __repr__(self):
        return f"<Order {self.symbol} {self.side} x{self.quantity}>"


class Watchlist(Base):
    """User watchlist model"""
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    symbols = Column(Text)  # JSON array of symbols
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="watchlists")
    
    def __repr__(self):
        return f"<Watchlist {self.name}>"


class Alert(Base):
    """Price/risk alert model"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # price_high, price_low, pnl, etc
    target_value = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    triggered_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert {self.symbol} {self.alert_type}>"
