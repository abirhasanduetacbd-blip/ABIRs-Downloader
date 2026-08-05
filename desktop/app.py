import os
import sys
import time
import subprocess
import threading
import webbrowser
import winreg
from PIL import Image, ImageDraw
import pystray
import requests

SERVER_PORT = 9191
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"
server_process = None

def create_tray_icon_image():
    """Create a sleek icon image for the system tray."""
    image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Circle background
    draw.ellipse((4, 4, 60, 60), fill=(99, 102, 241))
    # Down arrow symbol
    draw.polygon([(32, 46), (18, 28), (26, 28), (26, 16), (38, 16), (38, 28), (46, 28)], fill=(255, 255, 255))
    return image

def set_autostart_registry():
    """Add application to Windows Startup Registry."""
    try:
        key = winreg.HKEY_CURRENT_USER
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        exe_path = f'"{os.path.abspath(sys.argv[0])}"'
        with winreg.OpenKey(key, reg_path, 0, winreg.KEY_WRITE) as reg_key:
            winreg.SetValueEx(reg_key, "ABIRsDownloader", 0, winreg.REG_SZ, exe_path)
    except Exception as e:
        print(f"Registry autostart error: {e}")

def run_server_process():
    """Launch server.py in the background."""
    global server_process
    base_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(base_dir, "..", "server.py")
    if not os.path.exists(server_script):
        server_script = os.path.join(base_dir, "server.py")
    
    if os.path.exists(server_script):
        # Hide console window on Windows
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        server_process = subprocess.Popen([sys.executable, server_script], startupinfo=startupinfo)

def check_server():
    try:
        r = requests.get(f"{SERVER_URL}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def open_extension_page(icon, item):
    """Open Chrome extension management page."""
    webbrowser.open("chrome://extensions")

def open_web_interface(icon, item):
    """Open server status / web GUI."""
    webbrowser.open(SERVER_URL + "/health")

def exit_app(icon, item):
    """Exit application and stop background server."""
    global server_process
    if server_process:
        try:
            server_process.terminate()
        except Exception:
            pass
    icon.stop()
    sys.exit(0)

def main():
    set_autostart_registry()
    
    # Start Python backend server if not running
    if not check_server():
        threading.Thread(target=run_server_process, daemon=True).start()
    
    # System Tray Icon setup
    icon_image = create_tray_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem("ABIRs Downloader: Running", lambda i, item: None, enabled=False),
        pystray.MenuItem("Open Server Status", open_web_interface),
        pystray.MenuItem("Setup Chrome/Edge Extension", open_extension_page),
        pystray.MenuItem("Exit", exit_app)
    )
    
    tray_icon = pystray.Icon("ABIRsDownloader", icon_image, "ABIRs Downloader (Active)", menu)
    tray_icon.run()

if __name__ == "__main__":
    main()
