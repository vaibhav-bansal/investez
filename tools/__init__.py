"""InvestEasy Tools Package"""

from tools.kite import get_quote, get_price_history, authenticate, is_authenticated
from tools.screener import get_stock_fundamentals, get_peer_comparison, search_stock
from tools.amfi import get_nav, search_funds, get_fund_by_name
from tools.web_search import search_news, search_stock_news

__all__ = [
    "get_quote",
    "get_price_history",
    "authenticate",
    "is_authenticated",
    "get_stock_fundamentals",
    "get_peer_comparison",
    "search_stock",
    "get_nav",
    "search_funds",
    "get_fund_by_name",
    "search_news",
    "search_stock_news",
]
