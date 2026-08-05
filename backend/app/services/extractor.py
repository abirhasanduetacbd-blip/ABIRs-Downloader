import yt_dlp
from typing import Dict, Any
from backend.app.services.spotify import extract_spotify_metadata
from backend.app.utils.formatter import format_duration

def analyze_media_url(url: str) -> Dict[str, Any]:
    """Parses media URL using yt-dlp and returns extracted metadata & format options."""
    if "spotify.com" in url:
        return extract_spotify_metadata(url)

    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        title = info.get("title") or "Media Content"
        thumbnail = info.get("thumbnail") or ""
        uploader = info.get("uploader") or info.get("channel") or info.get("extractor_key") or "Web Video"
        duration = format_duration(info.get("duration"))
        
        formats_list = []
        
        # Audio formats option
        formats_list.append({
            "id": "mp3_best",
            "ext": "mp3",
            "label": "🎵 MP3 Audio (Best Quality)",
            "type": "audio",
            "quality": "best"
        })

        # Video resolution options
        seen_heights = set()
        raw_formats = info.get("formats", [])
        
        for f in raw_formats:
            h = f.get("height")
            vcodec = f.get("vcodec", "none")
            if h and h >= 144 and h not in seen_heights and vcodec != "none":
                seen_heights.add(h)
                label = f"🎬 {h}p HD Video (MP4)" if h >= 720 else f"🎬 {h}p Video (MP4)"
                formats_list.append({
                    "id": str(h),
                    "ext": "mp4",
                    "label": label,
                    "type": "video",
                    "height": h
                })

        # Sort video formats descending by resolution
        v_formats = [f for f in formats_list if f["type"] == "video"]
        v_formats.sort(key=lambda x: x.get("height", 0), reverse=True)

        # Fallback best video option
        best_video = {
            "id": "best",
            "ext": "mp4",
            "label": "⚡ Best Quality MP4 (Auto)",
            "type": "video",
            "height": 9999
        }
        
        final_formats = [best_video] + [f for f in formats_list if f["type"] == "audio"] + v_formats[:6]

        return {
            "success": True,
            "title": title[:100],
            "thumbnail": thumbnail,
            "uploader": uploader,
            "duration": duration,
            "formats": final_formats
        }
