import os
from dataclasses import dataclass

# Attempt to load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass(frozen=True)
class Config:
    """Immutable application configuration manager."""
    # Base directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DOWNLOAD_DIR: str = os.getenv("DOWNLOAD_DIR", os.path.join(BASE_DIR, "downloads"))
    WEB_DIR: str = os.getenv("WEB_DIR", os.path.join(BASE_DIR, "..", "web"))
    ROOT_DIR: str = os.path.dirname(BASE_DIR)
    
    # Environment & Application Mode
    APP_MODE: str = os.getenv("APP_MODE", "local")  # 'local' or 'cloud'
    
    # Server network settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 9191))
    
    # Executable paths
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    
    # Security & Cleanup settings
    MAX_FILE_AGE: int = int(os.getenv("MAX_FILE_AGE", 600))  # 10 minutes (600 seconds)
    MAX_FILENAME_LENGTH: int = int(os.getenv("MAX_FILENAME_LENGTH", 60))
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")

# Ensure required runtime directories exist
_config_instance = Config()
os.makedirs(_config_instance.DOWNLOAD_DIR, exist_ok=True)

def get_config() -> Config:
    """Returns the application configuration singleton."""
    return _config_instance
