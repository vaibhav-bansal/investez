"""
Formatting utilities for rich console output.
"""

from typing import Optional


def format_header(text: str, width: int = 50) -> str:
    """Format a header with underline."""
    return f"\n{text}\n{'━' * width}"


def format_subheader(text: str, width: int = 30) -> str:
    """Format a subheader with lighter underline."""
    return f"\n{text}\n{'─' * width}"


def format_metric(
    name: str,
    value: float,
    suffix: str = "",
    industry_avg: Optional[float] = None
) -> str:
    """
    Format a metric with optional industry comparison.
    """
    lines = [f"{name}: {value:.2f}{suffix}"]
    
    if industry_avg is not None:
        lines.append(f"Industry Avg: {industry_avg:.2f}{suffix}")
        diff = value - industry_avg
        if abs(diff) > 0.01:
            direction = "above" if diff > 0 else "below"
            lines.append(f"→ {abs(diff):.2f} {direction} industry average")
    
    return "\n".join(lines)


def format_change(value: float, suffix: str = "%") -> str:
    """Format a change value with sign."""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}{suffix}"


def format_currency(amount: float, currency: str = "₹") -> str:
    """Format currency with Indian number system."""
    if amount >= 10000000:  # 1 crore
        return f"{currency}{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        return f"{currency}{amount/100000:.2f} L"
    elif amount >= 1000:
        return f"{currency}{amount/1000:.1f}K"
    else:
        return f"{currency}{amount:,.2f}"


def format_market_cap(cap_crores: float) -> str:
    """Format market cap from crores."""
    if cap_crores >= 100000:
        return f"₹{cap_crores/100000:.2f}L Cr"
    elif cap_crores >= 1000:
        return f"₹{cap_crores/1000:.1f}K Cr"
    else:
        return f"₹{cap_crores:.0f} Cr"


def format_percentage(value: float, include_sign: bool = False) -> str:
    """Format a percentage value."""
    if include_sign:
        sign = "+" if value >= 0 else ""
        return f"{sign}{value:.2f}%"
    return f"{value:.2f}%"


def format_table(
    headers: list[str],
    rows: list[list[str]],
    col_widths: Optional[list[int]] = None
) -> str:
    """
    Format data as a simple table.
    """
    if not col_widths:
        # Auto-calculate widths
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(header)
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width + 2)
    
    lines = []
    
    # Header
    header_line = " | ".join(
        str(h).ljust(col_widths[i]) for i, h in enumerate(headers)
    )
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    # Rows
    for row in rows:
        row_line = " | ".join(
            str(row[i] if i < len(row) else "").ljust(col_widths[i])
            for i in range(len(headers))
        )
        lines.append(row_line)
    
    return "\n".join(lines)


def format_bullet_list(items: list[str], bullet: str = "•") -> str:
    """Format items as bullet list."""
    return "\n".join(f"{bullet} {item}" for item in items)


def format_numbered_list(items: list[str]) -> str:
    """Format items as numbered list."""
    return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))


def truncate(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_date(date_str: str, output_format: str = "%d %b %Y") -> str:
    """Format date string."""
    from datetime import datetime
    
    # Try common input formats
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S"]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime(output_format)
        except ValueError:
            continue
    
    return date_str  # Return as-is if parsing fails


def print_separator(char: str = "─", width: int = 50) -> str:
    """Return a separator line."""
    return char * width
