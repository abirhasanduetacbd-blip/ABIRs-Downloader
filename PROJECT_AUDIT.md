# PROJECT AUDIT: ABIRs Downloader

## Executive Summary
ABIRs Downloader is a multi-platform media downloader project with a Python backend, browser extension frontend, Windows desktop launcher, and Android app/webview integration. The current repository contains functioning prototypes for core behaviors, but it is not production-ready due to security, deployment, dependency, and architecture gaps.

Key findings:
- Backend API is present and provides format analysis + download endpoints.
- Frontend web and browser extension are implemented and wired to the backend.
- Android app and Windows launcher exist, but there are duplicate files and incomplete packaging.
- No automated tests, limited dependency management, and Docker deployment misses required static files.
- Production readiness is low due to open backend design, local file handling, and inadequate scaling.

## Current Status
- Project type: Hybrid local/cloud media downloader
- Primary backend: Python Flask app using `yt-dlp`, `requests`, `Flask`, `Flask-CORS`
- Desktop support: Windows `.exe` launcher, system tray app, local backend fallback
- Browser support: Chrome/Edge extension MV3
- Mobile support: Android webview/Share Target integration skeleton
- Deployment: Docker, Procfile, render.yaml declared but incomplete

## Feature Checklist
### Completed
- Backend server with `/formats` and `/download` endpoints
- Web UI (`index.html`) for input, format selection, and download
- Chrome extension popup and options pages
- Android app/webview wrapper for shared links
- Windows launcher with system tray icon and auto-start registry setup
- Dockerfile and cloud deployment manifests declared

### Partially Completed
- Spotify handling: fallback via YouTube search, not real Spotify extraction
- PWA support: manifest and service worker present, but static assets missing in deployment image
- Android Share Target: local webapp skeleton present, but cloud URL hard-coded in app and configuration is awkward
- Desktop packaging: PyInstaller build script exists, but dependency list and packaging dependencies are incomplete

### Missing / Not Started
- Authentication, rate limiting, and abuse protection
- Background download queue / async worker architecture
- Persistent storage/database for history, analytics, or user settings
- Full CI / automated tests
- Release packaging instructions for Android APK and browser extension publishing
- Effective asset/static file handling on cloud deployment
- Error monitoring/logging and operational health checks beyond basic `/health`

## Folder Structure
- `server.py` - Flask backend and download engine
- `index.html`, `manifest.json`, `sw.js` - web UI and PWA assets
- `extension/` - Chrome/Edge extension UI and settings
- `android_app/` - Android project files and local webview app assets
- `windows_app/` - Windows tray launcher and auto-start script
- `build_windows_app.py` - PyInstaller build script for Windows
- `Dockerfile`, `Procfile`, `render.yaml` - deployment config
- `requirements.txt` - backend Python dependencies

## Architecture Diagram (Markdown)
```
[Browser Extension]   [Web UI]   [Android WebView/App]
      \               |             /
       \              |            /
        \             |           /
         --> [Flask Backend / yt-dlp] <-- [Windows Desktop Launcher]
                    |
                    v
               [Local File Storage]
```

## Issues
### Security
- `CORS(app, resources={r"/*": {"origins": "*"}})` allows any origin.
- Download endpoint is an open proxy/SSRF risk: user-supplied URLs are fetched with `requests` and `yt-dlp`.
- No authentication, no rate limiting, no abuse protection.
- `share_target` uses GET and query parameters, which may leak URLs and metadata.
- `safe_name()` does not fully sanitize all problematic filename characters or newline injection.
- Browser extension requests arbitrary backend endpoints with `host_permissions: ["<all_urls>"]`.

### Performance
- Backend uses synchronous `yt-dlp` extraction and download on the request thread.
- `gunicorn` configured with `--workers 2`, making concurrent downloads limited.
- `cleanup_old_files()` scans the download directory on every `/download` request.
- File lookup after download scans entire downloads directory, which scales poorly.

### Scalability
- No queueing/task worker for long-running downloads.
- Local disk file storage is unsuitable for high-load or cloud scaling.
- Multiple duplicate Android/desktop app implementations increase maintenance burden.
- Backend API design mixes analysis and download with no separation of concerns.

### Architecture / Design
- Duplicate Android manifests and duplicate `MainActivity.java` versions indicate unclear main code path.
- `server.py` has duplicate endpoints (`/api/analyze` and `/formats`) for the same behavior.
- `render.yaml`/`Dockerfile` do not copy `manifest.json` or `sw.js`, so PWA/static assets break in deployment.
- `requirements.txt` omits desktop build dependencies such as `PyInstaller`, `Pillow`, and `pystray`.
- `server.py` imports `render_template_string` but never uses it.

### Broken / Missing Imports
- No explicit project tracking for desktop dependencies (`Pillow`, `pystray`, `PyInstaller`) in `requirements.txt`.
- Docker build copies only `server.py` and `index.html`; `manifest.json` and `sw.js` are missing.

### Configuration
- Cloud backend URL is hard-coded in mobile app source and Android web app defaults.
- Multiple Android/manifest versions create confusion about the active source of truth.
- `requirements.txt` pins some packages but leaves `yt-dlp` as a floating version range.
- `Dockerfile` builds only backend, not full static/PWA asset set.

### UI / UX Problems
- Web UI assumes backend is served from same origin and may fail if deployed otherwise.
- Browser extension and Android app both require server URL configuration; no unified onboarding flow.
- `popup.js` may fail silently when the backend is offline; no retry or fallback guidance beyond the badge.
- Web UI download uses direct anchor click and may not preserve filenames reliably.

### Deployment
- Docker image missing required static files (`manifest.json`, `sw.js`).
- `render.yaml` uses Docker deployment, but no build steps verify static asset inclusion.
- No CI/lint/test pipeline or deployment validation.

### Testing Coverage
- No test files found in repository.
- No unit tests, integration tests, or automation scripts present.
- No coverage measurement or testing framework configuration.

## Risks
- Production deployment may fail because the Docker image lacks static PWA assets.
- Open backend exposes the service to abuse and potential SSRF/external fetch attacks.
- The combination of long-running downloads and limited workers could exhaust resources quickly.
- Duplicate code paths increase the chance of bugs and inconsistent behavior.
- Mobile app hard-coded cloud URL and ambiguous Android config reduce release readiness.

## Recommendations
1. Fix Docker deployment by copying `manifest.json`, `sw.js`, and any required static files into the container.
2. Consolidate Android sources into a single active manifest and `MainActivity` implementation.
3. Add authentication or API key support and enforce origin restrictions for browser/API access.
4. Replace synchronous downloads with a background worker/queue system and return status IDs.
5. Store download metadata in a persistent store instead of relying on local disk scanning.
6. Add comprehensive automated tests for backend API behavior and regression coverage.
7. Remove duplicate frontend assets or clearly separate platform-specific implementations.
8. Harden filename sanitization and URL validation before passing data to `yt-dlp`.
9. Document packaging and release processes for Windows, Android, and extension publishing.
10. Add CI for linting, dependency validation, and Docker image verification.

## Completion Percentage
Estimated completion: **60%**

## Next Steps
- Repair Docker deployment and verify static asset serving.
- Consolidate duplicate Android/desktop files and choose a single active implementation.
- Add backend security hardening and API request validation.
- Introduce automated tests and code quality checks.
- Design a production-grade architecture with task queueing and persistent storage.

## Milestones
### Completed
- Core Flask backend API
- Web UI for media analysis and download
- Chrome extension UI + settings
- Android Share skeleton / webview wrapper
- Windows tray launcher and local server fallback
- Basic Docker / cloud deployment config files

### In Progress
- Spotify URL workaround via YouTube search
- PWA metadata and manifest support
- Desktop `.exe` build script and installer concept
- Cloud deployment manifest setup

### Not Started
- Authentication, rate limiting, and abuse mitigation
- Automated tests and CI/CD pipeline
- Production-ready backend scaling and queue architecture
- Real Spotify/media platform extraction handling
- Comprehensive mobile release packaging and UX polish
