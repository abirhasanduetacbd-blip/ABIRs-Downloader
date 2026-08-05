"""Central application constants for ABIRs Downloader backend."""

DEFAULT_PORT = 9191
DEFAULT_HOST = "127.0.0.1"
DEFAULT_MAX_FILE_AGE_SECONDS = 600  # 10 minutes
DEFAULT_MAX_FILENAME_LENGTH = 60
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Supported media types
TYPE_VIDEO = "video"
TYPE_AUDIO = "audio"

# Format Identifiers
FMT_BEST = "best"
FMT_MP3_BEST = "mp3_best"
FMT_SPOTIFY_AUDIO = "spotify_audio"

# Spotify Thumbnail Fallback
SPOTIFY_ICON_URL = "https://cdn-icons-png.flaticon.com/512/2111/2111624.png"
