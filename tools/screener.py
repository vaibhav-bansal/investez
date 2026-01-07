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

    # Remove rupee symbol (both ₹ and Rs.)
    text = text.replace("₹", "").replace("Rs.", "").replace("Rs", "")

    # Remove commas, whitespace, and common suffixes
    text = text.strip().replace(",", "").replace(" ", "")

    # Handle Cr (Crores) suffix - 1 Cr = 10,000,000
    # Handle both "Cr" and "Cr." variations
    multiplier = 1
    if text.endswith("Cr") or text.endswith("Cr."):
        # Remove "Cr" or "Cr." suffix
        if text.endswith("Cr."):
            text = text[:-3]
        else:
            text = text[:-2]
        multiplier = 10000000
    elif text.endswith("%"):
        text = text[:-1]

    # Extract first number from string (handles cases like "21,35,358Cr.")
    match = re.search(r'-?\d+\.?\d*', text)
    if not match:
        return None

    try:
        return float(match.group()) * multiplier
    except ValueError:
        return None


def _extract_ratio(soup: BeautifulSoup, ratio_name: str) -> Optional[float]:
    """Extract a specific ratio from the ratios section."""
    # Look for the ratio in the top ratios section
    ratios_list = soup.select("#top-ratios li")
    for li in ratios_list:
        name_elem = li.select_one(".name")
        if name_elem and ratio_name.lower() in name_elem.get_text().lower():
            # Try to get the number from the nested .number span first, then .value
            number_elem = li.select_one(".number")
            value_elem = li.select_one(".value")
            if number_elem:
                return _parse_number(number_elem.get_text())
            elif value_elem:
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
        # Try to find sector and industry patterns
        lines = info_text.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()
            if "Sector" in line or "sector" in line:
                if i + 1 < len(lines):
                    sector = lines[i + 1].strip()
            elif "Industry" in line or "industry" in line:
                if i + 1 < len(lines):
                    industry = lines[i + 1].strip()

    # Also try extracting from the page content
    if not sector:
        sector_elem = soup.select_one(".company-info a[href*='/sector/']")
        if sector_elem:
            sector = sector_elem.get_text().strip()
    if not industry:
        industry_elem = soup.select_one(".company-info a[href*='/industry/']")
        if industry_elem:
            industry = industry_elem.get_text().strip()

    # Market cap (in crores)
    market_cap = _extract_ratio(soup, "Market Cap")
    market_cap_category = None
    if market_cap:
        # market_cap is already in crores
        if market_cap >= 100000:  # 100,000 Cr+ (Large cap)
            market_cap_category = "Large Cap"
        elif market_cap >= 25000:  # 25,000 Cr+ (Mid cap)
            market_cap_category = "Mid Cap"
        else:
            market_cap_category = "Small Cap"

    # Get current price for P/B calculation
    current_price = _extract_ratio(soup, "Current Price")
    book_value = _extract_ratio(soup, "Book Value")

    # Valuation ratios
    pe_ratio = _extract_ratio(soup, "Stock P/E")

    # Calculate P/B from current price and book value
    pb_ratio = None
    if current_price and book_value and book_value > 0:
        pb_ratio = round(current_price / book_value, 2)

    ev_ebitda = _extract_ratio(soup, "EV/Ebitda")

    # Profitability
    roe = _extract_ratio(soup, "ROE")
    roce = _extract_ratio(soup, "ROCE")

    # Financial health
    debt_to_equity = _extract_ratio(soup, "Debt to equity")
    current_ratio = _extract_ratio(soup, "Current Ratio")

    # Dividend
    dividend_yield = _extract_ratio(soup, "Dividend Yield")

    # Shareholding - look in shareholding section
    promoter_holding = None
    fii_holding = None
    dii_holding = None
    shareholding_section = soup.select_one("#shareholding")
    if shareholding_section:
        for row in shareholding_section.select("tr"):
            cells = row.select("td")
            if not cells:
                continue
            row_text = row.get_text()
            if "Promoters" in row_text or "Promoter" in row_text:
                # Get the most recent quarter's value (usually last cell)
                for cell in reversed(cells[1:]):
                    val = _parse_number(cell.get_text())
                    if val is not None:
                        promoter_holding = val
                        break
            elif "FII" in row_text:
                for cell in reversed(cells[1:]):
                    val = _parse_number(cell.get_text())
                    if val is not None:
                        fii_holding = val
                        break
            elif ("DII" in row_text) or ("Domestic" in row_text):
                for cell in reversed(cells[1:]):
                    val = _parse_number(cell.get_text())
                    if val is not None:
                        dii_holding = val
                        break

    # Growth - look for sales and profit growth in the ratios/tables
    revenue_growth = _extract_ratio(soup, "Sales Growth") or _extract_ratio(soup, "Revenue Growth")
    profit_growth = _extract_ratio(soup, "Profit Growth") or _extract_ratio(soup, "PAT Growth")

    # If not found in top ratios, look in ranges-table for compounded growth
    # The structure is: <th>Compounded Sales Growth</th> followed by <table class="ranges-table">
    if revenue_growth is None or profit_growth is None:
        # Find all th elements containing "Growth" - these are the section headers
        growth_ths = soup.find_all("th", string=lambda t: t and "Growth" in t and "Compounded" in t)
        for th in growth_ths:
            th_text = th.get_text().strip()
            # Find the next ranges-table after this th
            next_table = th.find_next("table", class_="ranges-table")
            if next_table:
                # Get the 5 Years value (most commonly used)
                rows = next_table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        period = cells[0].get_text().strip()
                        value_text = cells[1].get_text().strip()

                        # Prefer 5 Years data
                        if "5 Years" in period or "5 years" in period:
                            if "Sales" in th_text and revenue_growth is None:
                                revenue_growth = _parse_number(value_text)
                            elif "Profit" in th_text and profit_growth is None:
                                profit_growth = _parse_number(value_text)
                                break  # Found what we need, stop processing this table

    # Extract industry PE and PB from peers section if available
    industry_pe = None
    industry_pb = None
    peers_section = soup.select_one("#peers")
    if peers_section:
        median_row = peers_section.select_one("tr.median")
        if median_row:
            cells = median_row.select("td")
            # Try to find PE and PB by cell content
            for cell in cells:
                cell_text = cell.get_text().strip()
                val = _parse_number(cell_text)
                if val and 0 < val < 1000:  # Reasonable PE/PB range
                    if industry_pe is None:
                        industry_pe = val
                    elif industry_pb is None:
                        industry_pb = val
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
        ev_ebitda=ev_ebitda,
        industry_pe=industry_pe,
        industry_pb=industry_pb,
        roe=roe,
        roce=roce,
        debt_to_equity=debt_to_equity,
        current_ratio=current_ratio,
        revenue_growth=revenue_growth,
        profit_growth=profit_growth,
        dividend_yield=dividend_yield,
        promoter_holding=promoter_holding,
        fii_holding=fii_holding,
        dii_holding=dii_holding,
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
