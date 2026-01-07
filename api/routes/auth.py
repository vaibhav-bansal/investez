"""
Authentication API endpoints for Kite Connect.
"""

from flask import Blueprint, jsonify, request
from kiteconnect import KiteConnect

from config import KITE_API_KEY, KITE_API_SECRET, BASE_DIR
from tools.kite import is_authenticated, get_kite, _save_token

auth_bp = Blueprint("auth", __name__)

# Token storage file
TOKEN_FILE = BASE_DIR / ".kite_token"


@auth_bp.route("/status", methods=["GET"])
def get_auth_status():
    """
    Check if Kite is authenticated.
    """
    authenticated = is_authenticated()
    return jsonify({
        "success": True,
        "data": {
            "authenticated": authenticated,
        },
    })


@auth_bp.route("/login-url", methods=["GET"])
def get_login_url():
    """
    Get Kite login URL for OAuth flow.
    """
    if not KITE_API_KEY:
        return jsonify({
            "success": False,
            "error": "Kite API key not configured",
        }), 500

    try:
        kite = KiteConnect(api_key=KITE_API_KEY)
        login_url = kite.login_url()
        return jsonify({
            "success": True,
            "data": {
                "login_url": login_url,
            },
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@auth_bp.route("/callback", methods=["POST"])
def handle_callback():
    """
    Handle Kite OAuth callback with request token.

    Expects JSON body: {"request_token": "..."}
    """
    data = request.get_json()
    if not data or "request_token" not in data:
        return jsonify({
            "success": False,
            "error": "request_token is required",
        }), 400

    request_token = data["request_token"]

    try:
        kite = KiteConnect(api_key=KITE_API_KEY)
        session_data = kite.generate_session(request_token, api_secret=KITE_API_SECRET)
        access_token = session_data["access_token"]

        kite.set_access_token(access_token)
        _save_token(access_token)

        # Update the global kite instance
        from tools import kite as kite_module
        kite_module._kite = kite

        return jsonify({
            "success": True,
            "data": {
                "message": "Authentication successful",
            },
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 401
