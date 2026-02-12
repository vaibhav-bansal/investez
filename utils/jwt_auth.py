"""
JWT authentication utilities.
"""

import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from typing import Optional, Callable, Any


def get_jwt_secret() -> str:
    """Get JWT secret from environment."""
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise ValueError("JWT_SECRET_KEY not set in environment")
    return secret


def create_token(user_id: int, expires_in_days: int = 30) -> str:
    """
    Create a JWT token for a user.

    Args:
        user_id: User ID to encode in token
        expires_in_days: Token expiration in days (default 30)

    Returns:
        JWT token string
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=expires_in_days),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm="HS256")


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user_id() -> Optional[int]:
    """
    Get current user ID from JWT token in request.
    Checks both Authorization header and session cookie.

    Returns:
        User ID or None if not authenticated
    """
    token = None

    # Check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]

    # Check session cookie
    if not token:
        token = request.cookies.get("session_token")

    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    return payload.get("user_id")


def require_auth(f: Callable) -> Callable:
    """
    Decorator to require authentication for a route.
    Adds user_id to kwargs if authenticated.
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        user_id = get_current_user_id()

        if not user_id:
            return jsonify({
                "success": False,
                "error": "Authentication required",
            }), 401

        # Add user_id to kwargs
        kwargs["user_id"] = user_id
        return f(*args, **kwargs)

    return decorated_function
