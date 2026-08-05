from flask import Blueprint, jsonify

health_bp = Blueprint("health_bp", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint returning system status and backend version."""
    return jsonify({
        "status": "ok",
        "name": "ABIR's Downloader Backend",
        "version": "3.0.0"
    })
