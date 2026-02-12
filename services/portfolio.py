"""
Portfolio service for fetching and analyzing holdings.

Usage:
    from services.portfolio import get_portfolio

    portfolio = get_portfolio()
"""

from datetime import datetime, timezone
from typing import Optional
from collections import defaultdict

from tools.kite import get_holdings as get_kite_holdings, get_mf_holdings
from tools.groww import get_holdings as get_groww_holdings
from tools.screener import get_stock_fundamentals
from tools.mfapi import get_mf_day_change
from tools.mf_isin_mapper import get_scheme_code_from_fund_name
from models.portfolio import (
    Holding,
    MFHolding,
    Portfolio,
    PortfolioSummary,
    AllocationBreakdown,
)


def _enrich_holding(raw: dict, broker: str) -> Holding:
    """Convert raw broker holding to enriched Holding model."""
    symbol = raw.get("tradingsymbol", "") or raw.get("trading_symbol", "")
    quantity = raw.get("quantity", 0)
    avg_price = raw.get("average_price", 0)
    current_price = raw.get("last_price", 0)

    value = quantity * current_price
    invested = quantity * avg_price
    pnl = raw.get("pnl", value - invested)
    pnl_percent = (pnl / invested * 100) if invested > 0 else 0

    # Get market cap from Screener (cached)
    market_cap_category = None
    try:
        fundamentals = get_stock_fundamentals(symbol)
        if fundamentals:
            market_cap_category = fundamentals.market_cap_category
        else:
            print(f"[{broker}] No fundamentals found for {symbol}")
    except Exception as e:
        print(f"[{broker}] Failed to fetch market cap for {symbol}: {e}")

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
        market_cap_category=market_cap_category,
        broker=broker,
    )


def _parse_mf_market_cap(scheme_name: str) -> str:
    """
    Parse market cap category from mutual fund scheme name.

    Returns: 'Large Cap', 'Mid Cap', 'Small Cap', or 'Multi Cap'
    Defaults to 'Multi Cap' for ELSS and other uncategorized funds.
    """
    name_upper = scheme_name.upper()

    # Check for specific categories first (order matters)
    if "SMALL CAP" in name_upper or "SMALLCAP" in name_upper:
        return "Small Cap"
    if "MID CAP" in name_upper or "MIDCAP" in name_upper:
        # Check if it's "Large and Mid Cap" type
        if "LARGE" in name_upper:
            return "Multi Cap"
        return "Mid Cap"
    if "LARGE CAP" in name_upper or "LARGECAP" in name_upper:
        # Check if combined with mid cap
        if "MID" in name_upper:
            return "Multi Cap"
        return "Large Cap"

    # Default to Multi Cap (ELSS, Flexi Cap, uncategorized funds)
    return "Multi Cap"


def _process_mf_holding(raw: dict, broker: str) -> MFHolding:
    """Convert raw Kite MF holding to MFHolding model with day change data."""
    units = raw.get("quantity", 0)
    avg_nav = raw.get("average_price", 0)
    current_nav = raw.get("last_price", 0)

    value = units * current_nav
    invested = units * avg_nav
    # Always calculate P&L from value - invested (don't trust raw pnl for MF)
    pnl = value - invested
    pnl_percent = (pnl / invested * 100) if invested > 0 else 0

    scheme_name = raw.get("fund", raw.get("tradingsymbol", ""))
    market_cap_category = _parse_mf_market_cap(scheme_name)

    # Try to get day change from MFApi.in using fund name search
    isin = raw.get("tradingsymbol", "")
    day_change = 0.0
    day_change_percent = 0.0

    if scheme_name:
        try:
            # Search for scheme code using fund name
            scheme_code = get_scheme_code_from_fund_name(scheme_name)
            if scheme_code:
                mf_change = get_mf_day_change(scheme_code)
                if mf_change:
                    # Day change in portfolio value (change per unit * total units)
                    day_change = mf_change["change"] * units
                    day_change_percent = mf_change["change_percent"]
        except Exception as e:
            # Silently fail - day change is optional enhancement
            print(f"Could not fetch day change for MF {scheme_name}: {e}")

    return MFHolding(
        scheme_code=isin,  # Store ISIN as scheme_code for display
        scheme_name=scheme_name,
        fund_house=None,
        folio=raw.get("folio"),
        units=units,
        avg_nav=avg_nav,
        current_nav=current_nav,
        value=round(value, 2),
        invested=round(invested, 2),
        pnl=round(pnl, 2),
        pnl_percent=round(pnl_percent, 2),
        day_change=round(day_change, 2),
        day_change_percent=round(day_change_percent, 2),
        market_cap_category=market_cap_category,
        broker=broker,
    )


def _calculate_allocation(
    holdings: list[Holding],
    mf_holdings: list[MFHolding],
    stocks_value: float,
    mf_value: float,
) -> AllocationBreakdown:
    """Calculate market cap and asset type allocations."""
    total = stocks_value + mf_value

    # Market cap allocation (stocks + mutual funds)
    mcap_values: dict[str, float] = defaultdict(float)

    # Add stock holdings
    for h in holdings:
        mcap = h.market_cap_category or "Unknown"
        mcap_values[mcap] += h.value

    # Add mutual fund holdings
    for mf in mf_holdings:
        mcap = mf.market_cap_category or "Unknown"
        mcap_values[mcap] += mf.value

    # Filter out "Unknown" category and recalculate percentages
    mcap_values_filtered = {k: v for k, v in mcap_values.items() if k != "Unknown"}
    total_filtered = sum(mcap_values_filtered.values())

    mcap_pct = {
        k: round(v / total_filtered * 100, 2) if total_filtered > 0 else 0
        for k, v in mcap_values_filtered.items()
    }

    # Asset type allocation
    asset_pct = {}
    if total > 0:
        asset_pct["Stocks"] = round(stocks_value / total * 100, 2)
        asset_pct["Mutual Funds"] = round(mf_value / total * 100, 2)

    return AllocationBreakdown(
        market_cap=mcap_pct,
        asset_type=asset_pct,
    )


def get_portfolio(user_id: Optional[int] = None) -> Optional[Portfolio]:
    """
    Fetch and analyze complete portfolio from all connected brokers (Kite, Groww).

    Args:
        user_id: User ID to fetch portfolio for. If provided, uses database-stored tokens.

    Returns Portfolio with holdings, MF holdings, and allocations from all brokers.
    """
    # Fetch raw data from Kite
    raw_kite_holdings = get_kite_holdings(user_id=user_id)
    raw_mf = get_mf_holdings(user_id=user_id)  # Only from Kite for now

    # Build price map from Kite holdings to reuse for Groww (avoids redundant API calls)
    price_map = {}
    if raw_kite_holdings:
        for h in raw_kite_holdings:
            symbol = h.get('tradingsymbol', '')
            last_price = h.get('last_price', 0)
            if symbol and last_price:
                price_map[symbol] = last_price

    # Fetch raw data from Groww with price map
    raw_groww_holdings = get_groww_holdings(user_id=user_id, price_map=price_map)

    # Combine all holdings
    all_raw_holdings = []
    if raw_kite_holdings:
        all_raw_holdings.extend([(h, "kite") for h in raw_kite_holdings])
    if raw_groww_holdings:
        all_raw_holdings.extend([(h, "groww") for h in raw_groww_holdings])

    if not all_raw_holdings and not raw_mf:
        return None

    # Calculate total values for summary and allocation
    stocks_value = sum(
        h.get("quantity", 0) * h.get("last_price", 0)
        for h, _ in all_raw_holdings
    )
    mf_value = sum(
        m.get("quantity", 0) * m.get("last_price", 0)
        for m in (raw_mf or [])
    )
    total_value = stocks_value + mf_value

    # Process holdings with broker information
    holdings = [_enrich_holding(h, broker) for h, broker in all_raw_holdings]
    mf_holdings = [_process_mf_holding(m, "kite") for m in (raw_mf or [])]

    # Calculate totals
    stocks_invested = sum(h.invested for h in holdings)
    mf_invested = sum(m.invested for m in mf_holdings)
    total_invested = stocks_invested + mf_invested

    stocks_pnl = sum(h.pnl for h in holdings)
    mf_pnl = sum(m.pnl for m in mf_holdings)
    total_pnl = stocks_pnl + mf_pnl
    total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    stocks_day_change = sum(h.day_change * h.quantity for h in holdings)
    mf_day_change = sum(m.day_change for m in mf_holdings)
    day_pnl = stocks_day_change + mf_day_change
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
        stocks_invested=round(stocks_invested, 2),
        mf_invested=round(mf_invested, 2),
        stocks_pnl=round(stocks_pnl, 2),
        mf_pnl=round(mf_pnl, 2),
        stocks_day_change=round(stocks_day_change, 2),
        mf_day_change=round(mf_day_change, 2),
        holdings_count=len(holdings),
        mf_count=len(mf_holdings),
    )

    allocation = _calculate_allocation(holdings, mf_holdings, stocks_value, mf_value)

    return Portfolio(
        summary=summary,
        holdings=holdings,
        mf_holdings=mf_holdings,
        allocation=allocation,
        fetched_at=datetime.now(timezone.utc),
    )


def get_holdings_only(user_id: Optional[int] = None) -> list[Holding]:
    """Get stock holdings from all brokers without MF data (faster)."""
    # Fetch from Kite first
    raw_kite_holdings = get_kite_holdings(user_id=user_id)

    # Build price map from Kite holdings
    price_map = {}
    if raw_kite_holdings:
        for h in raw_kite_holdings:
            symbol = h.get('tradingsymbol', '')
            last_price = h.get('last_price', 0)
            if symbol and last_price:
                price_map[symbol] = last_price

    # Fetch from Groww with price map
    raw_groww_holdings = get_groww_holdings(user_id=user_id, price_map=price_map)

    holdings = []
    if raw_kite_holdings:
        holdings.extend([_enrich_holding(h, "kite") for h in raw_kite_holdings])
    if raw_groww_holdings:
        holdings.extend([_enrich_holding(h, "groww") for h in raw_groww_holdings])

    return holdings


def get_mf_only(user_id: Optional[int] = None) -> list[MFHolding]:
    """Get mutual fund holdings only."""
    raw_mf = get_mf_holdings(user_id=user_id)
    if not raw_mf:
        return []

    return [_process_mf_holding(m) for m in raw_mf]
