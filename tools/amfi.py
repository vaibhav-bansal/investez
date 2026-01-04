"""
AMFI data fetcher for mutual fund NAV.

Fetches daily NAV data from AMFI (Association of Mutual Funds in India).
Data source: https://www.amfiindia.com/spages/NAVAll.txt
"""

import requests
from datetime import datetime
from typing import Optional

from models.mutual_fund import MutualFundNAV


# AMFI NAV data URL
AMFI_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

# Cache for NAV data (refreshed daily)
_nav_cache: dict[str, MutualFundNAV] = {}
_cache_date: Optional[str] = None


def _refresh_cache() -> bool:
    """Refresh the NAV cache from AMFI."""
    global _nav_cache, _cache_date
    
    today = datetime.now().strftime("%Y-%m-%d")
    if _cache_date == today and _nav_cache:
        return True
    
    try:
        response = requests.get(AMFI_NAV_URL, timeout=30)
        response.raise_for_status()
        
        _nav_cache = {}
        current_fund_house = ""
        current_scheme_type = ""
        
        lines = response.text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a fund house header
            if line.endswith("Mutual Fund"):
                current_fund_house = line
                continue
            
            # Check if this is a scheme type line (Open Ended, Close Ended, etc.)
            if line.startswith(("Open Ended", "Close Ended", "Interval Fund")):
                current_scheme_type = line
                continue
            
            # Parse NAV data line
            # Format: Scheme Code;ISIN Div Payout/ISIN Growth;ISIN Div Reinvestment;
            #         Scheme Name;Net Asset Value;Date
            parts = line.split(';')
            if len(parts) >= 5:
                try:
                    scheme_code = parts[0].strip()
                    scheme_name = parts[3].strip() if len(parts) > 3 else ""
                    nav_str = parts[4].strip() if len(parts) > 4 else ""
                    date_str = parts[5].strip() if len(parts) > 5 else ""
                    
                    if not scheme_code or not scheme_name or not nav_str:
                        continue
                    
                    # Skip N.A. entries
                    if nav_str.upper() == "N.A.":
                        continue
                    
                    nav_value = float(nav_str)
                    
                    # Parse date
                    try:
                        nav_date = datetime.strptime(date_str, "%d-%b-%Y")
                    except ValueError:
                        nav_date = datetime.now()
                    
                    fund_nav = MutualFundNAV(
                        scheme_code=scheme_code,
                        scheme_name=scheme_name,
                        nav=nav_value,
                        date=nav_date,
                        fund_house=current_fund_house,
                        scheme_type=current_scheme_type
                    )
                    
                    _nav_cache[scheme_code] = fund_nav
                    # Also index by lowercase name for search
                    _nav_cache[scheme_name.lower()] = fund_nav
                    
                except (ValueError, IndexError):
                    continue
        
        _cache_date = today
        return True
        
    except requests.RequestException as e:
        print(f"Error fetching AMFI data: {e}")
        return False


def get_nav(scheme_code: str) -> Optional[MutualFundNAV]:
    """
    Get NAV for a specific scheme by code.
    
    Args:
        scheme_code: AMFI scheme code
        
    Returns:
        MutualFundNAV object or None
    """
    _refresh_cache()
    return _nav_cache.get(scheme_code)


def search_funds(query: str, limit: int = 10) -> list[MutualFundNAV]:
    """
    Search for mutual funds by name.
    
    Args:
        query: Search query (partial name match)
        limit: Maximum results to return
        
    Returns:
        List of matching MutualFundNAV objects
    """
    _refresh_cache()
    
    query_lower = query.lower()
    results = []
    seen_codes = set()
    
    for key, fund in _nav_cache.items():
        if len(results) >= limit:
            break
        
        # Skip if already seen (we index by both code and name)
        if fund.scheme_code in seen_codes:
            continue
        
        if query_lower in fund.scheme_name.lower():
            results.append(fund)
            seen_codes.add(fund.scheme_code)
    
    return results


def get_fund_by_name(name: str) -> Optional[MutualFundNAV]:
    """
    Find a fund by exact or close name match.
    
    Args:
        name: Fund name to search for
        
    Returns:
        Best matching MutualFundNAV or None
    """
    results = search_funds(name, limit=5)
    
    if not results:
        return None
    
    # Try exact match first
    name_lower = name.lower()
    for fund in results:
        if fund.scheme_name.lower() == name_lower:
            return fund
    
    # Return first partial match
    return results[0]


def get_all_funds_by_house(fund_house: str) -> list[MutualFundNAV]:
    """
    Get all funds from a specific fund house.
    
    Args:
        fund_house: Fund house name (e.g., "PPFAS Mutual Fund")
        
    Returns:
        List of funds from that house
    """
    _refresh_cache()
    
    house_lower = fund_house.lower()
    results = []
    seen_codes = set()
    
    for fund in _nav_cache.values():
        if fund.scheme_code in seen_codes:
            continue
        
        if house_lower in fund.fund_house.lower():
            results.append(fund)
            seen_codes.add(fund.scheme_code)
    
    return results


def get_direct_plan(fund_name: str) -> Optional[MutualFundNAV]:
    """
    Find the Direct plan variant of a fund.
    
    Args:
        fund_name: Fund name (will append "Direct" if not present)
        
    Returns:
        Direct plan NAV or None
    """
    if "direct" not in fund_name.lower():
        fund_name = f"{fund_name} Direct"
    
    return get_fund_by_name(fund_name)
