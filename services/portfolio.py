"""
Portfolio service for fetching and analyzing holdings.

Usage:
    from services.portfolio import get_portfolio

    portfolio = get_portfolio()
"""

from datetime import datetime
from typing import Optional
from collections import defaultdict

from tools.kite import get_holdings, get_mf_holdings
from tools.screener import get_stock_fundamentals
from models.portfolio import (
    Holding,
    MFHolding,
    Portfolio,
    PortfolioSummary,
    AllocationBreakdown,
)


def _enrich_holding(raw: dict, total_value: float) -> Holding:
    """Convert raw Kite holding to enriched Holding model."""
    symbol = raw.get("tradingsymbol", "")
    quantity = raw.get("quantity", 0)
    avg_price = raw.get("average_price", 0)
    current_price = raw.get("last_price", 0)

    value = quantity * current_price
    invested = quantity * avg_price
    pnl = raw.get("pnl", value - invested)
    pnl_percent = (pnl / invested * 100) if invested > 0 else 0
    weight = (value / total_value * 100) if total_value > 0 else 0

    # Get sector and market cap from Screener (cached)
    sector = None
    market_cap_category = None
    try:
        fundamentals = get_stock_fundamentals(symbol)
        if fundamentals:
            sector = fundamentals.sector
            market_cap_category = fundamentals.market_cap_category
    except Exception:
        pass

    return Holding(
        symbol=symbol,
        exchange=raw.get("exchange", "NSE"),
        isin=raw.get("isin"),
        quantity=quantity,
        avg_price=avg_price,
        current_price=current_price,
        value=round(value, 2),
        invested=round(invested, 2),
        pnl=round(pnl, 2),
        pnl_percent=round(pnl_percent, 2),
        day_change=raw.get("day_change", 0),
        day_change_percent=raw.get("day_change_percentage", 0),
        weight=round(weight, 2),
        sector=sector,
        market_cap_category=market_cap_category,
    )


def _process_mf_holding(raw: dict, total_value: float) -> MFHolding:
    """Convert raw Kite MF holding to MFHolding model."""
    units = raw.get("quantity", 0)
    avg_nav = raw.get("average_price", 0)
    current_nav = raw.get("last_price", 0)

    value = units * current_nav
    invested = units * avg_nav
    pnl = raw.get("pnl", value - invested)
    pnl_percent = (pnl / invested * 100) if invested > 0 else 0
    weight = (value / total_value * 100) if total_value > 0 else 0

    return MFHolding(
        scheme_code=raw.get("tradingsymbol", ""),
        scheme_name=raw.get("fund", raw.get("tradingsymbol", "")),
        fund_house=None,
        folio=raw.get("folio"),
        units=units,
        avg_nav=avg_nav,
        current_nav=current_nav,
        value=round(value, 2),
        invested=round(invested, 2),
        pnl=round(pnl, 2),
        pnl_percent=round(pnl_percent, 2),
        weight=round(weight, 2),
    )


def _calculate_allocation(
    holdings: list[Holding],
    mf_holdings: list[MFHolding],
    stocks_value: float,
    mf_value: float,
) -> AllocationBreakdown:
    """Calculate sector, market cap, and asset type allocations."""
    total = stocks_value + mf_value

    # Sector allocation (stocks only)
    sector_values: dict[str, float] = defaultdict(float)
    for h in holdings:
        sector = h.sector or "Unknown"
        sector_values[sector] += h.value

    sector_pct = {
        k: round(v / total * 100, 2) if total > 0 else 0
        for k, v in sector_values.items()
    }

    # Market cap allocation (stocks only)
    mcap_values: dict[str, float] = defaultdict(float)
    for h in holdings:
        mcap = h.market_cap_category or "Unknown"
        mcap_values[mcap] += h.value

    mcap_pct = {
        k: round(v / total * 100, 2) if total > 0 else 0
        for k, v in mcap_values.items()
    }

    # Asset type allocation
    asset_pct = {}
    if total > 0:
        asset_pct["Stocks"] = round(stocks_value / total * 100, 2)
        asset_pct["Mutual Funds"] = round(mf_value / total * 100, 2)

    return AllocationBreakdown(
        sector=sector_pct,
        market_cap=mcap_pct,
        asset_type=asset_pct,
    )


def get_portfolio() -> Optional[Portfolio]:
    """
    Fetch and analyze complete portfolio from Kite.

    Returns Portfolio with holdings, MF holdings, and allocations.
    """
    # Fetch raw data from Kite
    raw_holdings = get_holdings()
    raw_mf = get_mf_holdings()

    if not raw_holdings and not raw_mf:
        return None

    # Calculate total values first (for weight calculation)
    stocks_value = sum(
        h.get("quantity", 0) * h.get("last_price", 0)
        for h in raw_holdings
    )
    mf_value = sum(
        m.get("quantity", 0) * m.get("last_price", 0)
        for m in raw_mf
    )
    total_value = stocks_value + mf_value

    # Process holdings
    holdings = [_enrich_holding(h, total_value) for h in raw_holdings]
    mf_holdings = [_process_mf_holding(m, total_value) for m in raw_mf]

    # Calculate totals
    total_invested = sum(h.invested for h in holdings) + sum(m.invested for m in mf_holdings)
    total_pnl = sum(h.pnl for h in holdings) + sum(m.pnl for m in mf_holdings)
    total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    day_pnl = sum(h.day_change * h.quantity for h in holdings)
    day_pnl_percent = (day_pnl / total_value * 100) if total_value > 0 else 0

    summary = PortfolioSummary(
        total_value=round(total_value, 2),
        total_invested=round(total_invested, 2),
        total_pnl=round(total_pnl, 2),
        total_pnl_percent=round(total_pnl_percent, 2),
        day_pnl=round(day_pnl, 2),
        day_pnl_percent=round(day_pnl_percent, 2),
        stocks_value=round(stocks_value, 2),
        mf_value=round(mf_value, 2),
        holdings_count=len(holdings),
        mf_count=len(mf_holdings),
    )

    allocation = _calculate_allocation(holdings, mf_holdings, stocks_value, mf_value)

    return Portfolio(
        summary=summary,
        holdings=holdings,
        mf_holdings=mf_holdings,
        allocation=allocation,
        fetched_at=datetime.now(),
    )


def get_holdings_only() -> list[Holding]:
    """Get stock holdings without MF data (faster)."""
    raw_holdings = get_holdings()
    if not raw_holdings:
        return []

    total_value = sum(
        h.get("quantity", 0) * h.get("last_price", 0)
        for h in raw_holdings
    )

    return [_enrich_holding(h, total_value) for h in raw_holdings]


def get_mf_only() -> list[MFHolding]:
    """Get mutual fund holdings only."""
    raw_mf = get_mf_holdings()
    if not raw_mf:
        return []

    total_value = sum(
        m.get("quantity", 0) * m.get("last_price", 0)
        for m in raw_mf
    )

    return [_process_mf_holding(m, total_value) for m in raw_mf]
