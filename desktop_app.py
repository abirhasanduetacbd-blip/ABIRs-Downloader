import sys
import time
import webbrowser
import threading
import subprocess
import os

# Live Cloud Server URL deployed on Render
CLOUD_SERVER_URL = "https://abir-downloader-backend.onrender.com"
LOCAL_SERVER_URL = "http://127.0.0.1:9191"

def check_cloud_server():
    """Check if the cloud server is reachable."""
    try:
        import urllib.request
        req = urllib.request.Request(f"{CLOUD_SERVER_URL}/health", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            return response.status == 200
    except Exception:
        return False

def check_local_server():
    """Check if local server is running."""
    try:
        import urllib.request
        with urllib.request.urlopen(f"{LOCAL_SERVER_URL}/health", timeout=2) as response:
            return response.status == 200
    except Exception:
        return False

def start_local_server():
    """Start local server as fallback if cloud is offline."""
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    server_script = os.path.join(base_dir, "server.py")
    if os.path.exists(server_script):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen([sys.executable, server_script], startupinfo=startupinfo)
        except Exception as e:
            print(f"Server start notice: {e}")

def main():
    print("==================================================")
    print("      ABIR's Downloader Desktop Launcher          ")
    print("==================================================")
    print("Connecting to ABIR's Downloader Cloud Engine...")

    target_url = CLOUD_SERVER_URL

    if not check_cloud_server():
        print("Cloud server sleeping or offline, switching to local engine...")
        if not check_local_server():
            start_local_server()
            time.sleep(2)
        target_url = LOCAL_SERVER_URL

    print(f"Opening App UI at: {target_url}")
    webbrowser.open(target_url)

if __name__ == "__main__":
    main()
