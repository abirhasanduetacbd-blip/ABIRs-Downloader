import os
from flask import Blueprint, send_file, jsonify
from backend.app.core.config import get_config

config = get_config()
web_bp = Blueprint("web_bp", __name__)

def _find_web_asset(filename: str) -> str:
    """Checks web/ single source directory first, then root fallback."""
    web_path = os.path.join(config.WEB_DIR, filename)
    if os.path.exists(web_path):
        return web_path
    root_path = os.path.join(config.ROOT_DIR, filename)
    if os.path.exists(root_path):
        return root_path
    base_path = os.path.join(config.BASE_DIR, filename)
    if os.path.exists(base_path):
        return base_path
    return ""

@web_bp.route("/", methods=["GET"])
def index():
    """Serves primary web application interface."""
    path = _find_web_asset("index.html")
    if path:
        return send_file(path)
    return "ABIR's Downloader Server is running. Please ensure index.html is present in the application directory."

@web_bp.route("/manifest.json", methods=["GET"])
def manifest():
    """Serves PWA manifest.json."""
    path = _find_web_asset("manifest.json")
    if path:
        return send_file(path, mimetype="application/json")
    return jsonify({"error": "Manifest not found"}), 404

@web_bp.route("/sw.js", methods=["GET"])
def service_worker():
    """Serves PWA service worker script."""
    path = _find_web_asset("sw.js")
    if path:
        return send_file(path, mimetype="application/javascript")
    return jsonify({"error": "Service worker not found"}), 404
