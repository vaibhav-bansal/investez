"""
News Agent - Fetches and summarizes news about stocks and mutual funds.
"""

from typing import Optional
import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from tools.web_search import search_news, search_stock_news, search_mutual_fund_news


def get_stock_news(symbol: str, company_name: Optional[str] = None) -> Optional[dict]:
    """
    Get news for a stock with optional summary.
    
    Args:
        symbol: Stock symbol
        company_name: Full company name for better search
        
    Returns:
        Dict with news items and optional summary
    """
    news = search_stock_news(symbol, company_name)
    
    if not news:
        return None
    
    result = {
        "symbol": symbol,
        "company_name": company_name,
        "news_items": news,
        "summary": None
    }
    
    # Generate summary if we have API key
    if ANTHROPIC_API_KEY and len(news) >= 2:
        result["summary"] = _summarize_news(news, f"{company_name or symbol} stock")
    
    return result


def get_mutual_fund_news(fund_name: str) -> Optional[dict]:
    """
    Get news for a mutual fund.
    
    Args:
        fund_name: Fund name
        
    Returns:
        Dict with news items
    """
    news = search_mutual_fund_news(fund_name)
    
    if not news:
        return None
    
    return {
        "fund_name": fund_name,
        "news_items": news,
        "summary": None
    }


def get_market_news() -> Optional[dict]:
    """
    Get general market news.
    
    Returns:
        Dict with market news items
    """
    news = search_news("Indian stock market NSE BSE Nifty Sensex", max_results=10)
    
    if not news:
        return None
    
    result = {
        "topic": "Indian Stock Market",
        "news_items": news,
        "summary": None
    }
    
    if ANTHROPIC_API_KEY and len(news) >= 3:
        result["summary"] = _summarize_news(news, "Indian stock market")
    
    return result


def _summarize_news(news_items: list[dict], topic: str) -> Optional[str]:
    """
    Generate a brief summary of news items using Claude.
    """
    if not ANTHROPIC_API_KEY:
        return None
    
    # Format news for summarization
    news_text = "\n".join([
        f"- {item['title']} ({item.get('source', 'Unknown')})"
        for item in news_items
    ])
    
    prompt = f"""Summarize the key themes from these recent news headlines about {topic} in 2-3 bullet points.
Focus on what matters for investors. Be concise.

Headlines:
{news_text}

Summary:"""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Error summarizing news: {e}")
        return None


def format_news_response(news_data: dict) -> str:
    """
    Format news data for display.
    """
    lines = []
    
    # Header
    if "symbol" in news_data:
        lines.append(f"\nNEWS: {news_data.get('company_name', news_data['symbol'])}")
    elif "fund_name" in news_data:
        lines.append(f"\nNEWS: {news_data['fund_name']}")
    else:
        lines.append(f"\nMARKET NEWS")
    
    lines.append("━" * 40)
    
    # Summary if available
    if news_data.get("summary"):
        lines.append("\nKey Themes:")
        lines.append(news_data["summary"])
        lines.append("")
    
    # Individual news items
    lines.append("Recent Headlines:")
    for item in news_data.get("news_items", [])[:5]:
        title = item.get("title", "")
        source = item.get("source", "")
        date = item.get("date", "")
        lines.append(f"\n• {title}")
        lines.append(f"  - {source}, {date}")
    
    return "\n".join(lines)
