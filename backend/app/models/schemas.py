from typing import Dict, Any, Optional

def api_response(success: bool, data: Optional[Any] = None, error: Optional[str] = None) -> Dict[str, Any]:
    """Construct standardized API response envelope."""
    payload: Dict[str, Any] = {"success": success}
    if data is not None:
        payload.update(data if isinstance(data, dict) else {"data": data})
    if error is not None:
        payload["error"] = error
    return payload
