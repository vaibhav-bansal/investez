"""
Screener.in scraper for fetching stock fundamentals.

Usage:
    from tools.screener import get_stock_fundamentals, get_peer_comparison

    fundamentals = get_stock_fundamentals("RELIANCE")
    peers = get_peer_comparison("RELIANCE")
"""

import re
import time
from datetime import datetime
from typing import Optional
import requests
from bs4 import BeautifulSoup

from config import SCREENER_BASE_URL, SCREENER_RATE_LIMIT_DELAY
from storage.cache import get_cached, set_cached
from models.stock import StockFundamentals


# Track last request time for rate limiting
_last_request_time: float = 0


def _rate_limit():
    """Ensure we don't hit Screener.in too fast."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < SCREENER_RATE_LIMIT_DELAY:
        time.sleep(SCREENER_RATE_LIMIT_DELAY - elapsed)
    _last_request_time = time.time()


def _get_page(symbol: str) -> Optional[BeautifulSoup]:
    """Fetch and parse a Screener.in company page."""
    _rate_limit()

    url = f"{SCREENER_BASE_URL}/company/{symbol}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def _parse_number(text: str) -> Optional[float]:
    """Parse a number from text, handling Indian number formats."""
    if not text:
        return None

    # Remove commas, whitespace, and common suffixes
    text = text.strip().replace(",", "").replace(" ", "")

    # Handle Cr (Crores) suffix
    multiplier = 1
    if text.endswith("Cr"):
        text = text[:-2]
    elif text.endswith("%"):
        text = text[:-1]

    try:
        return float(text)
    except ValueError:
        return None


def _extract_ratio(soup: BeautifulSoup, ratio_name: str) -> Optional[float]:
    """Extract a specific ratio from the ratios section."""
    # Look for the ratio in the top ratios section
    ratios_list = soup.select("#top-ratios li")
    for li in ratios_list:
        name_elem = li.select_one(".name")
        value_elem = li.select_one(".value, .number")
        if name_elem and value_elem:
            if ratio_name.lower() in name_elem.get_text().lower():
                return _parse_number(value_elem.get_text())
    return None


def _extract_from_table(soup: BeautifulSoup, label: str) -> Optional[float]:
    """Extract a value from any data table by label."""
    # Look in various table formats
    for row in soup.select("tr"):
        cells = row.select("td")
        if len(cells) >= 2:
            cell_text = cells[0].get_text().strip()
            if label.lower() in cell_text.lower():
                return _parse_number(cells[1].get_text())
    return None


def get_stock_fundamentals(
    symbol: str,
    force_refresh: bool = False
) -> Optional[StockFundamentals]:
    """
    Get stock fundamentals from Screener.in.

    Args:
        symbol: Stock symbol (e.g., "RELIANCE", "TCS")
        force_refresh: If True, bypass cache and fetch fresh data

    Returns:
        StockFundamentals object or None if fetch fails
    """
    symbol = symbol.upper().strip()
    cache_key = symbol

    # Check cache first
    if not force_refresh:
        cached = get_cached("fundamentals", cache_key)
        if cached:
            return StockFundamentals(**cached)

    # Fetch from Screener.in
    soup = _get_page(symbol)
    if not soup:
        return None

    # Extract company name
    name_elem = soup.select_one("h1.h2")
    name = name_elem.get_text().strip() if name_elem else symbol

    # Extract sector/industry from company info
    sector = None
    industry = None
    company_info = soup.select_one(".company-info")
    if company_info:
        info_text = company_info.get_text()
        # Sector info is usually in the company description

    # Market cap
    market_cap = _extract_ratio(soup, "Market Cap")
    market_cap_category = None
    if market_cap:
        if market_cap >= 20000:  # 20,000 Cr+
            market_cap_category = "Large Cap"
        elif market_cap >= 5000:  # 5,000 Cr+
            market_cap_category = "Mid Cap"
        else:
            market_cap_category = "Small Cap"

    # Valuation ratios
    pe_ratio = _extract_ratio(soup, "Stock P/E")
    pb_ratio = _extract_ratio(soup, "Book Value")
    if pb_ratio:
        # Screener shows book value, need to calculate P/B
        current_price = _extract_ratio(soup, "Current Price")
        if current_price and pb_ratio > 0:
            pb_ratio = round(current_price / pb_ratio, 2)
        else:
            pb_ratio = None

    # Profitability
    roe = _extract_ratio(soup, "ROE")
    roce = _extract_ratio(soup, "ROCE")

    # Financial health
    debt_to_equity = _extract_ratio(soup, "Debt to equity")

    # Dividend
    dividend_yield = _extract_ratio(soup, "Dividend Yield")

    # Shareholding - look in shareholding section
    promoter_holding = None
    shareholding_section = soup.select_one("#shareholding")
    if shareholding_section:
        for row in shareholding_section.select("tr"):
            cells = row.select("td")
            if cells and "Promoters" in row.get_text():
                # Get the most recent quarter's value (usually last cell)
                for cell in reversed(cells[1:]):
                    val = _parse_number(cell.get_text())
                    if val is not None:
                        promoter_holding = val
                        break

    # Extract industry PE from peers section if available
    industry_pe = None
    peers_section = soup.select_one("#peers")
    if peers_section:
        median_row = peers_section.select_one("tr.median")
        if median_row:
            cells = median_row.select("td")
            # PE is typically in a specific column
            for i, cell in enumerate(cells):
                if i > 0:  # Skip name column
                    val = _parse_number(cell.get_text())
                    if val and 0 < val < 1000:  # Reasonable PE range
                        industry_pe = val
                        break

    fundamentals = StockFundamentals(
        symbol=symbol,
        name=name,
        sector=sector,
        industry=industry,
        market_cap=market_cap,
        market_cap_category=market_cap_category,
        pe_ratio=pe_ratio,
        pb_ratio=pb_ratio,
        industry_pe=industry_pe,
        roe=roe,
        roce=roce,
        debt_to_equity=debt_to_equity,
        dividend_yield=dividend_yield,
        promoter_holding=promoter_holding,
        fetched_at=datetime.now(),
        source="screener.in"
    )

    # Cache the result
    set_cached("fundamentals", cache_key, fundamentals.model_dump(mode="json"))

    return fundamentals


def get_peer_comparison(symbol: str) -> Optional[list[dict]]:
    """
    Get peer comparison data for a stock.

    Returns list of peer dictionaries with basic metrics.
    """
    symbol = symbol.upper().strip()

    soup = _get_page(symbol)
    if not soup:
        return None

    peers_section = soup.select_one("#peers")
    if not peers_section:
        return None

    peers = []
    header_row = peers_section.select_one("thead tr")
    if not header_row:
        return None

    headers = [th.get_text().strip() for th in header_row.select("th")]

    for row in peers_section.select("tbody tr"):
        if "median" in row.get("class", []):
            continue  # Skip median row

        cells = row.select("td")
        if len(cells) < 2:
            continue

        peer = {}
        for i, cell in enumerate(cells):
            if i < len(headers):
                header = headers[i].lower().replace(" ", "_")
                text = cell.get_text().strip()
                # Try to parse as number
                num_val = _parse_number(text)
                peer[header] = num_val if num_val is not None else text

        if peer.get("name") or peer.get("s.no"):
            peers.append(peer)

    return peers[:10]  # Return top 10 peers


def search_stock(query: str) -> Optional[list[dict]]:
    """
    Search for stocks on Screener.in.

    Returns list of matching stocks with symbol and name.
    """
    _rate_limit()

    url = f"{SCREENER_BASE_URL}/api/company/search/"
    params = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()

        return [
            {"symbol": r.get("url", "").split("/")[-2], "name": r.get("name", "")}
            for r in results
            if r.get("url")
        ]
    except requests.RequestException as e:
        print(f"Error searching: {e}")
        return None
