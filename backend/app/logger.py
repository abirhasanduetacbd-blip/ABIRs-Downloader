import os
import logging
from backend.app.core.config import get_config

config = get_config()

# Ensure backend/logs directory exists
LOGS_DIR = os.path.join(config.BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOGS_DIR, "app.log")

# Configure central logger
logger = logging.getLogger("abirs_downloader")
logger.setLevel(logging.INFO)

if not logger.handlers:
    # 1. Console Stream Handler
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_format = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # 2. File Handler
    try:
        f_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        f_handler.setLevel(logging.INFO)
        f_format = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s")
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
    except Exception as e:
        logger.warning(f"Could not initialize file log handler at {LOG_FILE_PATH}: {e}")

def get_logger() -> logging.Logger:
    """Returns the central application logger instance."""
    return logger
