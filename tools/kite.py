"""
Zerodha Kite Connect wrapper for price data.

Usage:
    from tools.kite import get_quote, get_price_history, authenticate

    # First time or when token expires
    authenticate()

    # Get current price
    quote = get_quote("RELIANCE")

    # Get historical data
    history = get_price_history("RELIANCE", "1Y")
"""

import os
import webbrowser
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from kiteconnect import KiteConnect

from config import KITE_API_KEY, KITE_API_SECRET, BASE_DIR
from models.stock import StockQuote, PriceHistory
from typing import Any


# Token storage file
TOKEN_FILE = BASE_DIR / ".kite_token"

# Global Kite instance
_kite: Optional[KiteConnect] = None


def _load_token() -> Optional[str]:
    """Load access token from file."""
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, "r") as f:
                data = f.read().strip().split("\n")
                if len(data) >= 2:
                    token = data[0]
                    expiry = datetime.fromisoformat(data[1])
                    # Token valid until 6 AM next day
                    if datetime.now() < expiry:
                        return token
        except (IOError, ValueError):
            pass
    return None


def _save_token(token: str) -> None:
    """Save access token to file with expiry."""
    # Kite tokens expire at 6 AM next day
    now = datetime.now()
    if now.hour >= 6:
        expiry = datetime(now.year, now.month, now.day, 6, 0, 0) + timedelta(days=1)
    else:
        expiry = datetime(now.year, now.month, now.day, 6, 0, 0)

    with open(TOKEN_FILE, "w") as f:
        f.write(f"{token}\n{expiry.isoformat()}")


def get_kite() -> Optional[KiteConnect]:
    """Get authenticated Kite instance."""
    global _kite

    if _kite is not None:
        return _kite

    if not KITE_API_KEY:
        print("Error: KITE_API_KEY not set in environment")
        return None

    _kite = KiteConnect(api_key=KITE_API_KEY)

    # Try to load existing token
    token = _load_token()
    if token:
        _kite.set_access_token(token)
        return _kite

    print("Kite access token not found or expired. Run authenticate() to login.")
    return None


def authenticate() -> bool:
    """
    Authenticate with Kite Connect.
    Opens browser for login, then prompts for request token.
    """
    global _kite

    if not KITE_API_KEY or not KITE_API_SECRET:
        print("Error: KITE_API_KEY and KITE_API_SECRET must be set")
        return False

    _kite = KiteConnect(api_key=KITE_API_KEY)
    login_url = _kite.login_url()

    print(f"\nOpening Kite login page in browser...")
    print(f"URL: {login_url}\n")
    webbrowser.open(login_url)

    print("After logging in, you'll be redirected to your redirect URL.")
    print("Copy the 'request_token' from the URL and paste it here.\n")

    request_token = input("Enter request_token: ").strip()

    if not request_token:
        print("No token provided.")
        return False

    try:
        data = _kite.generate_session(request_token, api_secret=KITE_API_SECRET)
        access_token = data["access_token"]
        _kite.set_access_token(access_token)
        _save_token(access_token)
        print("Authentication successful! Token saved.")
        return True
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False


def is_authenticated() -> bool:
    """Check if we have a valid Kite session."""
    kite = get_kite()
    if not kite:
        return False

    try:
        kite.profile()
        return True
    except Exception:
        return False


def get_quote(symbol: str, exchange: str = "NSE") -> Optional[StockQuote]:
    """
    Get current quote for a stock.

    Args:
        symbol: Stock symbol (e.g., "RELIANCE")
        exchange: Exchange (default "NSE")

    Returns:
        StockQuote object or None
    """
    kite = get_kite()
    if not kite:
        return None

    instrument = f"{exchange}:{symbol.upper()}"

    try:
        data = kite.quote([instrument])
        if instrument not in data:
            print(f"No data found for {instrument}")
            return None

        q = data[instrument]
        ohlc = q.get("ohlc", {})

        return StockQuote(
            symbol=symbol.upper(),
            name=symbol.upper(),  # Kite doesn't return name
            current_price=q.get("last_price", 0),
            change=q.get("net_change", 0),
            change_percent=(q.get("net_change", 0) / ohlc.get("close", 1)) * 100
                if ohlc.get("close") else 0,
            high_52w=ohlc.get("high"),  # Note: This is day high, not 52W
            low_52w=ohlc.get("low"),    # Note: This is day low, not 52W
            volume=q.get("volume"),
            timestamp=datetime.now()
        )
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return None


def get_price_history(
    symbol: str,
    period: str = "1Y",
    exchange: str = "NSE"
) -> Optional[PriceHistory]:
    """
    Get historical price data for return calculation.

    Args:
        symbol: Stock symbol
        period: "1M", "3M", "1Y", "3Y", "5Y"
        exchange: Exchange (default "NSE")

    Returns:
        PriceHistory object with return calculation
    """
    kite = get_kite()
    if not kite:
        return None

    # Calculate date range based on period
    end_date = datetime.now()
    period_map = {
        "1M": 30,
        "3M": 90,
        "1Y": 365,
        "3Y": 365 * 3,
        "5Y": 365 * 5,
    }

    days = period_map.get(period, 365)
    start_date = end_date - timedelta(days=days)

    # Determine interval based on period
    if period in ["1M", "3M"]:
        interval = "day"
    else:
        interval = "week"  # Use weekly for longer periods to reduce data

    instrument = f"{exchange}:{symbol.upper()}"

    try:
        # Get instrument token first
        instruments = kite.instruments(exchange)
        instrument_token = None
        for inst in instruments:
            if inst["tradingsymbol"] == symbol.upper():
                instrument_token = inst["instrument_token"]
                break

        if not instrument_token:
            print(f"Instrument token not found for {symbol}")
            return None

        data = kite.historical_data(
            instrument_token=instrument_token,
            from_date=start_date,
            to_date=end_date,
            interval=interval
        )

        if not data:
            return None

        start_price = data[0]["close"]
        end_price = data[-1]["close"]
        return_pct = ((end_price - start_price) / start_price) * 100

        high = max(d["high"] for d in data)
        low = min(d["low"] for d in data)

        return PriceHistory(
            symbol=symbol.upper(),
            period=period,
            start_date=data[0]["date"],
            end_date=data[-1]["date"],
            start_price=start_price,
            end_price=end_price,
            return_percent=round(return_pct, 2),
            high=high,
            low=low
        )
    except Exception as e:
        print(f"Error fetching history: {e}")
        return None


def get_multiple_price_history(
    symbol: str,
    exchange: str = "NSE"
) -> dict[str, PriceHistory]:
    """
    Get price history for all standard periods.

    Returns dict with keys: 1M, 3M, 1Y, 3Y, 5Y
    """
    periods = ["1M", "3M", "1Y", "3Y", "5Y"]
    results = {}

    for period in periods:
        history = get_price_history(symbol, period, exchange)
        if history:
            results[period] = history

    return results


def get_holdings() -> list[dict[str, Any]]:
    """
    Get user's stock holdings from Kite.

    Returns list of holdings with P&L data:
        - tradingsymbol, exchange, isin
        - quantity, average_price, last_price
        - pnl, day_change, day_change_percentage
    """
    kite = get_kite()
    if not kite:
        return []

    try:
        holdings = kite.holdings()
        return holdings if holdings else []
    except Exception as e:
        print(f"Error fetching holdings: {e}")
        return []


def get_positions() -> dict[str, list[dict[str, Any]]]:
    """
    Get user's current positions (net and day).

    Returns dict with 'net' and 'day' position lists.
    """
    kite = get_kite()
    if not kite:
        return {"net": [], "day": []}

    try:
        positions = kite.positions()
        return positions if positions else {"net": [], "day": []}
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return {"net": [], "day": []}


def get_mf_holdings() -> list[dict[str, Any]]:
    """
    Get user's mutual fund holdings from Kite.

    Returns list of MF holdings with:
        - tradingsymbol, folio, fund
        - quantity (units), average_price, last_price
        - pnl
    """
    kite = get_kite()
    if not kite:
        return []

    try:
        mf_holdings = kite.mf_holdings()
        return mf_holdings if mf_holdings else []
    except Exception as e:
        print(f"Error fetching MF holdings: {e}")
        return []


def get_mf_instruments() -> list[dict[str, Any]]:
    """
    Get list of available mutual fund instruments.

    Returns list of MF instruments with scheme details.
    """
    kite = get_kite()
    if not kite:
        return []

    try:
        instruments = kite.mf_instruments()
        return instruments if instruments else []
    except Exception as e:
        print(f"Error fetching MF instruments: {e}")
        return []
