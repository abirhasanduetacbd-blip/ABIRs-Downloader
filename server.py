import os
import re
import string
import uuid
import time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import yt_dlp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def cleanup_old_files(max_age_seconds=600):
    """Remove files older than max_age_seconds from downloads folder."""
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
    """Clean filename for OS compatibility."""
    valid = set(string.printable) - set('<>:"/\\|?*')
    name = "".join(c for c in name if c in valid)
    name = name.strip()[:60]
    return name or "video"

@app.route("/", methods=["GET"])
def index():
    web_app_file = os.path.join(os.getcwd(), "android_app", "web_app", "index.html")
    if os.path.exists(web_app_file):
        return send_file(web_app_file)
    return jsonify({"status": "ok", "name": "ABIRs Downloader Server", "version": "2.0.0"})

@app.route("/android_app/web_app/manifest.json", methods=["GET"])
def pwa_manifest():
    manifest_file = os.path.join(os.getcwd(), "android_app", "web_app", "manifest.json")
    if os.path.exists(manifest_file):
        return send_file(manifest_file, mimetype="application/json")
    return jsonify({"error": "Not found"}), 404


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "name": "ABIRs Downloader Backend",
        "version": "2.0.0"
    })


@app.route("/formats", methods=["POST"])
def get_formats():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"success": False, "error": "No URL provided"}), 400

    try:
        if "spotify.com" in url:
            try:
                r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                title_match = re.search(r'<title>(.*?)</title>', r.text)
                title = title_match.group(1).replace(" | Spotify", "").replace(" - song and lyrics by ", " - ") if title_match else "Spotify Track"
            except Exception:
                title = "Spotify Track"
            return jsonify({
                "success": True,
                "formats": [{"id": "spotify", "ext": "mp3", "label": "MP3 Audio (Spotify)", "type": "audio"}],
                "title": title[:80]
            })

        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            fmts = [{"id": "mp3", "ext": "mp3", "label": "MP3 Audio", "type": "audio"}]
            seen = set()
            for f in info.get("formats", []):
                h = f.get("height")
                if h and h >= 144 and h not in seen:
                    seen.add(h)
                    fmts.append({"id": str(h), "ext": "mp4", "label": f"{h}p Video", "type": "video", "h": h})
            vids = sorted([f for f in fmts if f["type"] != "audio"], key=lambda x: x["h"], reverse=True)
            return jsonify({
                "success": True,
                "formats": [{"id": "best", "ext": "mp4", "label": "Best Quality", "type": "video"}, fmts[0]] + vids[:10],
                "title": info.get("title", "Media Content")[:80]
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)[:150]})

@app.route("/download", methods=["GET"])
def download_file():
    cleanup_old_files()
    url = request.args.get("url", "").strip()
    fmt = request.args.get("format_id", "best")
    typ = request.args.get("type", "video")

    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400

    if "spotify.com" in url or fmt == "spotify":
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            title_match = re.search(r'<title>(.*?)</title>', r.text)
            track = title_match.group(1).replace(" | Spotify", "") if title_match else "spotify track"
        except Exception:
            track = "spotify track"
        with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
            r = ydl.extract_info(f"ytsearch1:{track}", download=False)
            if r.get("entries"):
                url = f"https://www.youtube.com/watch?v={r['entries'][0]['id']}"
        fmt, typ = "best", "audio"

    uid = str(uuid.uuid4())[:8]
    tmpl = os.path.join(DOWNLOAD_DIR, uid)
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    if typ == "audio":
        opts = {
            "outtmpl": tmpl,
            "format": "bestaudio/best",
            "quiet": True,
            "http_headers": hdrs,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]
        }
    else:
        fstr = "best[ext=mp4]/best" if fmt == "best" else f"best[height<={fmt}][ext=mp4]/best[height<={fmt}]/best"
        opts = {
            "outtmpl": tmpl,
            "format": fstr,
            "quiet": True,
            "merge_output_format": "mp4",
            "http_headers": hdrs
        }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            name = safe_name(info.get("title", "video"))

        for f in os.listdir(DOWNLOAD_DIR):
            fp = os.path.join(DOWNLOAD_DIR, f)
            if os.path.isfile(fp) and uid in f and not f.endswith('.part') and not f.endswith('.ytdl'):
                ext = ".mp3" if typ == "audio" else ".mp4"
                download_name = f"{name}{ext}"
                print(f"Sending file: {download_name}")
                return send_file(fp, as_attachment=True, download_name=download_name, mimetype="application/octet-stream")

        return jsonify({"error": "File generation failed"}), 404
    except Exception as e:
        print(f"ERROR: {str(e)[:150]}")
        return jsonify({"error": str(e)[:150]}), 500

def start_mdns_service(port):
    """Register abirs-downloader.local on the local network using mDNS Zeroconf."""
    try:
        import socket
        from zeroconf import Zeroconf, ServiceInfo

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        info = ServiceInfo(
            "_http._tcp.local.",
            "ABIRs Downloader._http._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=port,
            properties={"version": "2.0.0"},
            server="abirs-downloader.local."
        )
        zeroconf = Zeroconf()
        zeroconf.register_service(info)
        print(f"mDNS Active: You can also visit http://abirs-downloader.local:{port}")
    except Exception as e:
        print(f"mDNS notice: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9191))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"ABIRs Downloader Server starting on http://{host}:{port}")
    start_mdns_service(port)
    app.run(host=host, port=port, debug=False)


