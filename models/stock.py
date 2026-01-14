from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StockQuote(BaseModel):
    symbol: str
    name: str
    current_price: float
    change: float
    change_percent: float
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    volume: Optional[int] = None
    timestamp: datetime


class StockFundamentals(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None  # in crores
    market_cap_category: Optional[str] = None  # Large/Mid/Small Cap

    # Valuation ratios
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None

    # Industry averages for context
    industry_pe: Optional[float] = None
    industry_pb: Optional[float] = None

    # Profitability
    roe: Optional[float] = None  # Return on Equity %
    roce: Optional[float] = None  # Return on Capital Employed %

    # Financial health
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None

    # Growth (YoY)
    revenue_growth: Optional[float] = None
    profit_growth: Optional[float] = None

    # Dividends
    dividend_yield: Optional[float] = None

    # Ownership
    promoter_holding: Optional[float] = None
    fii_holding: Optional[float] = None
    dii_holding: Optional[float] = None

    # Metadata
    fetched_at: datetime
    source: str = "screener.in"


class PriceHistory(BaseModel):
    symbol: str
    period: str  # 1M, 3M, 1Y, 3Y, 5Y
    start_date: datetime
    end_date: datetime
    start_price: float
    end_price: float
    return_percent: float
    high: float
    low: float


class PeerComparison(BaseModel):
    symbol: str
    peers: list[dict]  # List of peer fundamentals


class StockAnalysis(BaseModel):
    """Combined analysis result for a stock"""
    quote: Optional[StockQuote] = None
    fundamentals: Optional[StockFundamentals] = None
    price_history: Optional[list[PriceHistory]] = None
    peers: Optional[list[dict]] = None
    news: Optional[list[dict]] = None
