"""
MFApi.in wrapper for fetching mutual fund NAV data.

Usage:
    from tools.mfapi import get_mf_nav, get_mf_historical_nav

    # Get latest NAV
    nav = get_mf_nav("119551")  # scheme code

    # Get historical NAV for calculating day change
    history = get_mf_historical_nav("119551", days=2)
"""

import time
from datetime import datetime, timedelta
from typing import Optional
import requests

from storage.cache import get_cached, set_cached


# Base URL for MFApi.in
MFAPI_BASE_URL = "https://api.mfapi.in"

# Track last request time for rate limiting
_last_request_time: float = 0
RATE_LIMIT_DELAY = 0.5  # 500ms between requests


def _rate_limit():
    """Ensure we don't hit MFApi too fast."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - elapsed)
    _last_request_time = time.time()


def get_mf_nav(scheme_code: str, force_refresh: bool = False) -> Optional[dict]:
    """
    Get latest NAV for a mutual fund scheme.

    Args:
        scheme_code: MF scheme code (e.g., "119551" for Parag Parikh Flexi Cap)
        force_refresh: If True, bypass cache and fetch fresh data

    Returns:
        Dict with:
            - scheme_code: str
            - scheme_name: str
            - nav: float (latest NAV)
            - date: str (NAV date)
            - fund_house: str
    """
    cache_key = f"nav_{scheme_code}"

    # Check cache first (cache for 1 hour for NAV data)
    if not force_refresh:
        cached = get_cached("mf_nav", cache_key, max_age_minutes=60)
        if cached:
            return cached

    _rate_limit()

    url = f"{MFAPI_BASE_URL}/mf/{scheme_code}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "SUCCESS":
            print(f"MFApi error for scheme {scheme_code}: {data.get('status')}")
            return None

        # Get latest NAV from the data array
        nav_data = data.get("data")
        if not nav_data or len(nav_data) == 0:
            return None

        latest = nav_data[0]  # First entry is the latest

        result = {
            "scheme_code": scheme_code,
            "scheme_name": data.get("meta", {}).get("scheme_name", ""),
            "fund_house": data.get("meta", {}).get("fund_house", ""),
            "nav": float(latest.get("nav", 0)),
            "date": latest.get("date", ""),
        }

        # Cache the result
        set_cached("mf_nav", cache_key, result)

        return result

    except requests.RequestException as e:
        print(f"Error fetching MF NAV for {scheme_code}: {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error parsing MF NAV data for {scheme_code}: {e}")
        return None


def get_mf_historical_nav(
    scheme_code: str,
    days: int = 2,
    force_refresh: bool = False
) -> Optional[list[dict]]:
    """
    Get historical NAV data for calculating day changes.

    Args:
        scheme_code: MF scheme code
        days: Number of recent days to fetch (default 2 for today and yesterday)
        force_refresh: If True, bypass cache

    Returns:
        List of NAV entries (newest first), each with:
            - nav: float
            - date: str (DD-MM-YYYY format)
    """
    cache_key = f"history_{scheme_code}_{days}"

    # Check cache (cache for 1 hour)
    if not force_refresh:
        cached = get_cached("mf_history", cache_key, max_age_minutes=60)
        if cached:
            return cached

    _rate_limit()

    url = f"{MFAPI_BASE_URL}/mf/{scheme_code}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "SUCCESS":
            return None

        nav_data = data.get("data", [])
        if not nav_data:
            return None

        # Get the most recent 'days' entries
        result = []
        for entry in nav_data[:days]:
            result.append({
                "nav": float(entry.get("nav", 0)),
                "date": entry.get("date", ""),
            })

        # Cache the result
        set_cached("mf_history", cache_key, result)

        return result

    except requests.RequestException as e:
        print(f"Error fetching MF historical NAV for {scheme_code}: {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error parsing MF historical data for {scheme_code}: {e}")
        return None


def get_mf_day_change(scheme_code: str) -> Optional[dict]:
    """
    Calculate today's NAV change for a mutual fund.

    Args:
        scheme_code: MF scheme code

    Returns:
        Dict with:
            - current_nav: float
            - previous_nav: float
            - change: float (absolute change)
            - change_percent: float
            - date: str (current NAV date)
    """
    history = get_mf_historical_nav(scheme_code, days=2)

    if not history or len(history) < 2:
        return None

    current = history[0]
    previous = history[1]

    current_nav = current["nav"]
    previous_nav = previous["nav"]

    change = current_nav - previous_nav
    change_percent = (change / previous_nav * 100) if previous_nav > 0 else 0

    return {
        "current_nav": current_nav,
        "previous_nav": previous_nav,
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "date": current["date"],
    }


def search_mf(query: str) -> Optional[list[dict]]:
    """
    Search for mutual funds by name.
    Note: MFApi.in doesn't provide a search endpoint,
    so this would need to be implemented using mf_instruments data.

    For now, returns None. Can be enhanced later if needed.
    """
    # TODO: Implement search using cached instruments list
    return None
