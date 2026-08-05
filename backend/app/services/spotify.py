import re
import requests
import yt_dlp
from typing import Dict, Any, Tuple

SPOTIFY_DEFAULT_THUMBNAIL = "https://cdn-icons-png.flaticon.com/512/2111/2111624.png"

def extract_spotify_metadata(url: str) -> Dict[str, Any]:
    """Scrapes Spotify track webpage title and returns fallback metadata payload."""
    title = "Spotify Media Track"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        title_match = re.search(r'<title>(.*?)</title>', r.text)
        if title_match:
            title = title_match.group(1).replace(" | Spotify", "").replace(" - song and lyrics by ", " - ").strip()
    except Exception:
        pass

    return {
        "success": True,
        "title": title,
        "thumbnail": SPOTIFY_DEFAULT_THUMBNAIL,
        "uploader": "Spotify",
        "duration": "Track",
        "formats": [
            {"id": "spotify_audio", "ext": "mp3", "label": "MP3 High Quality Audio (320 kbps)", "type": "audio", "quality": "320k"}
        ]
    }

def resolve_spotify_to_youtube(url: str) -> str:
    """Extracts track title from Spotify link and performs ytsearch to locate matching YouTube video."""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        title_match = re.search(r'<title>(.*?)</title>', r.text)
        track = title_match.group(1).replace(" | Spotify", "").replace(" - song and lyrics by ", " - ") if title_match else "spotify track"
    except Exception:
        track = "spotify track"

    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
        r = ydl.extract_info(f"ytsearch1:{track}", download=False)
        if r.get("entries"):
            return f"https://www.youtube.com/watch?v={r['entries'][0]['id']}"

    return url
