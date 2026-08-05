from flask import Blueprint, request, jsonify
from backend.app.core.security import validate_and_sanitize_url
from backend.app.services.extractor import analyze_media_url

analyze_bp = Blueprint("analyze_bp", __name__)

@analyze_bp.route("/api/analyze", methods=["POST"])
@analyze_bp.route("/formats", methods=["POST"])
def analyze_endpoint():
    """Media format analysis endpoint."""
    data = request.get_json(silent=True) or {}
    raw_url = data.get("url", "")
    
    is_valid, url, err_msg = validate_and_sanitize_url(raw_url)
    if not is_valid:
        return jsonify({"success": False, "error": err_msg}), 400

    try:
        result = analyze_media_url(url)
        return jsonify(result)
    except Exception as e:
        err_str = str(e)
        if "Unsupported URL" in err_str:
            err_str = "Unsupported URL or video is private/unavailable."
        return jsonify({"success": False, "error": err_str[:180]}), 400
