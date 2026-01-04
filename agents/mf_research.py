"""
Mutual Fund Research Agent - Analyzes mutual funds.

Uses AMFI for NAV data and web search for additional details.
"""

from typing import Optional
from datetime import datetime

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from tools.amfi import get_nav, search_funds, get_fund_by_name, get_direct_plan
from tools.web_search import search_mutual_fund_news
from models.mutual_fund import MutualFundNAV, MutualFundDetails, MutualFundAnalysis


def analyze_mutual_fund(fund_name: str, include_news: bool = True) -> Optional[MutualFundAnalysis]:
    """
    Perform comprehensive mutual fund analysis.
    
    Args:
        fund_name: Fund name or partial match
        include_news: Whether to fetch recent news
        
    Returns:
        MutualFundAnalysis object with available data
    """
    # Try to find the fund
    nav = get_fund_by_name(fund_name)
    
    if not nav:
        # Try direct plan
        nav = get_direct_plan(fund_name)
    
    if not nav:
        return None
    
    # Get news if requested
    news = None
    if include_news:
        news = search_mutual_fund_news(nav.scheme_name)
    
    # Build details (we'd ideally scrape more data, but using what we have)
    details = MutualFundDetails(
        scheme_code=nav.scheme_code,
        scheme_name=nav.scheme_name,
        fund_house=nav.fund_house,
        category=_extract_category(nav.scheme_name),
        fetched_at=datetime.now()
    )
    
    return MutualFundAnalysis(
        nav=nav,
        details=details,
        news=news
    )


def _extract_category(scheme_name: str) -> Optional[str]:
    """Extract fund category from scheme name."""
    name_lower = scheme_name.lower()
    
    categories = [
        ("flexi cap", "Flexi Cap"),
        ("large cap", "Large Cap"),
        ("mid cap", "Mid Cap"),
        ("small cap", "Small Cap"),
        ("multi cap", "Multi Cap"),
        ("elss", "ELSS (Tax Saving)"),
        ("tax", "Tax Saving"),
        ("liquid", "Liquid"),
        ("overnight", "Overnight"),
        ("money market", "Money Market"),
        ("short duration", "Short Duration"),
        ("medium duration", "Medium Duration"),
        ("corporate bond", "Corporate Bond"),
        ("banking", "Banking & PSU"),
        ("gilt", "Gilt"),
        ("hybrid", "Hybrid"),
        ("balanced", "Balanced"),
        ("aggressive", "Aggressive Hybrid"),
        ("conservative", "Conservative Hybrid"),
        ("arbitrage", "Arbitrage"),
        ("index", "Index Fund"),
        ("nifty", "Index Fund"),
        ("sensex", "Index Fund"),
        ("international", "International"),
        ("global", "International"),
        ("us", "International"),
    ]
    
    for keyword, category in categories:
        if keyword in name_lower:
            return category
    
    return "Equity" if "equity" in name_lower or "growth" in name_lower else None


def format_mutual_fund_analysis(analysis: MutualFundAnalysis) -> str:
    """
    Format mutual fund analysis into readable output.
    """
    if not analysis or not analysis.nav:
        return "No analysis data available."
    
    lines = []
    nav = analysis.nav
    details = analysis.details
    
    # Header
    lines.append(f"\n{nav.scheme_name}")
    lines.append("━" * 50)
    
    # Basic info
    lines.append(f"\nFund House: {nav.fund_house}")
    if details and details.category:
        lines.append(f"Category: {details.category}")
    
    # NAV
    lines.append(f"\nNAV: ₹{nav.nav:.4f}")
    lines.append(f"As of: {nav.date.strftime('%d %b %Y')}")
    
    # Fund type
    if nav.scheme_type:
        lines.append(f"Type: {nav.scheme_type}")
    
    # Check if Direct plan
    if "direct" in nav.scheme_name.lower():
        lines.append("\n✓ This is a Direct Plan (lower expense ratio)")
    else:
        lines.append("\n⚠ This appears to be a Regular Plan. Consider Direct Plan for lower fees.")
    
    # News if available
    if analysis.news:
        lines.append("\nRECENT NEWS")
        lines.append("━" * 20)
        for item in analysis.news[:3]:
            title = item.get("title", "")[:60]
            source = item.get("source", "")
            lines.append(f"• {title}...")
            lines.append(f"  - {source}")
    
    # Disclaimer
    lines.append("\n" + "─" * 50)
    lines.append("Note: For detailed performance data, check Value Research or Morningstar.")
    lines.append("Source: AMFI India")
    
    return "\n".join(lines)


def search_mutual_funds(query: str) -> list[dict]:
    """
    Search for mutual funds and return formatted results.
    
    Args:
        query: Search query
        
    Returns:
        List of fund matches with basic info
    """
    funds = search_funds(query, limit=10)
    
    return [
        {
            "scheme_code": f.scheme_code,
            "scheme_name": f.scheme_name,
            "fund_house": f.fund_house,
            "nav": f.nav,
            "date": f.date.strftime("%Y-%m-%d")
        }
        for f in funds
    ]


def compare_funds(fund_names: list[str]) -> str:
    """
    Compare multiple mutual funds.
    
    Args:
        fund_names: List of fund names to compare
        
    Returns:
        Formatted comparison
    """
    analyses = []
    for name in fund_names[:5]:
        analysis = analyze_mutual_fund(name, include_news=False)
        if analysis and analysis.nav:
            analyses.append(analysis)
    
    if not analyses:
        return "Could not find any of the specified funds."
    
    lines = []
    lines.append("\nMUTUAL FUND COMPARISON")
    lines.append("━" * 60)
    
    for analysis in analyses:
        nav = analysis.nav
        details = analysis.details
        
        lines.append(f"\n{nav.scheme_name[:40]}...")
        lines.append(f"  Fund House: {nav.fund_house}")
        lines.append(f"  Category: {details.category if details else 'N/A'}")
        lines.append(f"  NAV: ₹{nav.nav:.4f}")
        is_direct = "Yes" if "direct" in nav.scheme_name.lower() else "No"
        lines.append(f"  Direct Plan: {is_direct}")
    
    lines.append("\n" + "─" * 60)
    lines.append("Source: AMFI India")
    
    return "\n".join(lines)
