import subprocess
import os
import sys

print("Building ABIRs Downloader Windows Standalone Executable (.exe)...")

base_dir = os.path.dirname(os.path.abspath(__file__))
app_script = os.path.join(base_dir, "windows_app", "app.py")

cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--noconfirm",
    "--onedir",
    "--windowed",
    "--name=ABIRs_Downloader",
    "--add-data=server.py;.",
    "--add-data=extension;extension",
    app_script
]

print("Executing command:", " ".join(cmd))
result = subprocess.run(cmd, cwd=base_dir)

if result.returncode == 0:
    print("SUCCESS! Executable built in dist/ABIRs_Downloader/ABIRs_Downloader.exe")
else:
    print("PyInstaller build failed with code", result.returncode)
