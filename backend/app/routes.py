"""Central routes aggregator module for ABIRs Downloader backend.

Imports and registers all endpoint blueprints.
"""
from flask import Flask
from backend.app.api.v1.endpoints.health import health_bp
from backend.app.api.v1.endpoints.analyze import analyze_bp
from backend.app.api.v1.endpoints.download import download_bp
from backend.app.api.v1.endpoints.web_server import web_bp
from backend.app.api.v1.endpoints.jobs import jobs_bp
from backend.app.api.v1.endpoints.history import history_bp

def register_routes(app: Flask) -> None:
    """Registers all application blueprints with the Flask instance."""
    app.register_blueprint(health_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(history_bp)
