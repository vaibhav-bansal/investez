"""
Groww Trade API wrapper for portfolio data.

Usage:
    from tools.groww import get_holdings, get_positions

    # Get user's holdings
    holdings = get_holdings(user_id=1)

    # Get user's positions
    positions = get_positions(user_id=1)
"""

from typing import Optional, Any
from growwapi import GrowwAPI

from database.db import get_db
from utils.crypto import decrypt_data


def get_groww(user_id: int) -> Optional[GrowwAPI]:
  """
  Get authenticated Groww instance for a user.

  Args:
      user_id: User ID to fetch credentials for.

  Returns:
      Authenticated GrowwAPI instance or None if not configured/authenticated.
  """
  # Get user's Groww credentials from database
  with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("""
      SELECT bc.access_token_encrypted
      FROM broker_credentials bc
      JOIN brokers b ON bc.broker_id = b.id
      WHERE bc.user_id = ? AND b.broker_id = 'groww'
    """, (user_id,))

    row = cursor.fetchone()
    if not row:
      print(f"Error: No Groww credentials found for user {user_id}")
      return None

    access_token_encrypted = row["access_token_encrypted"]

    if not access_token_encrypted:
      print(f"Error: Groww not authenticated for user {user_id}")
      return None

    access_token = decrypt_data(access_token_encrypted)

    # Create Groww instance with access token
    groww = GrowwAPI(access_token)
    return groww


def get_holdings(user_id: int, price_map: dict[str, float] | None = None) -> list[dict[str, Any]]:
  """
  Get user's stock holdings from Groww.

  Args:
      user_id: User ID to fetch holdings for.
      price_map: Optional dict mapping trading_symbol to last_price (from Kite or other sources).
                 Avoids redundant quote API calls for stocks already priced.

  Returns list of holdings with:
      - isin, trading_symbol
      - quantity, average_price
      - Various lock quantities and transfer data
  """
  groww = get_groww(user_id=user_id)
  if not groww:
    return []

  try:
    response = groww.get_holdings_for_user()

    # Groww API returns {'holdings': [...]} format
    if response and isinstance(response, dict) and 'holdings' in response:
      holdings = response['holdings']

      # Transform Groww format to match Kite format expected by portfolio service
      # Note: Groww holdings don't include current market price, need to fetch quotes separately
      transformed = []
      for h in holdings:
        symbol = h.get('trading_symbol', '')

        # Get current price - try multiple sources in order of preference
        last_price = h.get('average_price', 0)  # Default fallback
        day_change = 0
        day_change_percentage = 0

        # 1. Check if price available from Kite (same stock, no API call needed)
        if price_map and symbol in price_map:
          last_price = price_map[symbol]
          print(f"[Groww] Using Kite price for {symbol}: ₹{last_price}")
        else:
          # 2. Fetch from Groww quote API
          try:
            quote = groww.get_quote(
              trading_symbol=symbol,
              exchange=groww.EXCHANGE_NSE,  # Try NSE first
              segment=groww.SEGMENT_CASH
            )
            if quote and quote.get('last_price'):
              last_price = quote.get('last_price', h.get('average_price', 0))
              day_change = quote.get('day_change', 0)
              day_change_percentage = quote.get('day_change_perc', 0)
              print(f"[Groww] Fetched quote for {symbol}: ₹{last_price} ({day_change_percentage:.2f}%)")
            else:
              print(f"[Groww] No last_price in quote for {symbol}, using average price")
              last_price = h.get('average_price', 0)
          except Exception as e:
            # 3. Fallback to average price if quote fetch fails (shows 0 P&L)
            print(f"[Groww] Quote fetch failed for {symbol}: {e}")
            last_price = h.get('average_price', 0)

        transformed.append({
          'tradingsymbol': symbol,
          'trading_symbol': symbol,
          'exchange': 'NSE',  # Default to NSE
          'isin': h.get('isin'),
          'quantity': h.get('quantity', 0),
          'average_price': h.get('average_price', 0),
          'last_price': last_price,
          'pnl': (last_price - h.get('average_price', 0)) * h.get('quantity', 0),
          'day_change': day_change,
          'day_change_percentage': day_change_percentage,
        })

      return transformed

    return []
  except Exception as e:
    print(f"[Groww] Error fetching holdings: {e}")
    import traceback
    traceback.print_exc()
    return []


def get_positions(user_id: int, segment: Optional[str] = None) -> list[dict[str, Any]]:
  """
  Get user's current positions from Groww.

  Args:
      user_id: User ID to fetch positions for.
      segment: Optional segment filter (SEGMENT_CASH, SEGMENT_FNO, SEGMENT_COMMODITY).
               If None, returns positions from all segments.

  Returns list of positions with:
      - trading_symbol, segment, exchange, isin
      - credit/debit quantities and prices
      - carry_forward data
      - realized P&L
  """
  groww = get_groww(user_id=user_id)
  if not groww:
    return []

  try:
    # If segment is provided, pass it to the API
    if segment:
      positions = groww.get_positions_for_user(segment=segment)
    else:
      positions = groww.get_positions_for_user()

    return positions if positions else []
  except Exception as e:
    print(f"Error fetching Groww positions: {e}")
    return []


def get_quote(trading_symbol: str, exchange: str, segment: str, user_id: int) -> Optional[dict[str, Any]]:
  """
  Get real-time quote for a stock from Groww.

  Args:
      trading_symbol: Stock symbol (e.g., "RELIANCE")
      exchange: Exchange (e.g., "NSE", "BSE")
      segment: Segment (e.g., "CASH", "FO", "CD")
      user_id: User ID for authentication

  Returns:
      Quote data with OHLC, bid/ask, volume, etc. or None
  """
  groww = get_groww(user_id=user_id)
  if not groww:
    return None

  try:
    quote = groww.get_quote(
      exchange=exchange,
      segment=segment,
      trading_symbol=trading_symbol
    )
    return quote if quote else None
  except Exception as e:
    print(f"Error fetching Groww quote: {e}")
    return None
