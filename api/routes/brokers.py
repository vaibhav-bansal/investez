"""
Broker credentials management API endpoints.
"""

from flask import Blueprint, jsonify, request

from database.db import get_db
from utils.jwt_auth import require_auth
from utils.crypto import encrypt_data, decrypt_data

brokers_bp = Blueprint("brokers", __name__)


@brokers_bp.route("/brokers", methods=["GET"])
@require_auth
def get_brokers(user_id: int):
    """
    Get list of all available brokers with user's configuration status.
    """
    # Get broker user_id from profile if authenticated
    from api.routes.auth import _load_profile
    profile = _load_profile()
    broker_user_id = profile.get("user_id") if profile else None

    with get_db() as conn:
        cursor = conn.cursor()

        # Get all brokers with user's credential status
        cursor.execute("""
            SELECT
                b.id,
                b.name,
                b.broker_id,
                b.oauth_enabled,
                CASE
                    WHEN bc.id IS NULL THEN 'unconfigured'
                    ELSE bc.status
                END as status,
                CASE
                    WHEN bc.id IS NOT NULL THEN 1
                    ELSE 0
                END as has_credentials
            FROM brokers b
            LEFT JOIN broker_credentials bc
                ON b.id = bc.broker_id AND bc.user_id = ?
            ORDER BY b.name
        """, (user_id,))

        brokers = []
        for row in cursor.fetchall():
            broker_data = {
                "id": row["id"],
                "name": row["name"],
                "broker_id": row["broker_id"],
                "oauth_enabled": bool(row["oauth_enabled"]),
                "status": row["status"],
                "has_credentials": bool(row["has_credentials"]),
            }

            # Add broker user_id if authenticated
            if row["status"] == "authenticated" and broker_user_id:
                broker_data["user_id"] = broker_user_id

            brokers.append(broker_data)

    return jsonify({
        "success": True,
        "data": {
            "brokers": brokers,
        },
    })


@brokers_bp.route("/brokers/<broker_id>/credentials", methods=["GET"])
@require_auth
def get_broker_credentials_status(user_id: int, broker_id: str):
    """
    Check if user has configured credentials for a broker.
    Does not return actual credentials, just status.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get broker
        cursor.execute("SELECT id, name FROM brokers WHERE broker_id = ?", (broker_id,))
        broker = cursor.fetchone()

        if not broker:
            return jsonify({
                "success": False,
                "error": "Broker not found",
            }), 404

        # Check if user has credentials
        cursor.execute("""
            SELECT id, status, created_at, updated_at
            FROM broker_credentials
            WHERE user_id = ? AND broker_id = ?
        """, (user_id, broker["id"]))

        creds = cursor.fetchone()

        if not creds:
            return jsonify({
                "success": True,
                "data": {
                    "configured": False,
                    "status": "unconfigured",
                },
            })

        return jsonify({
            "success": True,
            "data": {
                "configured": True,
                "status": creds["status"],
                "created_at": creds["created_at"],
                "updated_at": creds["updated_at"],
            },
        })


@brokers_bp.route("/brokers/<broker_id>/credentials", methods=["POST"])
@require_auth
def save_broker_credentials(user_id: int, broker_id: str):
    """
    Save or update broker credentials for user.

    Expects JSON body:
    {
        "api_key": "...",
        "api_secret": "..."
    }
    """
    data = request.get_json()

    if not data or "api_key" not in data or "api_secret" not in data:
        return jsonify({
            "success": False,
            "error": "api_key and api_secret are required",
        }), 400

    api_key = data["api_key"].strip()
    api_secret = data["api_secret"].strip()

    if not api_key or not api_secret:
        return jsonify({
            "success": False,
            "error": "api_key and api_secret cannot be empty",
        }), 400

    try:
        # Encrypt the API secret
        encrypted_secret = encrypt_data(api_secret)

        with get_db() as conn:
            cursor = conn.cursor()

            # Get broker ID
            cursor.execute("SELECT id FROM brokers WHERE broker_id = ?", (broker_id,))
            broker = cursor.fetchone()

            if not broker:
                return jsonify({
                    "success": False,
                    "error": "Broker not found",
                }), 404

            # Check if credentials already exist
            cursor.execute("""
                SELECT id FROM broker_credentials
                WHERE user_id = ? AND broker_id = ?
            """, (user_id, broker["id"]))

            existing = cursor.fetchone()

            if existing:
                # Update existing credentials
                cursor.execute("""
                    UPDATE broker_credentials
                    SET api_key = ?, api_secret_encrypted = ?,
                        status = 'configured', updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND broker_id = ?
                """, (api_key, encrypted_secret, user_id, broker["id"]))
            else:
                # Insert new credentials
                cursor.execute("""
                    INSERT INTO broker_credentials
                    (user_id, broker_id, api_key, api_secret_encrypted, status)
                    VALUES (?, ?, ?, ?, 'configured')
                """, (user_id, broker["id"], api_key, encrypted_secret))

            conn.commit()

        return jsonify({
            "success": True,
            "data": {
                "message": "Credentials saved successfully",
                "status": "configured",
            },
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to save credentials: {str(e)}",
        }), 500


@brokers_bp.route("/brokers/<broker_id>/credentials", methods=["DELETE"])
@require_auth
def delete_broker_credentials(user_id: int, broker_id: str):
    """
    Delete broker credentials for user.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get broker ID
        cursor.execute("SELECT id FROM brokers WHERE broker_id = ?", (broker_id,))
        broker = cursor.fetchone()

        if not broker:
            return jsonify({
                "success": False,
                "error": "Broker not found",
            }), 404

        # Delete credentials
        cursor.execute("""
            DELETE FROM broker_credentials
            WHERE user_id = ? AND broker_id = ?
        """, (user_id, broker["id"]))

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "error": "No credentials found to delete",
            }), 404

        conn.commit()

    return jsonify({
        "success": True,
        "data": {
            "message": "Credentials deleted successfully",
        },
    })
