import os
import uuid
import time
import yt_dlp
from typing import Tuple, Dict, Any
from backend.app.core.config import get_config
from backend.app.utils.sanitizer import safe_name
from backend.app.services.spotify import resolve_spotify_to_youtube

config = get_config()

def cleanup_old_files(max_age_seconds: int = 600) -> int:
    """Remove temporary files older than max_age_seconds."""
    deleted_count = 0
    try:
        now = time.time()
        for f in os.listdir(config.DOWNLOAD_DIR):
            fp = os.path.join(config.DOWNLOAD_DIR, f)
            if os.path.isfile(fp) and (now - os.path.getmtime(fp) > max_age_seconds):
                try:
                    os.remove(fp)
                    deleted_count += 1
                except Exception:
                    pass
    except Exception:
        pass
    return deleted_count

def process_download(url: str, fmt: str = "best", typ: str = "video") -> Tuple[str, str, str]:
    """Executes yt-dlp media download and returns (file_path, download_filename, mimetype)."""
    cleanup_old_files(config.MAX_FILE_AGE)

    # Handle Spotify link resolution
    if "spotify.com" in url or fmt == "spotify_audio":
        url = resolve_spotify_to_youtube(url)
        fmt, typ = "best", "audio"

    uid = str(uuid.uuid4())[:8]
    output_template = os.path.join(config.DOWNLOAD_DIR, f"{uid}_%(title)s.%(ext)s")
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    if typ == "audio":
        opts = {
            "outtmpl": output_template,
            "format": "bestaudio/best",
            "quiet": True,
            "http_headers": hdrs,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320"
            }]
        }
    else:
        if fmt == "best" or not fmt.isdigit():
            fstr = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        else:
            fstr = f"bestvideo[height<={fmt}][ext=mp4]+bestaudio[ext=m4a]/best[height<={fmt}][ext=mp4]/best"
            
        opts = {
            "outtmpl": output_template,
            "format": fstr,
            "quiet": True,
            "merge_output_format": "mp4",
            "http_headers": hdrs
        }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        raw_title = info.get("title", "download")
        clean_title = safe_name(raw_title, config.MAX_FILENAME_LENGTH)

    # Locate downloaded file
    for f in os.listdir(config.DOWNLOAD_DIR):
        if f.startswith(uid):
            fp = os.path.join(config.DOWNLOAD_DIR, f)
            if os.path.isfile(fp) and not f.endswith('.part') and not f.endswith('.ytdl'):
                ext = ".mp3" if typ == "audio" else ".mp4"
                download_filename = f"{clean_title}{ext}"
                mimetype = "audio/mpeg" if typ == "audio" else "video/mp4"
                return fp, download_filename, mimetype

    raise FileNotFoundError("Downloaded file not found on disk after extraction")
