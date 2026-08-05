from backend.app.api.v1.endpoints.health import health_bp
from backend.app.api.v1.endpoints.analyze import analyze_bp
from backend.app.api.v1.endpoints.download import download_bp
from backend.app.api.v1.endpoints.web_server import web_bp

__all__ = ["health_bp", "analyze_bp", "download_bp", "web_bp"]
