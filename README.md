# 🚀 ABIRs Downloader - Ready-to-Use Cross-Platform App & Extension

ABIRs Downloader is a complete cross-platform video & audio downloading suite supporting **YouTube, Facebook, Instagram, and Spotify**. It is built for **Windows Desktop** and **Android Mobile Phones**, featuring automatic startup, browser extension integration, and cloud backend support.

---

## 🌟 Architecture & Features

1. **Windows Desktop App (`.exe`)**:
   - Runs silently in the system tray.
   - Automatically starts when Windows boots up (Registry integration).
   - Starts the download engine on `http://127.0.0.1:9191`.
   - 1-Click setup for Chrome & Edge extensions.

2. **Android App (Mobile APK & Share Target)**:
   - Native Android Share Target integration (`android.intent.action.SEND`).
   - Tap **"Share"** on YouTube, Facebook, Instagram, or Spotify -> Select **ABIRs Downloader** -> Auto-fetches and downloads!
   - Mobile-optimized responsive dark UI.

3. **Chrome / Edge Extension (Manifest V3)**:
   - Auto-detects media links on active tabs.
   - Quality/Resolution selector (1080p, 720p, 480p, MP3 Audio).
   - Configurable Backend URL (Local `http://127.0.0.1:9191` or Cloud Server).

4. **1-Click Cloud Deployment**:
   - `Dockerfile`, `Procfile`, `render.yaml`, `requirements.txt` included.
   - Ready to deploy on Render, Railway, HuggingFace, or Heroku so users can download without running a local PC server!

---

## 🪟 Windows Desktop Setup

### Option 1: Run Pre-built Executable
1. Open the `dist/ABIRs_Downloader/` folder.
2. Double-click `ABIRs_Downloader.exe`.
3. An icon will appear in your **Windows System Tray** (near the clock).
4. The background server is now active and will auto-start whenever your PC turns on.

### Option 2: Setup Chrome/Edge Extension
1. Open Chrome/Edge and navigate to `chrome://extensions`.
2. Turn on **Developer mode** (top-right toggle).
3. Click **Load unpacked**.
4. Select the `extension` folder in this repository.

---

## 📱 Android App Setup

### How to Install & Use on Android
1. Build the APK using Android Studio or PWA tool using the files in `android_app/`.
2. Install the `ABIRs_Downloader.apk` on your Android phone.
3. **Usage**:
   - Open YouTube / Facebook / Instagram / Spotify.
   - Tap **Share** -> Choose **ABIRs Downloader**.
   - The app will automatically open, extract the media link, and provide instant MP3 / MP4 download options!

---

## ☁️ Deploying Backend to Cloud (Render / Railway)

To let mobile users download videos without keeping their PC turned on:
1. Push this code to GitHub.
2. Connect your repository to **[Render.com](https://render.com)** or **Railway.app**.
3. Render automatically reads `render.yaml` / `Dockerfile` and deploys the backend server with FFmpeg pre-installed!
4. Copy your cloud URL (e.g. `https://abirs-downloader.onrender.com`).
5. Open Chrome Extension Settings or Android App Settings and paste your Cloud URL. Now it works anywhere over the internet!

---

## 🛠️ Folder Structure

```
Downloader/
├── server.py              # Main Python Flask & yt-dlp API
├── dist/                  # Built Windows Executable (.exe)
├── windows_app/
│   ├── app.py             # System Tray launcher & Auto-start code
│   └── install_extension.bat
├── extension/
│   ├── manifest.json      # Chrome / Edge MV3 Extension
│   ├── popup.html         # Extension Dark UI
│   ├── popup.js           # Extension Logic
│   ├── options.html       # Server Endpoint Settings
│   └── options.js
├── android_app/
│   ├── AndroidManifest.xml # Share Intent Filter
│   ├── MainActivity.java   # Android Share Handler
│   └── web_app/            # Mobile Web Interface
├── Dockerfile             # Cloud Docker Container with FFmpeg
├── Procfile               # Cloud Process Spec
└── requirements.txt       # Python Dependencies
```
