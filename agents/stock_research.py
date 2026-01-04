"""
Stock Research Agent - Analyzes individual stocks.

Uses Kite Connect for price data and Screener.in for fundamentals.
Provides structured analysis with plain-language takeaways.
"""

from typing import Optional
from datetime import datetime

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from tools.kite import get_quote, get_multiple_price_history, is_authenticated
from tools.screener import get_stock_fundamentals, get_peer_comparison, search_stock
from tools.web_search import search_stock_news
from models.stock import StockQuote, StockFundamentals, StockAnalysis


def analyze_stock(symbol: str, include_news: bool = True) -> Optional[StockAnalysis]:
    """
    Perform comprehensive stock analysis.
    
    Args:
        symbol: Stock symbol (e.g., "RELIANCE", "TCS")
        include_news: Whether to fetch recent news
        
    Returns:
        StockAnalysis object with all available data
    """
    symbol = symbol.upper().strip()
    
    # Get fundamentals from Screener (most important)
    fundamentals = get_stock_fundamentals(symbol)
    
    # Get current quote from Kite (if authenticated)
    quote = None
    price_history = None
    if is_authenticated():
        quote = get_quote(symbol)
        history_dict = get_multiple_price_history(symbol)
        if history_dict:
            price_history = list(history_dict.values())
    
    # Get peer comparison
    peers = get_peer_comparison(symbol)
    
    # Get news if requested
    news = None
    if include_news:
        company_name = fundamentals.name if fundamentals else None
        news = search_stock_news(symbol, company_name)
    
    if not fundamentals and not quote:
        return None
    
    return StockAnalysis(
        quote=quote,
        fundamentals=fundamentals,
        price_history=price_history,
        peers=peers,
        news=news
    )


def format_stock_analysis(analysis: StockAnalysis) -> str:
    """
    Format stock analysis into readable output with takeaways.
    """
    if not analysis:
        return "No analysis data available."
    
    lines = []
    f = analysis.fundamentals
    q = analysis.quote
    
    # Header
    name = f.name if f else (q.symbol if q else "Unknown")
    symbol = f.symbol if f else (q.symbol if q else "")
    lines.append(f"\n{name} ({symbol})")
    lines.append("=" * 50)
    
    # Basic info
    if f:
        if f.sector:
            lines.append(f"\nSector: {f.sector}")
        if f.market_cap:
            cap_str = _format_market_cap(f.market_cap)
            cat = f.market_cap_category or ""
            lines.append(f"Market Cap: {cat} | {cap_str}")
    
    # Current price
    if q:
        change_sign = "+" if q.change_percent >= 0 else ""
        lines.append(f"Current Price: Rs.{q.current_price:,.2f} ({change_sign}{q.change_percent:.2f}%)")
    
    # Performance section
    if analysis.price_history:
        lines.append("\nPERFORMANCE")
        perf_parts = []
        for ph in analysis.price_history:
            sign = "+" if ph.return_percent >= 0 else ""
            perf_parts.append(f"{ph.period}: {sign}{ph.return_percent:.1f}%")
        lines.append(" | ".join(perf_parts))
    
    # Key metrics with explanations
    if f:
        lines.append("\nKEY METRICS")
        lines.append("=" * 20)
        
        # P/E Ratio
        if f.pe_ratio is not None:
            lines.append(f"\nP/E Ratio: {f.pe_ratio:.1f}")
            if f.industry_pe:
                lines.append(f"Industry Avg: {f.industry_pe:.1f}")
                pe_diff = f.pe_ratio - f.industry_pe
                if pe_diff > 5:
                    lines.append(f"-> Trading at premium ({pe_diff:.1f}x above industry). Market expects higher growth.")
                elif pe_diff < -5:
                    lines.append(f"-> Trading at discount ({abs(pe_diff):.1f}x below industry). Could be undervalued or facing challenges.")
                else:
                    lines.append("-> In line with industry average.")
        
        # P/B Ratio
        if f.pb_ratio is not None:
            lines.append(f"\nP/B Ratio: {f.pb_ratio:.2f}")
            if f.industry_pb:
                lines.append(f"Industry Avg: {f.industry_pb:.2f}")
        
        # ROE
        if f.roe is not None:
            lines.append(f"\nROE: {f.roe:.1f}%")
            if f.roe >= 15:
                lines.append("-> Strong return on equity. Efficient use of shareholder capital.")
            elif f.roe >= 10:
                lines.append("-> Moderate ROE. Reasonable efficiency.")
            else:
                lines.append("-> Below average ROE. Capital may not be working efficiently.")
        
        # ROCE
        if f.roce is not None:
            lines.append(f"\nROCE: {f.roce:.1f}%")
        
        # Debt/Equity
        if f.debt_to_equity is not None:
            lines.append(f"\nDebt/Equity: {f.debt_to_equity:.2f}")
            if f.debt_to_equity < 0.3:
                lines.append("-> Low debt. Conservative financing, lower risk.")
            elif f.debt_to_equity < 1.0:
                lines.append("-> Moderate debt levels. Generally manageable.")
            else:
                lines.append("-> High debt. Higher financial risk, especially in downturns.")
        
        # Growth
        if f.revenue_growth is not None or f.profit_growth is not None:
            lines.append("\nGROWTH (YoY)")
            if f.revenue_growth is not None:
                sign = "+" if f.revenue_growth >= 0 else ""
                lines.append(f"Revenue: {sign}{f.revenue_growth:.1f}%")
            if f.profit_growth is not None:
                sign = "+" if f.profit_growth >= 0 else ""
                lines.append(f"Profit: {sign}{f.profit_growth:.1f}%")
        
        # Ownership
        if f.promoter_holding is not None:
            lines.append("\nOWNERSHIP")
            lines.append(f"Promoter: {f.promoter_holding:.1f}%")
            if f.fii_holding:
                lines.append(f"FII: {f.fii_holding:.1f}%")
            if f.dii_holding:
                lines.append(f"DII: {f.dii_holding:.1f}%")
            
            if f.promoter_holding >= 50:
                lines.append("-> High promoter holding indicates confidence in business.")
            elif f.promoter_holding < 25:
                lines.append("-> Low promoter holding. May indicate less skin in the game.")
    
    # Peers comparison
    if analysis.peers:
        lines.append("\nPEER COMPARISON")
        lines.append("=" * 20)
        for peer in analysis.peers[:5]:  # Top 5 peers
            peer_name = peer.get("name", peer.get("symbol", ""))
            peer_pe = peer.get("pe_ratio", "N/A")
            peer_roe = peer.get("roe", "N/A")
            lines.append(f"  {peer_name}: P/E {peer_pe}, ROE {peer_roe}%")
    
    # Recent news
    if analysis.news:
        lines.append("\nRECENT NEWS")
        lines.append("=" * 20)
        for news_item in analysis.news[:3]:
            title = news_item.get("title", "")[:60]
            source = news_item.get("source", "")
            date = news_item.get("date", "")
            lines.append(f"* {title}...")
            lines.append(f"  - {source}, {date}")
    
    # Sources
    lines.append("\n" + "-" * 50)
    lines.append("Sources: Screener.in, Kite Connect")
    
    return "\n".join(lines)


def _format_market_cap(cap_cr: float) -> str:
    """Format market cap in crores to readable string."""
    if cap_cr >= 100000:
        return f"Rs.{cap_cr/100000:.2f}L Cr"
    elif cap_cr >= 1000:
        return f"Rs.{cap_cr/1000:.1f}K Cr"
    else:
        return f"Rs.{cap_cr:.0f} Cr"


def get_metric_explanation(
    metric_name: str,
    value: float,
    context: Optional[dict] = None
) -> str:
    """
    Get plain-language explanation for a metric using Claude.
    
    Args:
        metric_name: Name of the metric (e.g., "P/E Ratio", "ROE")
        value: The metric value
        context: Optional context (industry avg, company name, etc.)
        
    Returns:
        Plain-language explanation
    """
    if not ANTHROPIC_API_KEY:
        return _get_static_explanation(metric_name, value)
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    context_str = ""
    if context:
        context_str = f"Context: {context}"
    
    prompt = f"""Explain what a {metric_name} of {value} means for a stock investor in 2-3 simple sentences. 
{context_str}
Be concise and use plain language. No jargon. Focus on what this means for the investor."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error getting explanation: {e}")
        return _get_static_explanation(metric_name, value)


def _get_static_explanation(metric_name: str, value: float) -> str:
    """Fallback static explanations when Claude is unavailable."""
    metric_lower = metric_name.lower()
    
    if "p/e" in metric_lower:
        if value > 30:
            return f"P/E of {value:.1f} is high. You're paying a premium for this stock."
        elif value < 15:
            return f"P/E of {value:.1f} is low. Could be undervalued or facing challenges."
        else:
            return f"P/E of {value:.1f} is moderate. Reasonably priced."
    
    if "roe" in metric_lower:
        if value > 15:
            return f"ROE of {value:.1f}% is strong. Good returns on shareholder equity."
        elif value < 10:
            return f"ROE of {value:.1f}% is below average. Capital isn't working very efficiently."
        else:
            return f"ROE of {value:.1f}% is moderate."
    
    if "debt" in metric_lower:
        if value < 0.5:
            return f"Debt/Equity of {value:.2f} is low. Conservative financing."
        elif value > 1.5:
            return f"Debt/Equity of {value:.2f} is high. Higher financial risk."
        else:
            return f"Debt/Equity of {value:.2f} is moderate."
    
    return f"{metric_name}: {value}"


def compare_stocks(symbols: list[str]) -> str:
    """
    Compare multiple stocks side by side.
    
    Args:
        symbols: List of stock symbols to compare
        
    Returns:
        Formatted comparison table
    """
    analyses = []
    for symbol in symbols[:5]:  # Max 5 stocks
        analysis = analyze_stock(symbol, include_news=False)
        if analysis and analysis.fundamentals:
            analyses.append(analysis)
    
    if not analyses:
        return "Could not fetch data for any of the specified stocks."
    
    lines = []
    lines.append("\nSTOCK COMPARISON")
    lines.append("=" * 60)
    
    # Header
    header = ["Metric"] + [a.fundamentals.symbol for a in analyses]
    lines.append(" | ".join(f"{h:>12}" for h in header))
    lines.append("-" * 60)
    
    # Metrics
    metrics = [
        ("Market Cap", lambda f: _format_market_cap(f.market_cap) if f.market_cap else "N/A"),
        ("P/E", lambda f: f"{f.pe_ratio:.1f}" if f.pe_ratio else "N/A"),
        ("P/B", lambda f: f"{f.pb_ratio:.2f}" if f.pb_ratio else "N/A"),
        ("ROE %", lambda f: f"{f.roe:.1f}" if f.roe else "N/A"),
        ("ROCE %", lambda f: f"{f.roce:.1f}" if f.roce else "N/A"),
        ("D/E", lambda f: f"{f.debt_to_equity:.2f}" if f.debt_to_equity else "N/A"),
        ("Div Yield %", lambda f: f"{f.dividend_yield:.2f}" if f.dividend_yield else "N/A"),
    ]
    
    for metric_name, extractor in metrics:
        row = [metric_name]
        for a in analyses:
            row.append(extractor(a.fundamentals))
        lines.append(" | ".join(f"{v:>12}" for v in row))
    
    lines.append("\n" + "-" * 60)
    lines.append("Source: Screener.in")
    
    return "\n".join(lines)
