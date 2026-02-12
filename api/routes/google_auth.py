"""
Google OAuth authentication API endpoints.
"""

import os
import requests
from flask import Blueprint, jsonify, request, make_response
from urllib.parse import urlencode

from database.db import get_db
from utils.jwt_auth import create_token, get_current_user_id

google_auth_bp = Blueprint("google_auth", __name__)

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
API_BASE_URL = os.getenv("API_BASE_URL")  # Production API server URL

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_redirect_uri() -> str:
    """
    Get the OAuth redirect URI based on environment.

    - In dev: Uses FRONTEND_URL (localhost:3000) which proxies to Flask backend
    - In production: Uses API_BASE_URL (actual API server) since frontend is static
    """
    if API_BASE_URL:
        # Production: Use API server URL directly
        return f"{API_BASE_URL}/api/auth/google/callback"
    else:
        # Dev: Use frontend URL which proxies /api/* to backend
        return f"{FRONTEND_URL}/api/auth/google/callback"


@google_auth_bp.route("/login", methods=["GET"])
def google_login():
    """
    Initiate Google OAuth flow.
    Returns Google authorization URL for frontend to redirect to.
    """
    if not GOOGLE_CLIENT_ID:
        return jsonify({
            "success": False,
            "error": "Google OAuth not configured. Set GOOGLE_CLIENT_ID in environment.",
        }), 500

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": get_redirect_uri(),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",
    }

    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    return jsonify({
        "success": True,
        "data": {
            "auth_url": auth_url,
        },
    })


@google_auth_bp.route("/callback", methods=["GET"])
def google_callback():
    """
    Handle Google OAuth callback.
    Exchanges code for tokens, creates/updates user, and sets session cookie.
    """
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        # Redirect to frontend with error
        return f"""
        <html>
            <body>
                <script>
                    window.opener.postMessage({{ type: 'GOOGLE_AUTH_ERROR', error: '{error}' }}, '{FRONTEND_URL}');
                    window.close();
                </script>
            </body>
        </html>
        """

    if not code:
        return jsonify({
            "success": False,
            "error": "Authorization code not provided",
        }), 400

    try:
        # Exchange code for access token
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": get_redirect_uri(),
            "grant_type": "authorization_code",
        }

        token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()

        access_token = tokens.get("access_token")
        if not access_token:
            raise Exception("No access token in response")

        # Get user info from Google
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()

        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")

        if not google_id or not email:
            raise Exception("Invalid user info from Google")

        # Create or update user in database
        with get_db() as conn:
            cursor = conn.cursor()

            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE google_id = ?", (google_id,))
            existing_user = cursor.fetchone()

            if existing_user:
                # Update existing user
                user_id = existing_user["id"]
                cursor.execute("""
                    UPDATE users
                    SET email = ?, name = ?, profile_picture = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (email, name, picture, user_id))
            else:
                # Create new user
                cursor.execute("""
                    INSERT INTO users (google_id, email, name, profile_picture)
                    VALUES (?, ?, ?, ?)
                """, (google_id, email, name, picture))
                user_id = cursor.lastrowid

            conn.commit()

        # Create JWT token
        jwt_token = create_token(user_id)

        # Redirect to frontend with token
        # Use postMessage to send token to opener window, then close popup
        response_html = f"""
        <html>
            <body>
                <script>
                    window.opener.postMessage({{
                        type: 'GOOGLE_AUTH_SUCCESS',
                        token: '{jwt_token}'
                    }}, '{FRONTEND_URL}');
                    window.close();
                </script>
                <p>Authentication successful! This window will close automatically...</p>
            </body>
        </html>
        """

        response = make_response(response_html)
        # Also set as httpOnly cookie for security
        response.set_cookie(
            "session_token",
            jwt_token,
            httponly=True,
            secure=request.scheme == "https",
            samesite="Lax",
            max_age=30 * 24 * 60 * 60,  # 30 days
        )

        return response

    except Exception as e:
        error_msg = str(e)
        return f"""
        <html>
            <body>
                <script>
                    window.opener.postMessage({{
                        type: 'GOOGLE_AUTH_ERROR',
                        error: '{error_msg}'
                    }}, '{FRONTEND_URL}');
                    window.close();
                </script>
            </body>
        </html>
        """


@google_auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """
    Get current authenticated user info.
    """
    user_id = get_current_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "error": "Not authenticated",
        }), 401

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, google_id, email, name, profile_picture, created_at
            FROM users
            WHERE id = ?
        """, (user_id,))
        user = cursor.fetchone()

    if not user:
        return jsonify({
            "success": False,
            "error": "User not found",
        }), 404

    return jsonify({
        "success": True,
        "data": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "profile_picture": user["profile_picture"],
            "created_at": user["created_at"],
        },
    })


@google_auth_bp.route("/logout", methods=["POST"])
def google_logout():
    """
    Logout current user by clearing session cookie.
    """
    response = make_response(jsonify({
        "success": True,
        "data": {
            "message": "Logged out successfully",
        },
    }))

    # Clear session cookie
    response.set_cookie(
        "session_token",
        "",
        httponly=True,
        secure=request.scheme == "https",
        samesite="Lax",
        max_age=0,  # Expire immediately
    )

    return response
