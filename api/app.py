"""
Flask API for Portfolio Dashboard.

Usage:
    flask --app api.app run --port 5000

    Or with hot reload:
    flask --app api.app run --port 5000 --debug
"""

from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
    """Create and configure Flask app."""
    app = Flask(__name__)

    # Enable CORS for frontend domains
    import os
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
    ]

    # Add Railway frontend domains from environment
    dashboard_url = os.getenv("DASHBOARD_URL")
    marketing_url = os.getenv("MARKETING_URL")

    if dashboard_url:
        allowed_origins.append(dashboard_url)
    if marketing_url:
        allowed_origins.append(marketing_url)

    CORS(app, origins=allowed_origins, supports_credentials=True)

    # Register blueprints
    from api.routes.portfolio import portfolio_bp
    from api.routes.auth import auth_bp

    app.register_blueprint(portfolio_bp, url_prefix="/api/portfolio")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    return app


# For flask run command
app = create_app()
