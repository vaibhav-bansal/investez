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
from growwapi.groww.exceptions import GrowwAPIException
import pyotp

from database.db import get_db
from utils.crypto import decrypt_data, encrypt_data


class GrowwTokenExpiredError(Exception):
    """Raised when Groww access token has expired or is invalid."""
    pass


def get_groww(user_id: int) -> Optional[GrowwAPI]:
    """
    Get authenticated Groww instance for a user using TOTP.

    Args:
        user_id: User ID to fetch credentials for.

    Returns:
        Authenticated GrowwAPI instance or None if not configured/authenticated.
    """
    # Get user's Groww credentials from database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
          SELECT bc.api_key, bc.totp_secret_encrypted, bc.access_token_encrypted
          FROM broker_credentials bc
          JOIN brokers b ON bc.broker_id = b.id
          WHERE bc.user_id = ? AND b.broker_id = 'groww'
        """, (user_id,))

        row = cursor.fetchone()
        if not row:
            print(f"Error: No Groww credentials found for user {user_id}")
            return None

        api_key = row["api_key"]
        totp_secret_encrypted = row["totp_secret_encrypted"]
        access_token_encrypted = row["access_token_encrypted"]

        if not totp_secret_encrypted:
            print(f"Error: Groww TOTP secret not configured for user {user_id}")
            return None

        # If we have a cached access token, try to use it
        if access_token_encrypted:
            try:
                access_token = decrypt_data(access_token_encrypted)
                groww = GrowwAPI(access_token)
                # Test the connection by trying to get holdings
                test_holdings = groww.get_holdings_for_user()
                if test_holdings:
                    return groww
            except (GrowwAPIException, Exception) as e:
                print(f"[Groww] Cached token expired, generating new one: {e}")
                # Token expired, continue to generate new one

        # Generate new access token using TOTP
        totp_secret = decrypt_data(totp_secret_encrypted)
        totp_gen = pyotp.TOTP(totp_secret)
        totp = totp_gen.now()

        try:
            access_token = GrowwAPI.get_access_token(api_key=api_key, totp=totp)

            # Cache the access token for future use
            _save_access_token(user_id, access_token)

            # Create Groww instance with access token
            groww = GrowwAPI(access_token)
            return groww
        except Exception as e:
            print(f"Error generating Groww access token: {e}")
            return None


def _save_access_token(user_id: int, access_token: str) -> None:
    """Save encrypted access token to database."""
    access_token_encrypted = encrypt_data(access_token)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE broker_credentials
            SET access_token_encrypted = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND broker_id = (SELECT id FROM brokers WHERE broker_id = 'groww')
        """, (access_token_encrypted, user_id))


def get_holdings(
    user_id: int,
    price_map: dict[str, float] | None = None,
    fetch_quotes: bool = True
) -> list[dict[str, Any]]:
    """
    Get user's stock holdings from Groww.

    Args:
        user_id: User ID to fetch holdings for.
        price_map: Optional dict mapping trading_symbol to last_price (from Kite or other sources).
                   Avoids redundant quote API calls for stocks already priced.
        fetch_quotes: If True, fetch individual quotes for each stock (slow).
                     If False, return holdings without quote data (prices will be None).

    Returns list of holdings with:
        - isin, trading_symbol
        - quantity, average_price
        - last_price: From price_map or Groww quote API (if fetch_quotes=True), else None
        - day_change: From Groww quote API (if fetch_quotes=True), else None
        - day_change_percentage: From Groww quote API (if fetch_quotes=True), else None

    Raises:
        GrowwTokenExpiredError: If the access token has expired or is invalid.
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
            transformed = []
            for h in holdings:
                symbol = h.get('trading_symbol', '')

                # Initialize with None - will be filled if fetch_quotes=True
                last_price = None
                day_change = None
                day_change_percentage = None

                # Only fetch quotes if requested
                if fetch_quotes:
                    # Get current price - try multiple sources in order of preference
                    last_price = h.get('average_price')  # Default fallback

                    # 1. Check if price available from price_map (from Kite or other source)
                    if price_map and symbol in price_map:
                        last_price = price_map[symbol]
                        day_change = 0  # Not available from price_map
                        day_change_percentage = 0  # Not available from price_map
                        print(f"[Groww] Using price_map price for {symbol}: ₹{last_price}")
                    else:
                        # 2. Fetch from Groww quote API
                        try:
                            quote = groww.get_quote(
                                trading_symbol=symbol,
                                exchange=groww.EXCHANGE_NSE,  # Try NSE first
                                segment=groww.SEGMENT_CASH
                            )
                            if quote and quote.get('last_price'):
                                last_price = quote.get('last_price')
                                day_change = quote.get('day_change')
                                day_change_percentage = quote.get('day_change_perc')
                                print(f"[Groww] Fetched quote for {symbol}: ₹{last_price} ({day_change_percentage:.2f}%)")
                            else:
                                print(f"[Groww] No last_price in quote for {symbol}")
                                last_price = None
                        except GrowwAPIException as e:
                            # Check if it's an authentication error
                            if '401' in str(e) or '403' in str(e) or 'Unauthorized' in str(e) or 'Authentication' in str(e):
                                raise GrowwTokenExpiredError("Groww access token has expired. Please re-authenticate.") from e
                            # Other errors - keep as None
                            print(f"[Groww] Quote fetch failed for {symbol}: {e}")
                            last_price = None
                        except Exception as e:
                            # Fallback to None if quote fetch fails
                            print(f"[Groww] Quote fetch failed for {symbol}: {e}")
                            last_price = None

                transformed.append({
                    'tradingsymbol': symbol,
                    'trading_symbol': symbol,
                    'exchange': 'NSE',  # Default to NSE
                    'isin': h.get('isin'),
                    'quantity': h.get('quantity', 0),
                    'average_price': h.get('average_price', 0),
                    'last_price': last_price,
                    'pnl': None,  # Will be calculated by frontend using avg_price if last_price is None
                    'day_change': day_change,
                    'day_change_percentage': day_change_percentage,
                })

            return transformed

        return []
    except GrowwTokenExpiredError:
        raise
    except GrowwAPIException as e:
        # Check if it's an authentication error
        if '401' in str(e) or '403' in str(e) or 'Unauthorized' in str(e) or 'Authentication' in str(e):
            raise GrowwTokenExpiredError("Groww access token has expired. Please re-authenticate.") from e
        print(f"[Groww] Error fetching holdings: {e}")
        import traceback
        traceback.print_exc()
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
    except GrowwTokenExpiredError:
        raise
    except GrowwAPIException as e:
        # Check if it's an authentication error
        if '401' in str(e) or '403' in str(e) or 'Unauthorized' in str(e) or 'Authentication' in str(e):
            raise GrowwTokenExpiredError("Groww access token has expired. Please re-authenticate.") from e
        print(f"Error fetching Groww positions: {e}")
        return []
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
    except GrowwTokenExpiredError:
        raise
    except GrowwAPIException as e:
        # Check if it's an authentication error
        if '401' in str(e) or '403' in str(e) or 'Unauthorized' in str(e) or 'Authentication' in str(e):
            raise GrowwTokenExpiredError("Groww access token has expired. Please re-authenticate.") from e
        print(f"Error fetching Groww quote: {e}")
        return None
    except Exception as e:
        print(f"Error fetching Groww quote: {e}")
        return None
