import os
from flask import Blueprint, request, jsonify, send_file
from backend.app.core.security import validate_and_sanitize_url, is_safe_path
from backend.app.workers.job_worker import start_download_job
from backend.app.services import job_service
from backend.app.models.job import JobStatus
from backend.app.core.config import get_config

config = get_config()
jobs_bp = Blueprint("jobs_bp", __name__)

@jobs_bp.route("/api/v1/jobs", methods=["POST"])
def create_job_endpoint():
    """Submits a new non-blocking background download job."""
    data = request.get_json(silent=True) or {}
    raw_url = data.get("url", "")
    fmt = data.get("format_id", "best")
    media_type = data.get("media_type", "video")

    is_valid, url, err_msg = validate_and_sanitize_url(raw_url)
    if not is_valid:
        return jsonify({"success": False, "error": err_msg}), 400

    try:
        job = start_download_job(url=url, format_id=fmt, media_type=media_type)
        return jsonify({
            "success": True,
            "data": job
        }), 202
    except Exception as e:
        return jsonify({"success": False, "error": str(e)[:180]}), 500

@jobs_bp.route("/api/v1/jobs/<job_id>", methods=["GET"])
def get_job_status_endpoint(job_id: str):
    """Retrieves real-time status and progress for a download job."""
    job = job_service.get_job_by_id(job_id)
    if not job:
        return jsonify({"success": False, "error": "Job not found"}), 404
        
    return jsonify({
        "success": True,
        "data": job
    })

@jobs_bp.route("/api/v1/jobs/<job_id>", methods=["DELETE"])
def cancel_job_endpoint(job_id: str):
    """Cancels a pending or running download job."""
    cancelled = job_service.cancel_job(job_id)
    if cancelled:
        return jsonify({"success": True, "message": f"Job {job_id} cancelled"})
    return jsonify({"success": False, "error": "Job not found or already completed/failed"}), 400

@jobs_bp.route("/api/v1/jobs/<job_id>/stream", methods=["GET"])
def stream_file_endpoint(job_id: str):
    """Streams attachment file for a completed download job."""
    job = job_service.get_job_by_id(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.get("status") != JobStatus.COMPLETED:
        return jsonify({"error": f"Job status is '{job.get('status')}'. File not ready for streaming."}), 400

    file_path = job.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "File no longer exists on disk"}), 404

    if not is_safe_path(config.DOWNLOAD_DIR, file_path):
        return jsonify({"error": "Path traversal prohibited"}), 403

    mimetype = "audio/mpeg" if job.get("media_type") == "audio" else "video/mp4"
    return send_file(
        file_path,
        as_attachment=True,
        download_name=job.get("file_name", "downloaded_media"),
        mimetype=mimetype
    )
