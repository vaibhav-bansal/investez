"""
Portfolio API endpoints.
"""

from flask import Blueprint, jsonify
from datetime import datetime

from services.portfolio import get_portfolio, get_holdings_only, get_mf_only

portfolio_bp = Blueprint("portfolio", __name__)


def _success_response(data, cached_at: datetime = None):
    """Wrap data in standard success response."""
    return jsonify({
        "success": True,
        "data": data,
        "cached_at": (cached_at or datetime.now()).isoformat(),
    })


def _error_response(message: str, status_code: int = 500):
    """Return error response."""
    return jsonify({
        "success": False,
        "error": message,
    }), status_code


@portfolio_bp.route("/", methods=["GET"])
def get_full_portfolio():
    """
    Get complete portfolio with holdings, MF, and allocations.
    """
    try:
        portfolio = get_portfolio()
        if not portfolio:
            return _error_response("Could not fetch portfolio. Check Kite authentication.", 401)

        return _success_response(
            portfolio.model_dump(mode="json"),
            portfolio.fetched_at,
        )
    except Exception as e:
        return _error_response(str(e))


@portfolio_bp.route("/summary", methods=["GET"])
def get_summary():
    """
    Get quick portfolio summary (total value, P&L).
    """
    try:
        portfolio = get_portfolio()
        if not portfolio:
            return _error_response("Could not fetch portfolio.", 401)

        return _success_response(
            portfolio.summary.model_dump(mode="json"),
            portfolio.fetched_at,
        )
    except Exception as e:
        return _error_response(str(e))


@portfolio_bp.route("/holdings", methods=["GET"])
def get_holdings():
    """
    Get stock holdings only.
    """
    try:
        holdings = get_holdings_only()
        return _success_response(
            [h.model_dump(mode="json") for h in holdings],
        )
    except Exception as e:
        return _error_response(str(e))


@portfolio_bp.route("/mf", methods=["GET"])
def get_mf():
    """
    Get mutual fund holdings only.
    """
    try:
        mf_holdings = get_mf_only()
        return _success_response(
            [m.model_dump(mode="json") for m in mf_holdings],
        )
    except Exception as e:
        return _error_response(str(e))


@portfolio_bp.route("/allocation", methods=["GET"])
def get_allocation():
    """
    Get allocation breakdown (sector, market cap, asset type).
    """
    try:
        portfolio = get_portfolio()
        if not portfolio:
            return _error_response("Could not fetch portfolio.", 401)

        return _success_response(
            portfolio.allocation.model_dump(mode="json"),
            portfolio.fetched_at,
        )
    except Exception as e:
        return _error_response(str(e))
