"""
Groww portfolio API endpoints.
"""

from flask import Blueprint, jsonify

from tools.groww import get_holdings, get_positions
from utils.jwt_auth import require_auth

groww_portfolio_bp = Blueprint("groww_portfolio", __name__)


@groww_portfolio_bp.route("/holdings", methods=["GET"])
@require_auth
def get_groww_holdings(user_id: int):
  """
  Get stock holdings from Groww.
  """
  try:
    holdings = get_holdings(user_id=user_id)

    if not holdings:
      return jsonify({
        "success": False,
        "error": "Could not fetch Groww holdings. Check authentication.",
      }), 401

    return jsonify({
      "success": True,
      "data": {
        "holdings": holdings,
        "count": len(holdings),
      },
    })
  except Exception as e:
    return jsonify({
      "success": False,
      "error": f"Failed to fetch holdings: {str(e)}",
    }), 500


@groww_portfolio_bp.route("/positions", methods=["GET"])
@require_auth
def get_groww_positions(user_id: int):
  """
  Get current positions from Groww (all segments).
  """
  try:
    positions = get_positions(user_id=user_id)

    if not positions:
      return jsonify({
        "success": True,
        "data": {
          "positions": [],
          "count": 0,
        },
      })

    return jsonify({
      "success": True,
      "data": {
        "positions": positions,
        "count": len(positions),
      },
    })
  except Exception as e:
    return jsonify({
      "success": False,
      "error": f"Failed to fetch positions: {str(e)}",
    }), 500


@groww_portfolio_bp.route("/positions/<segment>", methods=["GET"])
@require_auth
def get_groww_positions_by_segment(user_id: int, segment: str):
  """
  Get positions for a specific segment.

  Segments: SEGMENT_CASH, SEGMENT_FNO, SEGMENT_COMMODITY
  """
  try:
    # Map URL-friendly segment names to Groww constants
    segment_map = {
      "cash": "SEGMENT_CASH",
      "fno": "SEGMENT_FNO",
      "commodity": "SEGMENT_COMMODITY",
    }

    groww_segment = segment_map.get(segment.lower())
    if not groww_segment:
      return jsonify({
        "success": False,
        "error": f"Invalid segment. Must be one of: cash, fno, commodity",
      }), 400

    positions = get_positions(user_id=user_id, segment=groww_segment)

    return jsonify({
      "success": True,
      "data": {
        "segment": segment,
        "positions": positions,
        "count": len(positions),
      },
    })
  except Exception as e:
    return jsonify({
      "success": False,
      "error": f"Failed to fetch positions: {str(e)}",
    }), 500
