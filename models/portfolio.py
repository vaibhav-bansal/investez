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
    current_price: float
    value: float  # quantity * current_price
    invested: float  # quantity * avg_price
    pnl: float  # value - invested
    pnl_percent: float
    day_change: float
    day_change_percent: float
    weight: float  # % of total portfolio
    sector: Optional[str] = None
    market_cap_category: Optional[str] = None


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
    weight: float


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
    holdings_count: int
    mf_count: int


class AllocationBreakdown(BaseModel):
    """Allocation breakdown for charts."""
    sector: dict[str, float]  # sector_name -> percentage
    market_cap: dict[str, float]  # Large/Mid/Small -> percentage
    asset_type: dict[str, float]  # Stocks/MF -> percentage


class Portfolio(BaseModel):
    """Complete portfolio with all holdings and analysis."""
    summary: PortfolioSummary
    holdings: list[Holding]
    mf_holdings: list[MFHolding]
    allocation: AllocationBreakdown
    fetched_at: datetime
