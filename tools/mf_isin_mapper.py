"""
Fund name to MF Scheme Code mapper using MFApi.in search API.

Usage:
    from tools.mf_isin_mapper import get_scheme_code_from_fund_name

    scheme_code = get_scheme_code_from_fund_name("Parag Parikh Flexi Cap Fund")
"""

import time
from typing import Optional
import requests

from storage.cache import get_cached, set_cached


def get_scheme_code_from_fund_name(fund_name: str) -> Optional[str]:
    """
    Get MFApi scheme code from fund name using search API.

    Args:
        fund_name: Fund name (e.g., "Parag Parikh Flexi Cap Fund - Direct Plan")

    Returns:
        Scheme code as string (e.g., "122639") or None if not found
    """
    if not fund_name:
        return None

    # Check cache first (24 hours TTL)
    cache_key = f"search_{fund_name.lower()[:50]}"
    cached = get_cached("mf_nav", cache_key, max_age_minutes=24 * 60)
    if cached:
        return cached

    # Extract key terms from fund name for better search
    # Remove common suffixes that might not match exactly
    search_terms = fund_name.upper()
    for suffix in [" - DIRECT PLAN", " - DIRECT", " - REGULAR PLAN", " FUND"]:
        search_terms = search_terms.replace(suffix, "")

    # Use first few significant words (AMC name + fund type)
    words = search_terms.split()[:4]
    search_query = " ".join(words)

    url = "https://api.mfapi.in/mf/search"
    params = {"q": search_query}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()

        if not results or len(results) == 0:
            return None

        # Try to find best match
        # Prefer direct plans and growth options
        fund_upper = fund_name.upper()
        is_direct = "DIRECT" in fund_upper

        for result in results:
            scheme_name = result.get("schemeName", "").upper()
            scheme_code = str(result.get("schemeCode", ""))

            # Check if this is the right plan type (direct vs regular)
            if is_direct and "DIRECT" not in scheme_name:
                continue
            if not is_direct and "DIRECT" in scheme_name:
                continue

            # If name matches closely, return this scheme
            # Simple heuristic: check if key words from original name are in scheme name
            match_words = 0
            for word in words:
                if len(word) > 2 and word in scheme_name:
                    match_words += 1

            if match_words >= min(3, len(words)):
                # Cache and return
                set_cached("mf_nav", cache_key, scheme_code)
                return scheme_code

        # If no good match, return first result
        if results:
            first_scheme_code = str(results[0].get("schemeCode", ""))
            set_cached("mf_nav", cache_key, first_scheme_code)
            return first_scheme_code

        return None

    except Exception as e:
        print(f"Error searching for MF scheme '{fund_name}': {e}")
        return None
