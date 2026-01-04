"""
Mutual fund data models.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MutualFundNAV(BaseModel):
    """Basic NAV data from AMFI."""
    scheme_code: str
    scheme_name: str
    nav: float
    date: datetime
    fund_house: str
    scheme_type: Optional[str] = None
    scheme_category: Optional[str] = None


class MutualFundDetails(BaseModel):
    """Detailed mutual fund information."""
    scheme_code: str
    scheme_name: str
    fund_house: str
    
    # Basic info
    category: Optional[str] = None  # Equity, Debt, Hybrid, etc.
    sub_category: Optional[str] = None  # Large Cap, Flexi Cap, etc.
    aum: Optional[float] = None  # Assets Under Management (in crores)
    expense_ratio: Optional[float] = None
    
    # Performance (returns in %)
    return_1y: Optional[float] = None
    return_3y: Optional[float] = None  # Annualized
    return_5y: Optional[float] = None  # Annualized
    
    # Category average for comparison
    category_return_1y: Optional[float] = None
    category_return_3y: Optional[float] = None
    category_return_5y: Optional[float] = None
    
    # Fund manager
    fund_manager: Optional[str] = None
    fund_manager_since: Optional[str] = None
    
    # Holdings
    top_holdings: Optional[list[dict]] = None  # [{name, percentage}]
    sector_allocation: Optional[dict] = None  # {sector: percentage}
    
    # Allocation
    large_cap_pct: Optional[float] = None
    mid_cap_pct: Optional[float] = None
    small_cap_pct: Optional[float] = None
    
    # Metadata
    fetched_at: datetime
    source: str = "amfi/screener"


class MutualFundAnalysis(BaseModel):
    """Combined analysis result for a mutual fund."""
    nav: Optional[MutualFundNAV] = None
    details: Optional[MutualFundDetails] = None
    news: Optional[list[dict]] = None
