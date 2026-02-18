"""
Portfolio API endpoints.
"""

from flask import Blueprint, jsonify
from datetime import datetime, timezone

from services.portfolio import get_portfolio, get_holdings_only, get_mf_only
from utils.jwt_auth import require_auth
from tools.kite import KiteTokenExpiredError
from tools.groww import GrowwTokenExpiredError

portfolio_bp = Blueprint("portfolio", __name__)


def _success_response(data, cached_at: datetime = None):
    """Wrap data in standard success response."""
    return jsonify({
        "success": True,
        "data": data,
        "cached_at": (cached_at or datetime.now(timezone.utc)).isoformat(),
    })


def _error_response(message: str, status_code: int = 500):
    """Return error response."""
    return jsonify({
        "success": False,
        "error": message,
    }), status_code


@portfolio_bp.route("/holdings", methods=["GET"])
@require_auth
def get_holdings(user_id: int):
    """
    Get stock holdings only.
    """
    try:
        holdings = get_holdings_only(user_id=user_id)
        return _success_response(
            [h.model_dump(mode="json") for h in holdings],
        )
    except KiteTokenExpiredError:
        return jsonify({
            "success": False,
            "error": "Kite session has expired. Please re-authenticate.",
            "error_type": "kite_token_expired",
        }), 401
    except GrowwTokenExpiredError:
        return jsonify({
            "success": False,
            "error": "Groww session has expired. Please re-authenticate.",
            "error_type": "groww_token_expired",
        }), 401
    except Exception as e:
        return _error_response(str(e))


@portfolio_bp.route("/mf/holdings", methods=["GET"])
@require_auth
def get_mf(user_id: int):
    """
    Get mutual fund holdings only (without day change enrichment).
    """
    try:
        mf_holdings = get_mf_only(user_id=user_id)
        return _success_response(
            [m.model_dump(mode="json") for m in mf_holdings],
        )
    except KiteTokenExpiredError:
        return jsonify({
            "success": False,
            "error": "Kite session has expired. Please re-authenticate.",
            "error_type": "kite_token_expired",
        }), 401
    except GrowwTokenExpiredError:
        return jsonify({
            "success": False,
            "error": "Groww session has expired. Please re-authenticate.",
            "error_type": "groww_token_expired",
        }), 401
    except Exception as e:
        return _error_response(str(e))


# ============================================================================
# ENRICHMENT ENDPOINTS (Slow, fetch from external APIs)
# ============================================================================

@portfolio_bp.route("/enriched/holdings/quotes", methods=["GET"])
@require_auth
def get_holdings_quotes_enrichment(user_id: int):
    """
    Fetch current quotes for Groww stocks.

    Returns a map of {symbol: {last_price, day_change, day_change_percent}}
    for stocks that don't have quote data (typically Groww holdings).

    Time: ~10-20 seconds depending on number of Groww stocks.
    """
    from tools.groww import get_holdings as get_groww_holdings

    try:
        # Get holdings to find which ones need quotes
        holdings = get_holdings_only(user_id=user_id)

        # Filter Groww holdings that don't have current_price
        groww_symbols = [
            h.symbol for h in holdings
            if h.broker == "groww" and h.current_price is None
        ]

        if not groww_symbols:
            return _success_response({})

        # Build price map from Kite holdings (to skip quotes for shared stocks)
        kite_price_map = {
            h.symbol: h.current_price
            for h in holdings
            if h.broker == "kite" and h.current_price is not None
        }

        # Fetch Groww holdings with quotes
        groww_holdings = get_groww_holdings(
            user_id=user_id,
            price_map=kite_price_map,
            fetch_quotes=True
        )

        # Build response map
        quotes_map = {}
        for h in groww_holdings:
            symbol = h.get('tradingsymbol', '')
            if h.get('last_price') is not None:
                quotes_map[symbol] = {
                    'last_price': h['last_price'],
                    'day_change': h.get('day_change'),
                    'day_change_percent': h.get('day_change_percentage')
                }

        return _success_response(quotes_map)

    except KiteTokenExpiredError:
        return jsonify({
            "success": False,
            "error": "Kite session has expired. Please re-authenticate.",
            "error_type": "kite_token_expired",
        }), 401
    except GrowwTokenExpiredError:
        return jsonify({
            "success": False,
            "error": "Groww session has expired. Please re-authenticate.",
            "error_type": "groww_token_expired",
        }), 401
    except Exception as e:
        return _error_response(str(e))


@portfolio_bp.route("/enriched/holdings/market-cap", methods=["GET"])
@require_auth
def get_market_cap_enrichment(user_id: int):
    """
    Fetch market cap categories for stock holdings from Screener.in.

    Returns a map of {symbol: market_cap_category}.

    Time: ~30-40 seconds (1 second per stock with rate limiting).
    """
    from tools.screener import get_stock_fundamentals

    try:
        holdings = get_holdings_only(user_id=user_id)

        # Fetch market cap from Screener for each stock
        market_cap_map = {}
        for h in holdings:
            if h.symbol not in market_cap_map:
                try:
                    fundamentals = get_stock_fundamentals(h.symbol)
                    market_cap_map[h.symbol] = fundamentals.market_cap_category if fundamentals else None
                except Exception as e:
                    print(f"Failed to fetch market cap for {h.symbol}: {e}")
                    market_cap_map[h.symbol] = None

        return _success_response(market_cap_map)

    except KiteTokenExpiredError:
        return jsonify({
            "success": False,
            "error": "Kite session has expired. Please re-authenticate.",
            "error_type": "kite_token_expired",
        }), 401
    except GrowwTokenExpiredError:
        return jsonify({
            "success": False,
            "error": "Groww session has expired. Please re-authenticate.",
            "error_type": "groww_token_expired",
        }), 401
    except Exception as e:
        return _error_response(str(e))


@portfolio_bp.route("/enriched/mf/holdings/day-change", methods=["GET"])
@require_auth
def get_mf_day_change_enrichment(user_id: int):
    """
    Fetch day change data for mutual fund holdings from MFApi.in.

    Returns a map of {scheme_code: {day_change, day_change_percent}}.

    Time: ~10-15 seconds (0.5 second per MF with rate limiting).
    """
    from tools.mf_isin_mapper import get_scheme_code_from_fund_name
    from tools.mfapi import get_mf_day_change

    try:
        mf_holdings = get_mf_only(user_id=user_id)

        # Fetch day change from MFApi for each MF
        day_change_map = {}
        for mf in mf_holdings:
            # Use scheme_name to get the actual scheme code (mf.scheme_code contains ISIN)
            api_scheme_code = get_scheme_code_from_fund_name(mf.scheme_name)
            if api_scheme_code and api_scheme_code not in day_change_map:
                try:
                    mf_change = get_mf_day_change(api_scheme_code)
                    if mf_change:
                        # Key by the original scheme_code (ISIN) so frontend can match
                        day_change_map[mf.scheme_code] = {
                            'day_change': mf_change['change'],
                            'day_change_percent': mf_change['change_percent']
                        }
                except Exception as e:
                    print(f"Failed to fetch day change for {mf.scheme_name}: {e}")
                    day_change_map[mf.scheme_code] = None

        return _success_response(day_change_map)

    except KiteTokenExpiredError:
        return jsonify({
            "success": False,
            "error": "Kite session has expired. Please re-authenticate.",
            "error_type": "kite_token_expired",
        }), 401
    except GrowwTokenExpiredError:
        return jsonify({
            "success": False,
            "error": "Groww session has expired. Please re-authenticate.",
            "error_type": "groww_token_expired",
        }), 401
    except Exception as e:
        return _error_response(str(e))
