from flask import Blueprint, request, jsonify, send_file
from backend.app.core.security import validate_and_sanitize_url
from backend.app.services.downloader import process_download

download_bp = Blueprint("download_bp", __name__)

@download_bp.route("/api/download", methods=["GET"])
@download_bp.route("/download", methods=["GET"])
def download_endpoint():
    """Media download and attachment delivery endpoint."""
    raw_url = request.args.get("url", "")
    fmt = request.args.get("format_id", "best")
    typ = request.args.get("type", "video")

    is_valid, url, err_msg = validate_and_sanitize_url(raw_url)
    if not is_valid:
        return jsonify({"error": err_msg}), 400

    try:
        fp, download_filename, mimetype = process_download(url, fmt, typ)
        return send_file(
            fp,
            as_attachment=True,
            download_name=download_filename,
            mimetype=mimetype
        )
    except FileNotFoundError:
        return jsonify({"error": "Downloaded file not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)[:150]}"}), 500
