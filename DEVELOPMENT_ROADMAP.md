# DEVELOPMENT ROADMAP: ABIRs Downloader

This roadmap translates the audit findings into concrete implementation milestones for completing ABIRs Downloader. Each milestone is designed to be small, actionable, and aligned with the current project gaps.

---

## Milestone 1: Fix Docker Deployment and Static Asset Packaging

- Goal
  - Ensure the cloud deployment image serves the web UI and PWA assets correctly.
- Files to modify
  - `Dockerfile`
  - `render.yaml`
  - `Procfile`
  - `requirements.txt` (if runtime dependencies change)
- Estimated complexity
  - Low to medium
- Dependencies
  - Full file list of web assets
  - Knowledge of Docker build context and Flask static file serving
- Expected output
  - Docker image that includes `index.html`, `manifest.json`, `sw.js`, and any other web assets
  - Successful deployment verification via a health endpoint and browser UI load
- Acceptance criteria
  - `docker build` succeeds
  - `docker run` serves the web UI and PWA assets without 404 errors
  - `/health` returns 200 and the browser loads the home page and service worker assets

---

## Milestone 2: Consolidate Android App Sources and Configuration

- Goal
  - Remove duplicate Android manifests and unify the Android app build path.
- Files to modify
  - `android_app/AndroidManifest.xml`
  - `android_app/app/src/main/AndroidManifest.xml`
  - `android_app/MainActivity.java`
  - `android_app/app/src/main/java/com/abir/downloader/MainActivity.java`
  - `android_app/web_app/index.html`
  - `android_app/app/build.gradle`
- Estimated complexity
  - Medium
- Dependencies
  - Android Studio/Gradle knowledge
  - A single target Android app design decision
- Expected output
  - One active Android manifest and one active `MainActivity.java`
  - A clear configuration flow for the backend server URL instead of hard-coded endpoints
- Acceptance criteria
  - Android project builds successfully in Gradle
  - Share target works with a single implementation path
  - The app can be configured to use local or cloud backend URLs without source edits

---

## Milestone 3: Harden Backend Security and API Validation

- Goal
  - Protect the backend from open origin abuse and unsafe URL handling.
- Files to modify
  - `server.py`
  - `requirements.txt` (if additional security or validation libraries are added)
- Estimated complexity
  - Medium
- Dependencies
  - Security validation logic
  - Optional rate limiting or API key middleware libraries
- Expected output
  - Restricted CORS policy for expected origins
  - Input validation on `url`, `format_id`, and `type`
  - Safeguards against SSRF/untrusted remote fetches
- Acceptance criteria
  - CORS no longer allows `*` in production mode
  - Invalid or malicious URLs are rejected cleanly
  - Security-related regression tests cover validation rules

---

## Milestone 4: Separate Analysis and Download Flow with Background Worker Support

- Goal
  - Refactor the backend for better performance and scalability by separating request handling from download processing.
- Files to modify
  - `server.py`
  - `requirements.txt`
  - `Dockerfile`
  - optionally new worker/queue files (e.g. `worker.py`, `tasks.py`)
- Estimated complexity
  - High
- Dependencies
  - Task queue library such as `RQ`, `Celery`, or internal threaded worker design
  - Persistent metadata store or temporary file registry
- Expected output
  - `/formats` remains fast for metadata lookup
  - `/download` returns a job identifier instead of blocking until completion
  - Background worker processes downloads asynchronously
- Acceptance criteria
  - Long-running downloads do not block new API requests
  - Download status can be queried or the browser receives a stable stream
  - Resource usage is more predictable under concurrent load

---

## Milestone 5: Add Dependency Management and Build Documentation

- Goal
  - Make all runtime and packaging dependencies explicit and document build steps.
- Files to modify
  - `requirements.txt`
  - `build_windows_app.py`
  - `README.md`
  - `Dockerfile`
- Estimated complexity
  - Low to medium
- Dependencies
  - Accurate inventory of desktop and backend packages
  - Packaging requirements for PyInstaller and Android/extension builds
- Expected output
  - `requirements.txt` includes `Pillow`, `pystray`, `PyInstaller`, and any missing runtime dependencies
  - Build instructions documented for Windows executable, Docker, and Android APK
- Acceptance criteria
  - Dependency install succeeds for the backend and Windows packaging path
  - README clearly documents how to build and deploy each platform
  - No missing package errors during builds

---

## Milestone 6: Add Automated Tests and CI Pipeline

- Goal
  - Introduce baseline tests and automated quality checks.
- Files to modify
  - New test files under a `tests/` folder
  - `requirements.txt`
  - `README.md`
  - Optional CI config file (e.g. `.github/workflows/ci.yml`)
- Estimated complexity
  - Medium
- Dependencies
  - Test framework such as `pytest`
  - Mocking for network and yt-dlp interactions
- Expected output
  - Unit tests covering backend endpoints and validation rules
  - A CI configuration file validating linting and test execution
- Acceptance criteria
  - `pytest` passes with a baseline test suite
  - CI pipeline runs successfully and reports test results
  - No regressions introduced by future backend changes

---

## Milestone 7: Improve Frontend Resilience and Unified Server Configuration

- Goal
  - Make the browser extension and web UI robust to server availability and configuration changes.
- Files to modify
  - `extension/popup.js`
  - `extension/options.js`
  - `extension/popup.html`
  - `extension/options.html`
  - `index.html`
  - `android_app/web_app/index.html`
- Estimated complexity
  - Medium
- Dependencies
  - Frontend handling of server offline state and user settings
  - Storage and UI fallback behavior
- Expected output
  - Clear server status and retry messaging in the extension and web UI
  - Unified configuration pattern for local vs. cloud backend URLs
  - Better filename/download handling and error reporting
- Acceptance criteria
  - Users can configure the backend endpoint once and it applies consistently
  - Offline state is visible and recoverable
  - Download requests fail gracefully with actionable messages

---

## Milestone 8: Clean Up Duplicate Code and Simplify Architecture

- Goal
  - Reduce maintenance cost by removing redundant source files and clarifying active code paths.
- Files to modify
  - `android_app/` duplicates
  - `server.py` duplicate route aliases
  - `README.md` and docs if behavior changes
- Estimated complexity
  - Low to medium
- Dependencies
  - Clear project ownership of active implementations
- Expected output
  - Single source of truth for Android app behavior
  - No duplicate route definitions unless intentionally aliased
  - Documentation matches actual implementation
- Acceptance criteria
  - Codebase no longer contains two separate Android main activities or conflicting manifests
  - Backend route behavior is singular and consistent
  - README describes the active architecture accurately

---

## Milestone 9: Add Persistent Metadata Storage for History and Analytics

- Goal
  - Replace ad-hoc local storage and ephemeral file lookups with a durable download metadata store.
- Files to modify
  - `server.py`
  - `index.html`
  - optional database schema/migration files
- Estimated complexity
  - High
- Dependencies
  - Lightweight database choice such as SQLite or file-based JSON metadata store
- Expected output
  - Download history persisted across restarts
  - Backend can query recent downloads and clean expired artifacts reliably
- Acceptance criteria
  - History survives server restarts
  - Old files are cleaned deterministically without scanning full directories each request
  - Analytics data is available for future UI or admin use

---

## Milestone 10: Prepare Production Readiness and Release Packaging

- Goal
  - Finalize the project for a production release on Windows, Android, and browser extension channels.
- Files to modify
  - `README.md`
  - `manifest.json`
  - `android_app/` packaging files
  - `extension/` metadata
  - `build_windows_app.py`
- Estimated complexity
  - Medium to high
- Dependencies
  - Completed previous milestones
  - Release signing and packaging knowledge
- Expected output
  - Release-ready build instructions and packaging artifacts
  - Clear guidance for publishing the browser extension, Android APK, and desktop app
- Acceptance criteria
  - All platforms have documented and tested release steps
  - Release artifacts can be generated without manual source edits
  - The project is ready for handoff or production deployment
