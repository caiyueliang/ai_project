from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Enum, ForeignKey, Text, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    premium = "premium"
    basic = "basic"

class BacktestStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class SignalType(str, enum.Enum):
    buy = "buy"
    sell = "sell"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.basic)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    backtests = relationship("Backtest", back_populates="user")

class Fund(Base):
    __tablename__ = "funds"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    fund_type = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    navs = relationship("FundNav", back_populates="fund")

class FundNav(Base):
    __tablename__ = "fund_navs"

    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("funds.id"), nullable=False)
    nav_date = Column(Date, nullable=False, index=True)
    nav = Column(Numeric(10, 4), nullable=False)
    accumulated_nav = Column(Numeric(10, 4))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    fund = relationship("Fund", back_populates="navs")

class Backtest(Base):
    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(String(36), unique=True, nullable=False)
    strategy_params = Column(JSON, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    fund_codes = Column(JSON, nullable=False)
    status = Column(Enum(BacktestStatus), default=BacktestStatus.pending, index=True)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="backtests")
    result = relationship("BacktestResult", back_populates="backtest", uselist=False)
    signals = relationship("TradeSignal", back_populates="backtest")

class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), unique=True, nullable=False)
    total_return = Column(Numeric(10, 4))
    annual_return = Column(Numeric(10, 4))
    max_drawdown = Column(Numeric(10, 4))
    sharpe_ratio = Column(Numeric(10, 4))
    win_rate = Column(Numeric(5, 2))
    profit_factor = Column(Numeric(10, 4))
    total_trades = Column(Integer)
    detail_metrics = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    backtest = relationship("Backtest", back_populates="result")

class TradeSignal(Base):
    __tablename__ = "trade_signals"

    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), nullable=False)
    signal_date = Column(Date, nullable=False, index=True)
    fund_code = Column(String(10), nullable=False)
    signal_type = Column(Enum(SignalType), nullable=False)
    price = Column(Numeric(10, 4), nullable=False)
    quantity = Column(Integer, nullable=False)
    portfolio_value = Column(Numeric(15, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    backtest = relationship("Backtest", back_populates="signals")
