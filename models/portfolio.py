from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Holding(BaseModel):
    """Individual stock holding in portfolio."""
    symbol: str
    exchange: str
    isin: Optional[str] = None
    quantity: int
    avg_price: float
    current_price: Optional[float] = None  # From broker (Kite) or enrichment (Groww quotes)
    value: float  # quantity * current_price (or avg_price if current_price is None)
    invested: float  # quantity * avg_price
    pnl: Optional[float] = None  # value - invested (None if current_price is not available)
    pnl_percent: Optional[float] = None  # None if current_price is not available
    day_change: Optional[float] = None  # From broker (Kite) or enrichment (Groww quotes)
    day_change_percent: Optional[float] = None  # From broker (Kite) or enrichment (Groww quotes)
    market_cap_category: Optional[str] = None  # From enrichment (Screener)
    broker: str  # Which broker this holding is from (kite, groww, etc.)


class MFHolding(BaseModel):
    """Mutual fund holding in portfolio."""
    scheme_code: str
    scheme_name: str
    fund_house: Optional[str] = None
    folio: Optional[str] = None
    units: float
    avg_nav: float
    current_nav: float
    value: float
    invested: float
    pnl: float
    pnl_percent: float
    day_change: Optional[float] = None  # From enrichment (MFApi)
    day_change_percent: Optional[float] = None  # From enrichment (MFApi)
    market_cap_category: Optional[str] = None  # Parsed from scheme name
    broker: str


class PortfolioSummary(BaseModel):
    """Quick portfolio summary stats."""
    total_value: float
    total_invested: float
    total_pnl: float
    total_pnl_percent: float
    day_pnl: float
    day_pnl_percent: float
    stocks_value: float
    mf_value: float
    stocks_invested: float
    mf_invested: float
    stocks_pnl: float
    mf_pnl: float
    stocks_day_change: float
    mf_day_change: float
    holdings_count: int
    mf_count: int


class AllocationBreakdown(BaseModel):
    """Allocation breakdown for charts."""
    market_cap: dict[str, float]  # Large/Mid/Small/Multi Cap -> percentage
    asset_type: dict[str, float]  # Stocks/MF -> percentage


class Portfolio(BaseModel):
    """Complete portfolio with all holdings and analysis."""
    summary: PortfolioSummary
    holdings: list[Holding]
    mf_holdings: list[MFHolding]
    allocation: AllocationBreakdown
    fetched_at: datetime
