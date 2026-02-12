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
        "http://127.0.0.1:5000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://dashboard-production-b3df.up.railway.app",
        "https://api-production-9507.up.railway.app",
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
    from .routes.portfolio import portfolio_bp
    from .routes.auth import auth_bp
    from .routes.google_auth import google_auth_bp
    from .routes.brokers import brokers_bp
    from .routes.groww_portfolio import groww_portfolio_bp

    app.register_blueprint(portfolio_bp, url_prefix="/api/portfolio")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(google_auth_bp, url_prefix="/api/auth/google")
    app.register_blueprint(brokers_bp, url_prefix="/api")
    app.register_blueprint(groww_portfolio_bp, url_prefix="/api/groww")

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    return app


# For flask run command
app = create_app()
