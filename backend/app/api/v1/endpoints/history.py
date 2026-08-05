from flask import Blueprint, request, jsonify
from backend.app.services import job_service

history_bp = Blueprint("history_bp", __name__)

@history_bp.route("/api/v1/history", methods=["GET"])
def get_history_endpoint():
    """Retrieves download history list."""
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))
    
    history_items = job_service.list_history(limit=limit, offset=offset)
    return jsonify({
        "success": True,
        "data": history_items
    })

@history_bp.route("/api/v1/history/<int:history_id>", methods=["DELETE"])
def delete_history_item_endpoint(history_id: int):
    """Deletes a single history record."""
    deleted = job_service.clear_history(history_id)
    if deleted:
        return jsonify({"success": True, "message": "History item deleted"})
    return jsonify({"success": False, "error": "History item not found"}), 404

@history_bp.route("/api/v1/history/clear", methods=["DELETE"])
def clear_all_history_endpoint():
    """Clears all download history records."""
    job_service.clear_history(history_id=None)
    return jsonify({"success": True, "message": "All download history cleared"})
