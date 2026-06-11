from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database.db import Base


class Company(Base):
    __tablename__ = "companies"

    id          = Column(Integer, primary_key=True, index=True)
    ticker      = Column(String(20), unique=True, index=True, nullable=False)
    name        = Column(String(200), nullable=False)
    sector      = Column(String(100))
    yahoo_symbol = Column(String(30))   # e.g. PSO.KA
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())


class FinancialData(Base):
    __tablename__ = "financial_data"

    id          = Column(Integer, primary_key=True, index=True)
    ticker      = Column(String(20), index=True, nullable=False)
    fiscal_year = Column(Integer)

    # Income Statement
    revenue         = Column(Float)
    net_income      = Column(Float)
    ebit            = Column(Float)
    gross_profit    = Column(Float)

    # Balance Sheet
    total_assets        = Column(Float)
    total_liabilities   = Column(Float)
    total_equity        = Column(Float)
    current_assets      = Column(Float)
    current_liabilities = Column(Float)
    retained_earnings   = Column(Float)
    working_capital     = Column(Float)

    # Cash Flow
    operating_cash_flow = Column(Float)

    # Per Share
    eps     = Column(Float)
    bvps    = Column(Float)

    # Market
    market_cap  = Column(Float)
    market_price = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisCache(Base):
    __tablename__ = "analysis_cache"

    id          = Column(Integer, primary_key=True, index=True)
    ticker      = Column(String(20), index=True)
    fiscal_year = Column(Integer)
    result_json = Column(Text)   # full JSON blob of analysis result
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
