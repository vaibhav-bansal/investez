"""
SQLite database connection and schema management.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional

from config import BASE_DIR

# Database file path
DB_PATH = BASE_DIR / "investez.db"


def get_connection() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.
    Returns Row objects that can be accessed by column name.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """
    Context manager for database connections.
    Automatically commits and closes the connection.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize the database with required tables."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                name TEXT,
                profile_picture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index on google_id for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_google_id
            ON users(google_id)
        """)

        # Brokers table (catalog of available brokers)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brokers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                broker_id TEXT UNIQUE NOT NULL,
                oauth_enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Check if broker_credentials table exists and needs migration
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='broker_credentials'
        """)
        table_exists = cursor.fetchone()

        if table_exists:
            # Check if totp_secret_encrypted column exists
            cursor.execute("PRAGMA table_info(broker_credentials)")
            columns = {row['name'] for row in cursor.fetchall()}
            if 'totp_secret_encrypted' not in columns:
                print("Migrating broker_credentials table to add TOTP support...")
                # Create new table with updated schema
                cursor.execute("""
                    CREATE TABLE broker_credentials_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        broker_id INTEGER NOT NULL,
                        api_key TEXT NOT NULL,
                        api_secret_encrypted TEXT,
                        totp_secret_encrypted TEXT,
                        access_token_encrypted TEXT,
                        status TEXT DEFAULT 'configured',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (broker_id) REFERENCES brokers(id) ON DELETE CASCADE,
                        UNIQUE(user_id, broker_id)
                    )
                """)
                # Copy existing data
                cursor.execute("""
                    INSERT INTO broker_credentials_new
                    (id, user_id, broker_id, api_key, api_secret_encrypted, access_token_encrypted, status, created_at, updated_at)
                    SELECT id, user_id, broker_id, api_key, api_secret_encrypted, access_token_encrypted, status, created_at, updated_at
                    FROM broker_credentials
                """)
                # Drop old table and rename new one
                cursor.execute("DROP TABLE broker_credentials")
                cursor.execute("ALTER TABLE broker_credentials_new RENAME TO broker_credentials")
        else:
            # Create table with updated schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS broker_credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    broker_id INTEGER NOT NULL,
                    api_key TEXT NOT NULL,
                    api_secret_encrypted TEXT,
                    totp_secret_encrypted TEXT,
                    access_token_encrypted TEXT,
                    status TEXT DEFAULT 'configured',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (broker_id) REFERENCES brokers(id) ON DELETE CASCADE,
                    UNIQUE(user_id, broker_id)
                )
            """)

        # Create indexes for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_broker_credentials_user_id
            ON broker_credentials(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_broker_credentials_broker_id
            ON broker_credentials(broker_id)
        """)

        # Seed brokers table with Kite and Groww
        cursor.execute("""
            INSERT OR IGNORE INTO brokers (name, broker_id, oauth_enabled)
            VALUES ('Zerodha Kite', 'kite', 1)
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO brokers (name, broker_id, oauth_enabled)
            VALUES ('Groww', 'groww', 1)
        """)

        conn.commit()


def reset_db() -> None:
    """Drop all tables and reinitialize. USE WITH CAUTION."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()


# Initialize database on module import
init_db()
