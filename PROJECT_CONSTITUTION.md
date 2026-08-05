# 📜 MASTER PROJECT CONSTITUTION: ABIRs Downloader

> **Document Version:** 1.0.0  
> **Status:** RATIFIED & MANDATORY  
> **Scope:** Entire Repository, All Supported Platforms, All Contributors  
> **Authority:** Chief Software Architect  
> **Enforcement:** Automated CI/CD Gates, Linter Rules, & Mandatory Code Reviews  

---

## 1. Project Vision

### Purpose
ABIRs Downloader is a unified, high-performance, cross-platform media extraction and download ecosystem. Its primary mission is to provide users with an effortless, privacy-respecting, and reliable solution to extract, transcode, and save media (video/audio) from major online platforms—including YouTube, Facebook, Instagram, and Spotify—across desktop, browser, mobile, and cloud environments.

### Target Users
1. **Desktop Power Users:** Users seeking background download automation on Windows with native system tray integration and auto-boot capabilities.
2. **Web & Extension Users:** Browser-focused users who desire one-click media detection and quality selection directly while browsing Chrome, Edge, or Firefox.
3. **Mobile On-The-Go Users:** Android users leveraging native OS "Share Target" intents to send links directly from native social media apps to the downloader without copy-pasting.
4. **Cloud / Self-Hosted Operators:** Tech-savvy users and server administrators running hosted download engines on Docker, Render, Railway, or private VPS infrastructure.

### Supported Platforms
- **Windows Desktop:** Windows 10/11 (64-bit) with system tray daemon and Windows Registry auto-start integration.
- **Web Browser Extensions:** Manifest V3 compliant extensions for Google Chrome, Microsoft Edge, and Brave.
- **Android Mobile:** Android 8.0+ (API Level 26+) native Android Share Target wrapper combined with responsive PWA/WebView UI.
- **Cloud & Server Environments:** Docker containerized deployment (Linux/amd64/arm64), compatible with Render, Railway, Heroku, and HuggingFace Spaces.

### Future Expansion
- **macOS & Linux Desktop Applications:** Tauri-based native desktop wrappers for cross-platform system tray and notification integration.
- **iOS Shortcut / Safari Extension:** Apple ecosystem integration via iOS Web Extensions and Share Sheet Shortcuts.
- **Multi-Node Distributed Engine:** Clustered download engine with proxy rotation and automatic IP load balancing for high-throughput cloud environments.

---

## 2. Project Goals

### Primary Goals
1. **Single Engine Reliability:** Guarantee 99.5%+ download success rate across supported media platforms by maintaining automated yt-dlp core updates.
2. **Sub-2-Second Metadata Extraction:** Deliver media resolution, thumbnail, and format analysis within 2 seconds of link submission.
3. **Zero-Lock-in Portability:** Ensure complete operation across pure local execution (offline/PC server) and remote cloud backend setups with a single toggle.
4. **Strict Architectural Consolidation:** Maintain exactly **one** single source of truth for every platform component, completely eliminating duplicate codebases or divergent manifests.

### Secondary Goals
1. **Minimal CPU/RAM Footprint:** Idle RAM usage below 35 MB on Windows tray daemon and below 80 MB on Android webview container.
2. **Unified Design System:** Consistently deliver a modern dark glassmorphism interface across Web, Browser Extension, Windows Launcher, and Android WebView.
3. **Zero-Configuration Onboarding:** Provide automatic local backend detection with zero mandatory initial configuration for desktop users.

### Non-Goals
1. **DRM Bypass / Copyright Violation Tools:** ABIRs Downloader will NOT include decryption algorithms for Widevine, PlayReady, or FairPlay DRM-protected commercial streaming media (e.g., Netflix, Hulu, Spotify DRM tracks). Spotify tracks are fetched via legal public metadata matching and authorized media streams.
2. **Paid Subscription / Gated Paywalls:** The core software will remain 100% open, free of internal monetization paywalls, pop-up advertising networks, or user data tracking scripts.
3. **P2P Torrent Client Functionality:** The application is dedicated exclusively to HTTP/HTTPS media extraction and stream stitching, not BitTorrent protocols.

---

## 3. Core Principles

### 3.1 Performance First
- Network operations must be non-blocking and asynchronous.
- Direct file streaming and chunks flushing must be preferred over loading full media files into server memory (`RAM`).
- Static web assets must be pre-compressed (gzip/brotli) and cached with long-lived HTTP headers.

### 3.2 Security First
- Strict input validation and strict domain whitelisting must precede any extraction attempt.
- Server-Side Request Forgery (SSRF) protection is mandatory: no extraction requests to private IP ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.1`).
- All cross-origin permissions (CORS) must be explicitly restricted to verified app domain names or configured client extensions.

### 3.3 Offline Friendly
- Web UI and extension popups must serve UI shells locally via Service Workers when network connectivity drops.
- Local desktop installation must function completely offline for media playback, history lookup, and local asset rendering.

### 3.4 Cross Platform
- Code must avoid platform-specific path separators or OS-bound terminal commands in core logic. Use standard Python `pathlib` and cross-platform abstractions.
- Business logic must reside in shared core modules, keeping platform layers (Windows Tray, Android WebView, Chrome Extension) thin UI adapters.

### 3.5 Maintainability
- Monolithic scripts are strictly forbidden. Code must follow clear modular layer boundaries: Controller -> Service -> Task -> Repository.
- Type hints (Python `typing`, JSDoc / TypeScript) are required across all backend functions and public API contracts.

### 3.6 Scalability
- Long-running downloads must NEVER block HTTP worker threads. All downloads must execute in background asynchronous worker queues (Redis/RQ or Asyncio Background Tasks).
- Ephemeral download files must be tracked in a database and purged on deterministic TTL schedules rather than unindexed disk scans.

### 3.7 Accessibility
- All UI interfaces must meet WCAG 2.1 AA standards, supporting keyboard navigation, visible focus indicators, high contrast, and `aria-*` screen-reader labels.

### 3.8 Minimal Resource Usage
- Background processes must remain idle when inactive. No infinite polling loops; rely strictly on event-driven IPC, WebSockets, or Server-Sent Events (SSE).

---

## 4. Technology Decisions

| Domain | Technology / Library | Selection Justification |
| :--- | :--- | :--- |
| **Backend Language** | Python 3.11+ | Optimal ecosystem for `yt-dlp`, native async primitives, and rapid cross-platform packaging. |
| **Backend Framework** | FastAPI (Upgrading from Flask) | Native async/await support, automatic OpenAPI specs, high performance, structured Pydantic schemas. |
| **Desktop Launcher** | PyInstaller + `pystray` + `Pillow` | Native Windows executable compilation with system tray icon support and zero runtime dependencies. |
| **Android Wrapper** | Native Java / Kotlin (Android SDK) | Lightweight native wrapper (`MainActivity`, `ShareTarget` intent receiver) hosting the responsive PWA Web UI. |
| **Extension Standard** | Manifest V3 (Vanilla JS + HTML5 + CSS3) | Compliance with modern Chrome/Edge browser store security policies without heavy frontend bundlers. |
| **Web UI Stack** | Vanilla HTML5 / Modern CSS3 / Modern JS | Ultra-fast load times (< 100ms), zero node_modules overhead, high aesthetic fidelity using CSS variables & Glassmorphism. |
| **Database Engine** | SQLite3 (WAL mode) / PostgreSQL | Embedded, zero-config relational store for local history/settings; pluggable PostgreSQL for cloud deployments. |
| **Task Queue** | Redis + RQ (Cloud) / Python `asyncio` Task Manager (Local) | Reliable asynchronous background processing for media extraction, audio conversion, and stream merging. |
| **Media Transcoding** | FFmpeg 6.0+ static build | Required by `yt-dlp` for merging high-definition video/audio streams and converting MP3 audio. |
| **Build Tools** | Docker, PyInstaller, Gradle | Reproducible container builds for cloud; native binary generators for desktop and mobile distribution. |
| **Testing Framework** | `pytest`, `pytest-asyncio`, `Playwright` | Robust unit, integration, and end-to-end browser/API automation framework. |
| **CI/CD Pipeline** | GitHub Actions | Automated linting, matrix testing, Docker image creation, and multi-platform binary compilation. |

---

## 5. Repository Structure

### 5.1 Ideal Target Directory Hierarchy

```
Downloader/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Automated build, lint, test pipeline
│       └── release.yml               # Automated release & binary asset builder
├── backend/                          # Single Backend Core Source of Truth
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point & routing configuration
│   │   ├── config.py                 # Pydantic environment & app configuration
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── analyze.py    # Media format extraction route
│   │   │   │   │   ├── download.py   # Asynchronous download job trigger route
│   │   │   │   │   ├── health.py     # System health and diagnostic route
│   │   │   │   │   └── history.py    # Persistent download history route
│   │   │   │   └── api.py            # API router aggregator
│   │   ├── core/
│   │   │   ├── security.py           # SSRF protection, URL validation, rate limits
│   │   │   └── database.py           # SQLite / PostgreSQL connection manager
│   │   ├── services/
│   │   │   ├── extractor.py          # yt-dlp core wrapper & format parser
│   │   │   ├── downloader.py         # Media downloader engine
│   │   │   └── spotify.py            # Spotify metadata resolver & YouTube matcher
│   │   ├── models/                   # Pydantic & ORM schemas
│   │   └── workers/                  # Background task processing logic
│   ├── tests/                        # Backend test suite
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── Dockerfile                    # Production Docker container definition
│   ├── requirements.txt              # Strict pinned production dependencies
│   └── requirements-dev.txt          # Development, linting, testing dependencies
├── desktop/                          # Single Windows Desktop Source of Truth
│   ├── app.py                        # System tray app launcher & daemon manager
│   ├── installer.bat                 # One-click extension & environment installer
│   ├── build.py                      # PyInstaller compilation script
│   └── assets/                       # Icons, tray graphics, installer media
├── extension/                        # Single Browser Extension Source of Truth (MV3)
│   ├── manifest.json                 # Manifest V3 extension configuration
│   ├── popup.html                    # Dark Glassmorphism popup UI
│   ├── popup.js                      # Extension popup interaction script
│   ├── options.html                  # Backend URL configuration page
│   ├── options.js                    # Storage management script
│   └── assets/                       # Extension icon set (16, 48, 128)
├── android/                          # Single Android Source of Truth
│   ├── app/
│   │   ├── src/
│   │   │   └── main/
│   │   │       ├── java/com/abir/downloader/
│   │   │       │   └── MainActivity.java  # Native ShareTarget Intent receiver
│   │   │       ├── res/              # Android layout & icon resources
│   │   │       └── AndroidManifest.xml# Active, canonical Android manifest
│   │   └── build.gradle              # App build configuration
│   ├── build.gradle                  # Top-level Gradle configuration
│   └── settings.gradle               # Gradle settings
├── web/                              # Single Shared Web UI Source of Truth
│   ├── index.html                    # Responsive main interface
│   ├── styles.css                    # Design system CSS rules & dark tokens
│   ├── app.js                        # Web application controller
│   ├── manifest.json                 # PWA Web Manifest
│   └── sw.js                         # Offline Service Worker
├── docs/                             # Architecture & usage documentation
│   ├── API_SPEC.md                   # OpenAPI documentation
│   └── DEPLOYMENT.md                 # Deployment & packaging guides
├── PROJECT_CONSTITUTION.md           # Master System Architecture & Standard Document
├── README.md                         # Repository introduction & setup guide
├── render.yaml                       # Cloud deployment specification
└── .gitignore                        # Git exclusion rules
```

### 5.2 Consolidation & Single Source of Truth Principles
1. **One Android Target:** Delete duplicate root `android_app/AndroidManifest.xml` and `android_app/MainActivity.java`. The sole canonical path is `android/app/src/main/`.
2. **One Desktop Launcher:** Delete root `desktop_app.py`. The sole canonical desktop script resides at `desktop/app.py`.
3. **One Shared Web UI:** The static UI files inside `web/` serve as the single interface delivered by the cloud backend, local desktop web server, and Android WebView.
4. **One Backend API:** Deprecate redundant Flask routes (`/formats` vs `/api/analyze`). Standardize all endpoints under `/api/v1/`.

### 5.3 Removal Plan for Legacy & Duplicate Artifacts
- Remove root level redundant files: `desktop_app.py`, `server.py` (after refactoring into `backend/`), duplicate VBS scripts (`Start_Server.vbs`, `Stop_Server.vbs`).
- Clean root directory to keep only top-level orchestrators (`render.yaml`, `README.md`, `PROJECT_CONSTITUTION.md`).

---

## 6. Coding Standards

### 6.1 Naming Conventions
- **Python:** `snake_case` for variables, function names, and module files; `PascalCase` for classes; `ALL_CAPS` for global constants.
- **JavaScript:** `camelCase` for variables and functions; `PascalCase` for UI component classes; `kebab-case` for static file names (`styles.css`, `app-controller.js`).
- **Java / Android:** `camelCase` for variable names; `PascalCase` for classes; `activity_main.xml` for layout XML resources.
- **REST APIs:** `kebab-case` for URL paths (`/api/v1/media-analysis`, `/api/v1/download-jobs`).

### 6.2 Formatting & Style
- **Python:** Strict adherence to PEP 8. Format with `black` (line length 100) and sort imports with `isort`.
- **JavaScript / HTML / CSS:** Format with `Prettier` (tab width 2, single quotes for JS, double quotes for HTML attributes).
- **Indentation:** 4 spaces for Python and Java; 2 spaces for JavaScript, HTML, CSS, JSON, and YAML.

### 6.3 Comments & Inline Documentation
- Write code that is self-documenting through precise variable names.
- Inline comments must explain *why* non-obvious logic exists (e.g., regex workaround for platform changes), never *what* standard syntax does.
- All Python functions must include Google-style docstrings:
```python
def extract_media_metadata(url: str, include_formats: bool = True) -> Dict[str, Any]:
    """Extracts format and media metadata using yt-dlp.

    Args:
        url: Validated public media URL.
        include_formats: Whether to parse video resolution options.

    Returns:
        Dict containing title, thumbnail, duration, and list of formats.

    Raises:
        InvalidURLError: If the URL fails domain validation.
        ExtractionError: If yt-dlp fails to parse the media source.
    """
```

### 6.4 Documentation Architecture
- API specifications must be auto-generated via FastAPI OpenAPI/Swagger.
- Architecture choices must be logged in Section 17 of this Constitution.

### 6.5 File Size Limits
- Source code files MUST NOT exceed **300 lines of code** (excluding docstrings/imports). Files exceeding 300 lines must be refactored into submodule layers.

### 6.6 Function Size Limits
- Functions and methods MUST NOT exceed **40 lines of code**. Single-purpose, pure functions are mandatory.

### 6.7 Class Responsibilities
- Classes must have a single, clearly defined responsibility (Single Responsibility Principle). Data transfer objects (DTOs) must use Pydantic models in Python.

### 6.8 SOLID Design Principles
- **S:** Separate route handling from extraction logic and file storage.
- **O:** Format parsing must be extensible to new platforms without modifying core extraction controllers.
- **L:** Subclassed format extractors must be completely substitutable for base extractors.
- **I:** Client APIs must depend on minimal, targeted interface endpoints.
- **D:** High-level services must depend on storage abstractions, not direct OS file functions.

### 6.9 DRY (Don't Repeat Yourself)
- URL sanitization, filename cleaning, and HTTP header generation must exist in exactly **one** shared utility module.

### 6.10 KISS (Keep It Simple, Stupid)
- Avoid unneeded frontend frameworks (React/Vue/Angular) when Vanilla JS meets all requirements with superior speed and zero build step.

---

## 7. Security Standards

### 7.1 Authentication & Identity Management
- **Local Mode:** No authentication required for `127.0.0.1` desktop deployment.
- **Cloud Mode:** Optional API Key header (`X-API-Key`) validation required for public multi-user deployments to prevent unauthorized third-party proxy usage.

### 7.2 Authorization & Access Control
- Downloader endpoints must prohibit file system path traversal. Users can only download generated files within the designated sandboxed temporary storage directory.

### 7.3 API Validation & SSRF Prevention
- Strict validation must be performed on all incoming URLs:
  1. Scheme must be strictly `http` or `https`.
  2. Hostnames must be resolved against DNS to block internal private IP ranges (`127.0.0.1`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254` AWS metadata endpoints).
  3. Domain hostnames must match allowed extractor patterns or pass standard public top-level domain checks.

### 7.4 Rate Limiting & Abuse Mitigation
- Cloud backend instances must enforce rate limits using `slowapi` or Redis token buckets:
  - Format Analysis Endpoint (`/api/v1/analyze`): Max 30 requests / minute / IP.
  - Download Trigger Endpoint (`/api/v1/download`): Max 10 requests / minute / IP.

### 7.5 Input Validation & Sanitization
- File names generated from media titles must be sanitized to remove OS reserved characters (`<>:"/\|?*`), control characters, and leading/trailing whitespace.
- File names must be capped at 60 characters to prevent Windows MAX_PATH (260 char) buffer overflows.

### 7.6 Secrets Management
- Hardcoding secrets, API keys, or private tokens in git source control is strictly prohibited.
- `.env` files must be included in `.gitignore`. A `.env.example` file must be maintained with dummy values.

### 7.7 Environment Variables Policy
- All backend parameters (PORT, HOST, DOWNLOAD_DIR, MAX_FILE_AGE, REDIS_URL, ALLOWED_ORIGINS) must be driven by Pydantic `BaseSettings`.

### 7.8 Logging & Audit Trail
- Use structured JSON logging (`structlog`).
- Logs MUST NEVER contain authorization tokens, API keys, or raw personal IP addresses (IPs must be anonymized/hashed).

### 7.9 User Data Privacy & Compliance
- ABIRs Downloader does NOT track user download history on cloud servers beyond ephemeral job completion states.
- Local history is stored strictly on the user's client device in SQLite/IndexedDB.

---

## 8. API Design Rules

### 8.1 REST Conventions
- Use standard HTTP verbs: `GET` for retrieval, `POST` for job submission, `DELETE` for resource cleanup.
- All endpoint URIs must be pluralized nouns, prefixed with `/api/v1/`.

### 8.2 Versioning
- API versions are declared in the URL path (`/api/v1/`, `/api/v2/`). Breaking schema changes mandate a major version increment.

### 8.3 Standard Response Format
All API responses must return a consistent JSON payload structure:

```json
{
  "success": true,
  "data": {
    "title": "Sample Media Title",
    "duration": "03:45",
    "thumbnail": "https://img.youtube.com/vi/sample/maxresdefault.jpg",
    "uploader": "Channel Name",
    "formats": [
      {
        "format_id": "mp3_best",
        "extension": "mp3",
        "label": "🎵 MP3 Audio (Best Quality)",
        "type": "audio"
      }
    ]
  },
  "error": null,
  "timestamp": "2026-08-05T11:12:00Z"
}
```

### 8.4 Standard Error Format
When an error occurs, `success` must be `false`, returning an explicit error object:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNSUPPORTED_URL",
    "message": "The provided URL is private or not supported.",
    "details": []
  },
  "timestamp": "2026-08-05T11:12:00Z"
}
```

### 8.5 Status Codes
- `200 OK`: Successful synchronous request.
- `202 Accepted`: Asynchronous download job queued successfully.
- `400 Bad Request`: Validation failure or malformed payload.
- `403 Forbidden`: SSRF attempt or API key invalid.
- `429 Too Many Requests`: Rate limit exceeded.
- `500 Internal Server Error`: Unhandled server exception.

### 8.6 Pagination
- Endpoints returning collections (e.g., download history) must support limit-offset pagination: `?page=1&limit=20`.

---

## 9. UI/UX Standards

### 9.1 Design Language
- **Theme:** Modern Dark Glassmorphism.
- **Color Palette:**
  - Background Base: `#0f172a` (Deep Slate / Dark Blue)
  - Surface Glass: `rgba(30, 41, 59, 0.7)` with `backdrop-filter: blur(12px)`
  - Primary Accent: `linear-gradient(135deg, #6366f1 0%, #a855f7 100%)` (Indigo to Purple)
  - Text Primary: `#f8fafc`
  - Text Secondary: `#94a3b8`
  - Success: `#22c55e`
  - Error/Warning: `#ef4444`

### 9.2 Themes
- Dark mode is default across all platforms. System preference detection (`prefers-color-scheme`) must be respected.

### 9.3 Icons
- SVG icons exclusively (Lucide Icons or Feather Icons). Raster PNG icons are forbidden for UI actions.

### 9.4 Responsive Behavior
- UIs must adapt seamlessly across desktop monitors (1920x1080), extension popups (400x550), and mobile viewports (360px width min).

### 9.5 Micro-Animations
- Interactive elements (buttons, inputs) must include subtle CSS transitions (`transition: all 0.2s ease-in-out`).

### 9.6 Loading States
- Skeleton loaders and glowing progress bars must accompany format fetching and download processing. Generic unstyled spinners are forbidden.

### 9.7 Errors
- Error messages presented to users must be human-readable, friendly, and provide clear recovery actions (e.g., "Invalid link format. Please check the copied link and try again.").

### 9.8 Accessibility
- Minimum contrast ratio of 4.5:1 for normal text. Touch targets on mobile/PWA must be at least 48x48 pixels.

---

## 10. Database Standards

### 10.1 Schema Rules
- All tables must include:
  - `id`: Primary key (`INTEGER AUTOINCREMENT` for SQLite, `UUID` for PostgreSQL).
  - `created_at`: Timestamp UTC default.
  - `updated_at`: Timestamp UTC default.
- No direct physical deletion of user history records; soft deletes (`is_deleted: boolean`) are preferred for history.

### 10.2 Migration Strategy
- Use Alembic for Python database schema migrations. Manual database schema modifications are strictly forbidden.

### 10.3 Naming Conventions
- Table names must be plural `snake_case` (e.g., `download_jobs`, `user_settings`).
- Foreign key columns must use singular target name + `_id` (e.g., `job_id`).

### 10.4 Indexes
- Create indexes on frequently queried columns: `created_at`, `job_status`, `client_ip_hash`.

### 10.5 Backups
- Ephemeral backend downloads directory requires no backup. Local SQLite database file (`downloader.db`) is backed up locally before migrations.

---

## 11. Deployment Strategy

### 11.1 Development Environment
- Local execution via Python virtualenv (`venv`) running FastAPI dev server with auto-reload (`uvicorn app.main:app --reload`).

### 11.2 Testing & Staging Environment
- Docker container instance spun up locally or in CI pipelines executing integration test suites against mock media providers.

### 11.3 Production Cloud Deployment
- **Container Registry:** GitHub Container Registry (`ghcr.io`) or Docker Hub.
- **PaaS Host:** Render.com / Railway / Docker Container with multi-stage build ensuring FFmpeg 6.0 binary installation and static asset hosting.

### 11.4 Windows Packaging & Distribution
- PyInstaller bundle compiling `desktop/app.py` into a single standalone executable or clean directory distribution with auto-start Registry scripts.

### 11.5 Android APK Packaging & Distribution
- Android Studio / Gradle pipeline compiling native APK wrappers with bundled responsive web assets and ShareTarget intent filters.

---

## 12. Release Strategy

### 12.1 Semantic Versioning (SemVer 2.0.0)
- Format: `MAJOR.MINOR.PATCH` (e.g., `3.1.0`)
  - **MAJOR:** Breaking changes in API schema or platform support.
  - **MINOR:** New supported platforms, feature additions, backwards-compatible backend updates.
  - **PATCH:** Bug fixes, `yt-dlp` updates, minor UI tweaks.

### 12.2 Git Branch Strategy (GitFlow Variant)
- `main`: Production-ready code only. Tagged with SemVer releases.
- `develop`: Integration branch for active development.
- `feature/*`: Short-lived branches for specific features.
- `fix/*` or `hotfix/*`: Bug fix branches.

### 12.3 Commit Convention
All commits must follow Conventional Commits standard:
- `feat(backend): add asynchronous redis task worker`
- `fix(extension): resolve popup connection retry logic`
- `docs(constitution): establish master project constitution`
- `style(web): refine glassmorphism cards and buttons`

### 12.4 Release Checklist
- [ ] All automated unit and integration tests pass in CI.
- [ ] Core dependency `yt-dlp` updated to latest release.
- [ ] Static web UI files verified inside Docker image (`index.html`, `manifest.json`, `sw.js`).
- [ ] PyInstaller Windows executable built and system tray auto-start tested on Windows 10/11.
- [ ] Android APK generated and Share Target verified from YouTube & Instagram apps.
- [ ] Manifest V3 Chrome Extension verified with zero console errors.

---

## 13. Testing Strategy

### 13.1 Unit Testing
- Framework: `pytest`.
- Target: 80%+ code coverage on backend utilities, URL sanitizers, format parsers, and configuration models.

### 13.2 Integration Testing
- Test FastAPI endpoints with `httpx.AsyncClient`.
- Mock external network calls to media sites to verify JSON extraction parsing without relying on live site uptime.

### 13.3 UI & End-to-End Testing
- Playwright tests for Web UI and Browser Extension popup interaction flows.

### 13.4 Performance Testing
- `locust` or `k6` load scripts ensuring the API handles 100 concurrent format analysis requests without worker exhaustion.

### 13.5 Regression Testing
- Automated regression suite executing on every PR to verify that platform updates do not break existing media platform links.

---

## 14. Future Roadmap

### 14.1 Short-Term Roadmap (Months 1–3)
- Execute architectural consolidation: refactor backend to FastAPI, enforce single source directory structure.
- Add background worker queue (Redis / Asyncio Tasks) to decouple downloads from HTTP request threads.
- Fix Docker deployment packaging to bundle all PWA and web static assets cleanly.

### 14.2 Medium-Term Roadmap (Months 4–6)
- Build real Spotify track metadata resolver (fetching track name/artist via web metadata and searching audio stream).
- Implement download history persistence in local SQLite / IndexedDB.
- Introduce auto-update notification for Windows Desktop App and `yt-dlp` core.

### 14.3 Long-Term Roadmap (Months 7–12+)
- Cross-platform desktop release using Tauri (macOS, Linux support).
- iOS Share Sheet Shortcut and Safari MV3 extension release.
- Multi-user authentication & custom cloud storage sync (Google Drive / Dropbox direct downloads).

---

## 15. Feature Inventory

### 15.1 Approved Features
- Multi-platform media extraction (YouTube, Facebook, Instagram, Twitter/X, TikTok).
- Audio conversion (MP3 320kbps extraction via FFmpeg).
- Windows System Tray launcher with Registry auto-boot integration.
- Android Native Share Target Intent integration.
- Browser MV3 extension with active tab media detection.
- One-click cloud Docker container deployment.

### 15.2 Rejected Features
- Direct DRM video decryption (violates core non-goals and legal parameters).
- BitTorrent P2P protocols (out of project scope).
- User tracking, monetization paywalls, or third-party ad network integration.

### 15.3 Future Features
- Batch download playlist extraction support.
- Custom video trimming before downloading (start/end timestamp markers).
- Direct cloud storage export (WebDAV / S3 / Google Drive).

---

## 16. Definition of Done (DoD)

A feature or pull request is strictly considered **DONE** when and only when:

1. **Code Compliance:** Code strictly adheres to all naming, formatting, and file size standards defined in Section 6.
2. **Consolidation:** No duplicate source files, scripts, or manifests have been introduced.
3. **Automated Testing:** All unit and integration tests pass; test coverage does not decrease.
4. **Security & Validation:** Input validation, SSRF checks, and filename sanitization have been applied.
5. **Cross-Platform Verification:** Feature is verified across the target platforms (Web, Windows Desktop, Extension, Android).
6. **Documentation Updated:** API spec, README, or internal docs reflect the changes.
7. **CI/CD Approval:** GitHub Actions CI pipeline passes cleanly with zero lint or build errors.

---

## 17. Architecture Decision Records (ADRs)

### ADR-001: Asynchronous Task Architecture over Synchronous HTTP Downloads
- **Context:** The original backend executed `yt-dlp` synchronous downloads directly inside HTTP request routes. Long downloads blocked Gunicorn worker threads, leading to request timeouts and poor scalability under concurrent usage.
- **Decision:** Separate media analysis (`/api/v1/analyze`) from media downloading (`/api/v1/download`). The download route accepts a request, registers an asynchronous task job, returns a `202 Accepted` response with a unique `job_id`, and processes the download in a background worker queue (Redis/RQ or Asyncio Task Manager).
- **Consequences:** Eliminates HTTP request timeouts, allows clients to poll job status or receive WebSockets/SSE updates, and ensures server thread availability under load.

### ADR-002: SQLite (Local) & PostgreSQL (Cloud) Database Strategy
- **Context:** Ephemeral disk file lookups were used to locate completed downloads, requiring recursive directory scans on every request. No download history or job states were persisted across restarts.
- **Decision:** Introduce a lightweight database persistence layer using SQLAlchemy / SQLModel. Local mode utilizes SQLite with Write-Ahead Logging (WAL) enabled; cloud multi-user mode supports PostgreSQL.
- **Consequences:** Fast indexed lookup of download job status, persistent client history, and deterministic automatic cleanup of expired files via background cron jobs without scanning physical directories.

### ADR-003: Manifest V3 Architecture for Browser Extensions
- **Context:** Browser extension ecosystems (Chrome Web Store, Microsoft Edge Add-ons) require all extensions to use Manifest V3.
- **Decision:** Implement browser extension adhering strictly to MV3 guidelines using declarative service workers, Chrome Storage API for endpoint configuration, and standard content script messaging.
- **Consequences:** Full compliance with modern browser security policies, future-proof store listing eligibility, and low battery/memory consumption.

### ADR-004: Native Android Share Target + Hybrid WebView Integration
- **Context:** Mobile users require an effortless method to download videos directly from native apps (YouTube, Instagram, Facebook) without manually copying links into a browser.
- **Decision:** Build a lightweight native Android wrapper handling `android.intent.action.SEND` intents (`MainActivity.java`), extracting shared text URLs, and loading the unified glassmorphism Web UI inside a tuned Android `WebView`.
- **Consequences:** Native OS feel and instant Share menu accessibility while reusing 100% of the single source of truth Web UI codebase.

### ADR-005: System Tray & Auto-Start Registry Launcher for Windows
- **Context:** Windows desktop users expect the application to run silently in the background without keeping an open console terminal window.
- **Decision:** Implement a background daemon (`desktop/app.py`) utilizing `pystray` for system tray controls (Open UI, Change Port, Exit) and Windows Registry key integration (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`) for optional boot start.
- **Consequences:** Native Windows desktop experience, zero-terminal user interaction, and seamless background server availability.

### ADR-006: Containerized Docker Deployment with Static PWA Asset Serving
- **Context:** Cloud deployments on platforms like Render or Railway frequently suffered missing static assets (`manifest.json`, `sw.js`) because only `server.py` was copied into container images.
- **Decision:** Design a multi-stage `Dockerfile` that installs system dependencies (FFmpeg), copies all single source of truth web assets (`web/` directory), and serves both API routes and static PWA assets through the primary FastAPI application.
- **Consequences:** Guarantees 100% reliable cloud deployments where PWA features, offline service workers, and web UIs function out-of-the-box.

### ADR-007: Single Source of Truth Repository Restructuring
- **Context:** The repository suffered from duplicate implementations (e.g., dual Android manifests and dual `MainActivity` files, scattered desktop scripts).
- **Decision:** Re-architect the repository directory structure into distinct, non-overlapping platform modules (`backend/`, `desktop/`, `extension/`, `android/`, `web/`). Remove all legacy/duplicate code paths.
- **Consequences:** Significantly reduces maintenance debt, eliminates ambiguity for developers and CI/CD tools, and establishes clear code ownership.

---

> **BY ORDER OF THE CHIEF SOFTWARE ARCHITECT**  
> *This document shall be strictly enforced across all pull requests, code additions, and architectural decisions.*
