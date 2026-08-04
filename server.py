import os
import re
import string
import uuid
import time
import webbrowser
import threading
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import requests
import yt_dlp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def cleanup_old_files(max_age_seconds=600):
    """Remove temporary files older than max_age_seconds."""
    try:
        now = time.time()
        for f in os.listdir(DOWNLOAD_DIR):
            fp = os.path.join(DOWNLOAD_DIR, f)
            if os.path.isfile(fp) and (now - os.path.getmtime(fp) > max_age_seconds):
                try:
                    os.remove(fp)
                except Exception:
                    pass
    except Exception:
        pass

def safe_name(name):
    """Sanitize file name for Windows OS compatibility."""
    valid = set(string.printable) - set('<>:"/\\|?*')
    name = "".join(c for c in name if c in valid)
    name = name.strip()[:60]
    return name or "downloaded_media"

def format_duration(seconds):
    if not seconds or not isinstance(seconds, (int, float)):
        return ""
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

@app.route("/", methods=["GET"])
def index():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return send_file(index_path)
    return "ABIR's Downloader Server is running. Please ensure index.html is present in the application directory."

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "name": "ABIR's Downloader Backend",
        "version": "3.0.0"
    })

@app.route("/api/analyze", methods=["POST"])
@app.route("/formats", methods=["POST"])
def analyze_url():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"success": False, "error": "Please enter a valid media URL"}), 400

    try:
        # Handle Spotify links by extracting title and searching YouTube
        if "spotify.com" in url:
            title = "Spotify Media Track"
            thumbnail = "https://cdn-icons-png.flaticon.com/512/2111/2111624.png"
            try:
                r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                title_match = re.search(r'<title>(.*?)</title>', r.text)
                if title_match:
                    title = title_match.group(1).replace(" | Spotify", "").replace(" - song and lyrics by ", " - ").strip()
            except Exception:
                pass
            
            return jsonify({
                "success": True,
                "title": title,
                "thumbnail": thumbnail,
                "uploader": "Spotify",
                "duration": "Track",
                "formats": [
                    {"id": "spotify_audio", "ext": "mp3", "label": "MP3 High Quality Audio (320 kbps)", "type": "audio", "quality": "320k"}
                ]
            })

        # Process with yt-dlp
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
            
            # Audio formats
            formats_list.append({
                "id": "mp3_best",
                "ext": "mp3",
                "label": "🎵 MP3 Audio (Best Quality)",
                "type": "audio",
                "quality": "best"
            })

            # Video formats
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

            return jsonify({
                "success": True,
                "title": title[:100],
                "thumbnail": thumbnail,
                "uploader": uploader,
                "duration": duration,
                "formats": final_formats
            })

    except Exception as e:
        err_msg = str(e)
        if "Unsupported URL" in err_msg:
            err_msg = "Unsupported URL or video is private/unavailable."
        return jsonify({"success": False, "error": err_msg[:180]}), 400

@app.route("/api/download", methods=["GET"])
@app.route("/download", methods=["GET"])
def download_file():
    cleanup_old_files()
    url = request.args.get("url", "").strip()
    fmt = request.args.get("format_id", "best")
    typ = request.args.get("type", "video")

    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400

    # Spotify link handling: search YouTube for matching track
    if "spotify.com" in url or fmt == "spotify_audio":
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            title_match = re.search(r'<title>(.*?)</title>', r.text)
            track = title_match.group(1).replace(" | Spotify", "").replace(" - song and lyrics by ", " - ") if title_match else "spotify track"
        except Exception:
            track = "spotify track"
        with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
            r = ydl.extract_info(f"ytsearch1:{track}", download=False)
            if r.get("entries"):
                url = f"https://www.youtube.com/watch?v={r['entries'][0]['id']}"
        fmt, typ = "best", "audio"

    uid = str(uuid.uuid4())[:8]
    output_template = os.path.join(DOWNLOAD_DIR, f"{uid}_%(title)s.%(ext)s")
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

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_title = info.get("title", "download")
            clean_title = safe_name(raw_title)

        # Locate downloaded file
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(uid):
                fp = os.path.join(DOWNLOAD_DIR, f)
                if os.path.isfile(fp) and not f.endswith('.part') and not f.endswith('.ytdl'):
                    ext = ".mp3" if typ == "audio" else ".mp4"
                    download_filename = f"{clean_title}{ext}"
                    mimetype = "audio/mpeg" if typ == "audio" else "video/mp4"
                    return send_file(
                        fp,
                        as_attachment=True,
                        download_name=download_filename,
                        mimetype=mimetype
                    )

        return jsonify({"error": "Downloaded file not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)[:150]}"}), 500

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:9191")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9191))
    host = os.environ.get("HOST", "127.0.0.1")
    print("\n==================================================")
    print("ABIR's Downloader App is running!")
    print(f"Access Web UI: http://127.0.0.1:{port}")
    print("==================================================\n")
    
    # Auto launch browser in local desktop mode
    if host in ["127.0.0.1", "localhost"]:
        threading.Thread(target=open_browser, daemon=True).start()

    app.run(host=host, port=port, debug=False)

