# 📋 PHASE 2 BACKEND REPORT: Flask Modularization

> **Phase:** 2 (Flask Modularization & Backend Cleanup)  
> **Status:** COMPLETED & VERIFIED  
> **Framework:** Python Flask (v1 Baseline Architecture preserved)  
> **Governing Documents:** [PROJECT_CONSTITUTION.md](file:///C:/Users/Abir/Downloader/PROJECT_CONSTITUTION.md), [ENTERPRISE_ARCHITECTURE.md](file:///C:/Users/Abir/Downloader/ENTERPRISE_ARCHITECTURE.md), & [docs/BACKEND_DESIGN_FREEZE.md](file:///C:/Users/Abir/Downloader/docs/BACKEND_DESIGN_FREEZE.md)  
> **Development Target:** `backend/app/main.py`  
> **Reference File (Untouched):** `server.py`  

---

## 1. Architecture Before (Monolithic Root Architecture)

Prior to Phase 2, the backend consisted of a single monolithic script (`server.py`) residing in the repository root:

- **Monolithic State:** Extraction logic (`yt-dlp`), Spotify html scraping, filename sanitization, temporary file cleanup, static web file delivery, CORS setup, and HTTP route handling were all tightly coupled inside one 285-line script.
- **Open Security Surface:** Open CORS (`*`), zero validation of user URLs against SSRF/private subnets, unindexed disk scanning on every request.
- **Execution Risks:** Requests blocked main thread workers during file downloads.

```
[Monolithic server.py]
├── Flask App & CORS Setup
├── Static File Delivery (/ , /manifest.json, /sw.js)
├── Format Analysis (/formats, /api/analyze)
├── Download Transcoding (/download, /api/download)
└── File Cleanup & Sanitization Logic
```

---

## 2. Architecture After (Modular Flask Blueprint Architecture)

The backend has been modularized into distinct, single-responsibility components residing under `backend/app/`. The framework remains **100% Flask**, preserving 100% API behavior compatibility while establishing clean layer separation.

```
[backend/app/main.py]  <-- Flask Factory & Blueprint Registrar
        │
        ├── [api/v1/endpoints/]
        │     ├── health.py        (GET /health)
        │     ├── analyze.py       (POST /formats, POST /api/analyze)
        │     ├── download.py      (GET /download, GET /api/download)
        │     └── web_server.py    (GET /, GET /manifest.json, GET /sw.js)
        │
        ├── [core/]
        │     ├── config.py        (Central Settings & Paths)
        │     └── security.py      (SSRF Guard & URL Sanitizer)
        │
        ├── [services/]
        │     ├── extractor.py     (yt-dlp Format Extraction Engine)
        │     ├── downloader.py    (FFmpeg Transcoder & File Cleaner)
        │     └── spotify.py       (Spotify Resolver & YouTube Matcher)
        │
        ├── [workers/]
        │     └── task_queue.py    (ThreadPoolExecutor Manager)
        │
        ├── [utils/] & [models/]
        │     ├── sanitizer.py     (safe_name)
        │     ├── formatter.py     (format_duration)
        │     └── schemas.py       (api_response envelope)
        │
        └── [constants.py, logger.py, exceptions.py]
```

---

## 3. New Modules & 4. Responsibilities

| Module | File Path | Responsibilities & Purpose |
| :--- | :--- | :--- |
| **Config** | `backend/app/core/config.py` | Centralized settings, path constants (`DOWNLOAD_DIR`, `WEB_DIR`), and network configuration. |
| **Security Guard** | `backend/app/core/security.py` | URL scheme validation, DNS resolution, and private subnet/SSRF IP filtering (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, AWS metadata `169.254.169.254`). |
| **Sanitizer** | `backend/app/utils/sanitizer.py` | Windows OS compatibility filename sanitization (`safe_name`). |
| **Formatter** | `backend/app/utils/formatter.py` | Duration seconds conversion into `HH:MM:SS` or `MM:SS` format (`format_duration`). |
| **Logger** | `backend/app/logger.py` | Centralized logging system (`get_logger()`). |
| **Constants** | `backend/app/constants.py` | System constants, default ports, user agent strings, and media type definitions. |
| **Exceptions** | `backend/app/exceptions.py` | Custom Exception hierarchy (`DownloaderBaseException`, `InvalidURLError`, `SSRFValidationError`). |
| **Task Queue** | `backend/app/workers/task_queue.py` | ThreadPoolExecutor background task queue manager for non-blocking asynchronous downloads. |
| **Spotify Service** | `backend/app/services/spotify.py` | Spotify webpage HTML title scraping and YouTube search query resolver. |
| **Extractor** | `backend/app/services/extractor.py` | `yt-dlp` metadata analyzer and resolution option generator. |
| **Downloader** | `backend/app/services/downloader.py` | `yt-dlp` download runner, FFmpeg stream merger/MP3 audio converter, and TTL file cleaner. |
| **Schemas** | `backend/app/models/schemas.py` | API response JSON envelope builder (`api_response`). |
| **Endpoints** | `backend/app/api/v1/endpoints/` | Flask Blueprints for `/health`, `/api/analyze`, `/api/download`, and static PWA web asset delivery. |
| **Main App** | `backend/app/main.py` | Development target Flask application factory, CORS registrar, and browser launcher daemon. |

---

## 5. Files Created

- `backend/app/core/config.py`
- `backend/app/core/security.py`
- `backend/app/utils/__init__.py`
- `backend/app/utils/sanitizer.py`
- `backend/app/utils/formatter.py`
- `backend/app/services/__init__.py`
- `backend/app/services/spotify.py`
- `backend/app/services/extractor.py`
- `backend/app/services/downloader.py`
- `backend/app/models/__init__.py`
- `backend/app/models/schemas.py`
- `backend/app/api/__init__.py`
- `backend/app/api/v1/__init__.py`
- `backend/app/api/v1/endpoints/__init__.py`
- `backend/app/api/v1/endpoints/health.py`
- `backend/app/api/v1/endpoints/analyze.py`
- `backend/app/api/v1/endpoints/download.py`
- `backend/app/api/v1/endpoints/web_server.py`
- `backend/app/constants.py`
- `backend/app/logger.py`
- `backend/app/exceptions.py`
- `backend/app/workers/task_queue.py`
- `backend/app/main.py`
- `docs/BACKEND_DESIGN_FREEZE.md`

---

## 6. Files Modified

- `ENTERPRISE_ARCHITECTURE.md` (Updated Section 20 Development Order to reflect 10-phase plan).
- `server.py` (**UNTOUCHED** — Preserved as Read-Only Reference File).
- Root files & legacy backups (**UNTOUCHED** — Preserved in root and `migration_backup/`).

---

## 7. Compatibility Notes

- **Flask Preserved:** Backend remains 100% Flask. No FastAPI migration was performed.
- **Route Aliases Preserved:** Both legacy route formats (`/formats` and `/api/analyze`, `/download` and `/api/download`) remain fully active and supported.
- **Payload Schema Identical:** JSON format payloads returned by `/api/analyze` match existing UI expectations exactly.
- **Static Web Serving:** Serves static PWA files (`index.html`, `manifest.json`, `sw.js`) from both `web/` single source directory and root fallback paths.

---

## 8. Security Improvements

1. **SSRF Guard:** Incoming URLs are verified against private IP subnets (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, AWS metadata `169.254.169.254`).
2. **URL Scheme Enforcement:** Restricts extraction strictly to `http://` and `https://` schemes.
3. **Filename Sanitization:** Input titles sanitized via `safe_name` to prevent Windows MAX_PATH overflows and path traversal.

---

## 9. Potential Risks

- **Dual Server Files:** Developers must use `backend/app/main.py` for new work while ignoring read-only `server.py`.
- **Directory Path Updates:** When moving to production Docker environments, ensure `downloads/` directory permissions allow write access.

---

## 10. Manual Review Checklist

- [x] Flask framework retained (no FastAPI/ASGI).
- [x] Root `server.py` remains untouched.
- [x] All 15+ sub-modules created in `backend/app/`.
- [x] Central logger, constants, config, security guard, exceptions, and task queue created.
- [x] Endpoint routes `/health`, `/api/analyze`, `/download`, `/`, `/manifest.json`, `/sw.js` tested and working (200 OK).
- [x] Zero application logic removed or broken.

---

## 11. Known Limitations

- Downloads currently execute synchronously on request threads for v1 API compatibility. Async task polling via `ThreadPoolExecutor` will be activated in Phase 5.
- File metadata index currently relies on filesystem scans; SQLite database persistence will be added in Phase 4.

---

## 12. Phase 3 Prerequisites (Backend Cleanup & SQLite Integration)

To proceed to **Phase 3 / Phase 4**:
1. Integrate SQLite database layer (`download_jobs`, `app_settings` tables) in `backend/app/core/database.py`.
2. Replace physical file directory scanning with indexed SQLite job status tracking.

---

> **PHASE 2 COMPLETE — VERIFIED & RATIFIED**  
> *Backend modularization finished cleanly with 100% Flask compatibility and security foundations.*
