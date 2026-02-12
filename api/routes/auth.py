"""
Authentication API endpoints for Kite Connect and Groww.
"""

import json
from flask import Blueprint, jsonify, request
from kiteconnect import KiteConnect
from growwapi import GrowwAPI

from config import BASE_DIR
from database.db import get_db
from utils.jwt_auth import require_auth, get_current_user_id
from utils.crypto import decrypt_data, encrypt_data

auth_bp = Blueprint("auth", __name__)

# Legacy token storage files (deprecated, kept for backward compatibility)
TOKEN_FILE = BASE_DIR / ".kite_token"
PROFILE_FILE = BASE_DIR / ".kite_profile"


def _get_user_kite_credentials(user_id: int) -> tuple[str, str] | None:
    """
    Get user's Kite API credentials from database.
    Returns (api_key, api_secret) or None if not configured.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bc.api_key, bc.api_secret_encrypted
            FROM broker_credentials bc
            JOIN brokers b ON bc.broker_id = b.id
            WHERE bc.user_id = ? AND b.broker_id = 'kite'
        """, (user_id,))

        row = cursor.fetchone()
        if not row:
            return None

        api_key = row["api_key"]
        api_secret = decrypt_data(row["api_secret_encrypted"])
        return (api_key, api_secret)


def _save_user_access_token(user_id: int, access_token: str) -> None:
    """Save user's Kite access token to database."""
    encrypted_token = encrypt_data(access_token)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE broker_credentials
            SET access_token_encrypted = ?, status = 'authenticated',
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND broker_id = (
                SELECT id FROM brokers WHERE broker_id = 'kite'
            )
        """, (encrypted_token, user_id))
        conn.commit()


def _get_user_access_token(user_id: int) -> str | None:
    """Get user's Kite access token from database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bc.access_token_encrypted
            FROM broker_credentials bc
            JOIN brokers b ON bc.broker_id = b.id
            WHERE bc.user_id = ? AND b.broker_id = 'kite'
        """, (user_id,))

        row = cursor.fetchone()
        if not row or not row["access_token_encrypted"]:
            return None

        return decrypt_data(row["access_token_encrypted"])


def _clear_user_access_token(user_id: int) -> None:
    """Clear user's Kite access token from database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE broker_credentials
            SET access_token_encrypted = NULL, status = 'configured',
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND broker_id = (
                SELECT id FROM brokers WHERE broker_id = 'kite'
            )
        """, (user_id,))
        conn.commit()


def _save_profile(profile_data: dict) -> None:
    """Save user profile data to file."""
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile_data, f)


def _load_profile() -> dict | None:
    """Load user profile data from file."""
    if PROFILE_FILE.exists():
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
    return None


def _delete_profile() -> None:
    """Delete stored profile data."""
    if PROFILE_FILE.exists():
        PROFILE_FILE.unlink()


@auth_bp.route("/status", methods=["GET"])
def get_auth_status():
    """
    Check if Kite is authenticated for current user.
    Returns authenticated status and user info if logged in.
    """
    user_id = get_current_user_id()

    # If no user session, not authenticated
    if not user_id:
        return jsonify({
            "success": True,
            "data": {
                "user_authenticated": False,
                "broker_authenticated": False,
            },
        })

    # Check if user has Kite access token
    access_token = _get_user_access_token(user_id)
    broker_authenticated = access_token is not None

    return jsonify({
        "success": True,
        "data": {
            "user_authenticated": True,
            "broker_authenticated": broker_authenticated,
        },
    })


@auth_bp.route("/login-url", methods=["GET"])
@require_auth
def get_login_url(user_id: int):
    """
    Get Kite login URL for OAuth flow.
    Requires user authentication.
    """
    # Get user's Kite credentials from database
    credentials = _get_user_kite_credentials(user_id)

    if not credentials:
        return jsonify({
            "success": False,
            "error": "Kite credentials not configured. Please add your API key and secret first.",
        }), 400

    api_key, _ = credentials

    try:
        kite = KiteConnect(api_key=api_key)
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
@require_auth
def handle_callback(user_id: int):
    """
    Handle Kite OAuth callback with request token.
    Requires user authentication.

    Expects JSON body: {"request_token": "..."}
    """
    data = request.get_json()
    if not data or "request_token" not in data:
        return jsonify({
            "success": False,
            "error": "request_token is required",
        }), 400

    request_token = data["request_token"]

    # Get user's Kite credentials from database
    credentials = _get_user_kite_credentials(user_id)

    if not credentials:
        return jsonify({
            "success": False,
            "error": "Kite credentials not configured",
        }), 400

    api_key, api_secret = credentials

    try:
        kite = KiteConnect(api_key=api_key)
        session_data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = session_data["access_token"]

        # Save access token to database
        _save_user_access_token(user_id, access_token)

        # Also save to legacy file for backward compatibility
        kite.set_access_token(access_token)
        from tools.kite import _save_token
        _save_token(access_token)

        # Extract and save profile data (legacy)
        profile_data = {
            "user_id": session_data.get("user_id"),
            "user_name": session_data.get("user_name"),
            "user_shortname": session_data.get("user_shortname"),
            "email": session_data.get("email"),
            "user_type": session_data.get("user_type"),
            "broker": session_data.get("broker", "ZERODHA"),
        }
        _save_profile(profile_data)

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


@auth_bp.route("/profile", methods=["GET"])
@require_auth
def get_profile(user_id: int):
    """
    Get broker (Kite) profile information for authenticated user.
    """
    # Check if user has Kite access token
    access_token = _get_user_access_token(user_id)

    if not access_token:
        return jsonify({
            "success": False,
            "error": "Kite not authenticated. Please authenticate with Kite first.",
        }), 404

    # Get credentials to create Kite instance
    credentials = _get_user_kite_credentials(user_id)
    if not credentials:
        return jsonify({
            "success": False,
            "error": "Kite credentials not found",
        }), 404

    api_key, _ = credentials

    try:
        # Fetch profile from Kite API
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        kite_profile = kite.profile()

        profile_data = {
            "user_id": kite_profile.get("user_id"),
            "user_name": kite_profile.get("user_name"),
            "user_shortname": kite_profile.get("user_shortname"),
            "email": kite_profile.get("email"),
            "user_type": kite_profile.get("user_type"),
            "broker": kite_profile.get("broker", "ZERODHA"),
        }

        # Save to legacy file
        _save_profile(profile_data)

        # Add broker connection info
        profile_data["connected_brokers"] = [
            {
                "name": "Kite",
                "broker_id": "kite",
                "user_id": profile_data.get("user_id"),
                "connected": True,
            }
        ]

        return jsonify({
            "success": True,
            "data": profile_data,
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch profile: {str(e)}",
        }), 500


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout(user_id: int):
    """
    Logout broker (Kite) and clear broker session data.
    Does not log out the user from Google.
    """
    try:
        # Clear user's Kite access token from database
        _clear_user_access_token(user_id)

        # Delete legacy token and profile files
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
        _delete_profile()

        # Clear the global kite instance
        from tools import kite as kite_module
        kite_module._kite = None

        return jsonify({
            "success": True,
            "data": {
                "message": "Broker session ended successfully",
            },
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@auth_bp.route("/logout-all", methods=["POST"])
@require_auth
def logout_all_brokers(user_id: int):
    """
    Logout from all brokers and clear all broker session data.
    Does not log out the user from Google.
    """
    try:
        # Clear all broker access tokens for this user
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE broker_credentials
                SET access_token_encrypted = NULL, status = 'configured',
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()

        # Delete legacy token and profile files
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
        _delete_profile()

        # Clear the global kite instance
        from tools import kite as kite_module
        kite_module._kite = None

        return jsonify({
            "success": True,
            "data": {
                "message": "All broker sessions ended successfully",
            },
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


# ============================================================================
# Groww Authentication Routes
# ============================================================================

def _get_user_groww_credentials(user_id: int) -> tuple[str, str] | None:
    """
    Get user's Groww API credentials from database.
    Returns (api_key, api_secret) or None if not configured.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bc.api_key, bc.api_secret_encrypted
            FROM broker_credentials bc
            JOIN brokers b ON bc.broker_id = b.id
            WHERE bc.user_id = ? AND b.broker_id = 'groww'
        """, (user_id,))

        row = cursor.fetchone()
        if not row:
            return None

        api_key = row["api_key"]
        api_secret = decrypt_data(row["api_secret_encrypted"])
        return (api_key, api_secret)


def _save_user_groww_access_token(user_id: int, access_token: str) -> None:
    """Save user's Groww access token to database."""
    encrypted_token = encrypt_data(access_token)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE broker_credentials
            SET access_token_encrypted = ?, status = 'authenticated',
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND broker_id = (
                SELECT id FROM brokers WHERE broker_id = 'groww'
            )
        """, (encrypted_token, user_id))
        conn.commit()


def _get_user_groww_access_token(user_id: int) -> str | None:
    """Get user's Groww access token from database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bc.access_token_encrypted
            FROM broker_credentials bc
            JOIN brokers b ON bc.broker_id = b.id
            WHERE bc.user_id = ? AND b.broker_id = 'groww'
        """, (user_id,))

        row = cursor.fetchone()
        if not row or not row["access_token_encrypted"]:
            return None

        return decrypt_data(row["access_token_encrypted"])


def _clear_user_groww_access_token(user_id: int) -> None:
    """Clear user's Groww access token from database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE broker_credentials
            SET access_token_encrypted = NULL, status = 'configured',
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND broker_id = (
                SELECT id FROM brokers WHERE broker_id = 'groww'
            )
        """, (user_id,))
        conn.commit()


@auth_bp.route("/groww/authenticate", methods=["POST"])
@require_auth
def authenticate_groww(user_id: int):
    """
    Authenticate with Groww using stored API credentials.
    Generates and stores access token.
    """
    # Get user's Groww credentials from database
    credentials = _get_user_groww_credentials(user_id)

    if not credentials:
        return jsonify({
            "success": False,
            "error": "Groww credentials not configured. Please add your API key and secret first.",
        }), 400

    api_key, api_secret = credentials

    try:
        # Generate access token using Groww API
        access_token = GrowwAPI.get_access_token(api_key=api_key, secret=api_secret)

        if not access_token:
            return jsonify({
                "success": False,
                "error": "Failed to generate access token. Please check your credentials.",
            }), 401

        # Save access token to database
        _save_user_groww_access_token(user_id, access_token)

        return jsonify({
            "success": True,
            "data": {
                "message": "Groww authentication successful",
            },
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Authentication failed: {str(e)}",
        }), 401


@auth_bp.route("/groww/logout", methods=["POST"])
@require_auth
def logout_groww(user_id: int):
    """
    Logout from Groww and clear Groww session data.
    """
    try:
        # Clear user's Groww access token from database
        _clear_user_groww_access_token(user_id)

        return jsonify({
            "success": True,
            "data": {
                "message": "Groww session ended successfully",
            },
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500
