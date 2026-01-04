"""
Web search wrapper for fetching news about stocks/companies.

Usage:
    from tools.web_search import search_news

    news = search_news("Reliance Industries")
"""

import re
from datetime import datetime
from typing import Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


def search_news(
    query: str,
    max_results: int = 5
) -> Optional[list[dict]]:
    """
    Search for recent news about a company/topic.

    Uses Google News RSS feed for fetching news.

    Args:
        query: Search query (e.g., "Reliance Industries stock")
        max_results: Maximum number of results to return

    Returns:
        List of news items with title, source, date, and link
    """
    # Use Google News RSS
    encoded_query = quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml-xml")
        items = soup.find_all("item")

        results = []
        for item in items[:max_results]:
            title = item.find("title")
            link = item.find("link")
            pub_date = item.find("pubDate")
            source = item.find("source")

            if title and link:
                results.append({
                    "title": title.get_text().strip(),
                    "link": link.get_text().strip(),
                    "source": source.get_text().strip() if source else "Unknown",
                    "date": _parse_date(pub_date.get_text()) if pub_date else None,
                    "date_raw": pub_date.get_text().strip() if pub_date else None
                })

        return results

    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
        return None


def _parse_date(date_str: str) -> Optional[str]:
    """Parse RSS date format to readable format."""
    try:
        # RSS format: "Sat, 04 Jan 2026 10:30:00 GMT"
        dt = datetime.strptime(date_str.strip(), "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        try:
            # Try alternate format
            dt = datetime.strptime(date_str.strip()[:25], "%a, %d %b %Y %H:%M:%S")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None


def search_stock_news(symbol: str, company_name: Optional[str] = None) -> Optional[list[dict]]:
    """
    Search for news about a specific stock.

    Args:
        symbol: Stock symbol (e.g., "RELIANCE")
        company_name: Full company name (e.g., "Reliance Industries")

    Returns:
        List of news items
    """
    # Build search query
    if company_name:
        query = f"{company_name} stock news"
    else:
        query = f"{symbol} stock news India"

    return search_news(query)


def search_mutual_fund_news(fund_name: str) -> Optional[list[dict]]:
    """
    Search for news about a mutual fund.

    Args:
        fund_name: Fund name (e.g., "Parag Parikh Flexi Cap")

    Returns:
        List of news items
    """
    query = f"{fund_name} mutual fund"
    return search_news(query)


def get_market_news() -> Optional[list[dict]]:
    """Get general Indian stock market news."""
    return search_news("Indian stock market NSE BSE", max_results=10)
