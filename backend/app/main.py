import sys
import os
import time
import webbrowser
import threading
from flask import Flask, jsonify
from flask_cors import CORS

# Bootstrap repository root into sys.path to allow direct script execution
_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from backend.app.core.config import get_config
from backend.app.logger import get_logger
from backend.app.exceptions import DownloaderBaseException
from backend.app.routes import register_routes

config = get_config()
logger = get_logger()

def create_app() -> Flask:
    """Application factory for modular Flask server."""
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": config.ALLOWED_ORIGINS}})
    
    # Register all API and Web Blueprints via routes module
    register_routes(app)

    # Central Error Handlers
    @app.errorhandler(DownloaderBaseException)
    def handle_downloader_exception(error: DownloaderBaseException):
        logger.warning(f"Domain Exception [{error.status_code}]: {error.message}")
        return jsonify({"success": False, "error": error.message}), error.status_code

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        logger.error(f"Unhandled Exception: {str(error)}")
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    
    return app

app = create_app()

def open_browser():
    """Auto launch default web browser in local desktop mode."""
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{config.PORT}")

if __name__ == "__main__":
    logger.info("==================================================")
    logger.info("ABIR's Downloader Modular Backend (Development Target)")
    logger.info(f"Access Web UI: http://127.0.0.1:{config.PORT}")
    logger.info("==================================================\n")
    
    # Auto launch browser in local desktop mode
    if config.HOST in ["127.0.0.1", "localhost"]:
        threading.Thread(target=open_browser, daemon=True).start()

    app.run(host=config.HOST, port=config.PORT, debug=False)
