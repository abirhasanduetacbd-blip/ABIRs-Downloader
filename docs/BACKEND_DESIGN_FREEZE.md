# 🧊 BACKEND DESIGN FREEZE SPECIFICATION

> **Document Version:** 1.0.0  
> **Status:** RATIFIED & FROZEN (ZERO-REFACTOR SPECIFICATION)  
> **Target Framework:** Python Flask (v1 Baseline Architecture)  
> **Governing Documents:** [PROJECT_CONSTITUTION.md](file:///C:/Users/Abir/Downloader/PROJECT_CONSTITUTION.md) & [ENTERPRISE_ARCHITECTURE.md](file:///C:/Users/Abir/Downloader/ENTERPRISE_ARCHITECTURE.md)  
> **Development Reference Rule:** `server.py` in root is READ-ONLY REFERENCE. `backend/app/main.py` is ACTIVE DEVELOPMENT FILE.  

---

## 1. Executive Summary

This Backend Design Freeze defines the exact internal architecture, module responsibilities, function signatures, data flow schemas, and dependencies for all Python components residing within the `backend/` directory.

No implementation code will be written until this specification is frozen. By pre-defining every module, class, public method signature, parameter type, return type, and dependency, we guarantee zero code refactoring during Phase 2 & Phase 3.

```
+-----------------------------------------------------------------------------------+
|                            backend/app/main.py (Flask App)                        |
+-----------------------------------------------------------------------------------+
                                          |
                   +----------------------+----------------------+
                   |                                             |
                   v                                             v
+------------------------------------+         +------------------------------------+
|  backend/app/api/v1/endpoints/     |         |  backend/app/core/                 |
|  - health.py (GET /health)         |         |  - config.py (Settings & Constants)|
|  - analyze.py (POST /formats)      |         |  - security.py (SSRF & Guards)     |
|  - download.py (GET /download)     |         |  - database.py (SQLite - Phase 4)  |
+------------------------------------+         +------------------------------------+
                   |                                             |
                   +----------------------+----------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                            backend/app/services/                                  |
|  - extractor.py (yt-dlp Media Metadata Extraction)                                |
|  - downloader.py (Media Transcoding, FFmpeg Merging & Cleanup)                    |
|  - spotify.py (Spotify Metadata Resolving & YouTube Search Workaround)           |
+-----------------------------------------------------------------------------------+
                                          |
                   +----------------------+----------------------+
                   |                                             |
                   v                                             v
+------------------------------------+         +------------------------------------+
|  backend/app/utils/                |         |  backend/app/models/               |
|  - sanitizer.py (safe_name)        |         |  - schemas.py (API Payloads)       |
|  - formatter.py (duration formats) |         |                                    |
+------------------------------------+         +------------------------------------+
```

---

## 2. Module Specifications

### 2.1 Configuration Module (`backend/app/core/config.py`)

- **Purpose:** Centralized, type-safe configuration manager for local desktop and cloud deployments.
- **Responsibilities:** Load environment variables, define default host/port bindings, declare path constants, provide runtime setting lookups.
- **Dependencies:** Standard Library (`os`, `dataclasses`, `typing`).

#### Class & Function Signatures

```python
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DOWNLOAD_DIR: str = os.path.join(BASE_DIR, "downloads")
    WEB_DIR: str = os.path.join(BASE_DIR, "..", "web")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 9191))
    MAX_FILE_AGE: int = int(os.getenv("MAX_FILE_AGE", 600))  # 10 minutes
    MAX_FILENAME_LENGTH: int = 60
    ALLOWED_ORIGINS: str = "*"

def get_config() -> Config:
    """Returns the immutable application configuration instance."""
    ...
```

---

### 2.2 Security & SSRF Guard Module (`backend/app/core/security.py`)

- **Purpose:** Protect backend from Server-Side Request Forgery (SSRF), malicious URL injection, and illegal IP space traversal.
- **Responsibilities:** Validate HTTP/HTTPS schemes, resolve hostnames to IP addresses, verify IP addresses against private subnet blocklists, sanitize raw URL strings.
- **Dependencies:** Standard Library (`urllib.parse`, `socket`, `ipaddress`, `typing`).

#### Public Function Signatures

```python
from typing import Tuple

def is_valid_scheme(url: str) -> bool:
    """Validates that URL scheme is strictly http or https.
    
    Args:
        url: Raw input URL string.
    Returns:
        True if scheme is valid, False otherwise.
    """
    ...

def is_private_ip(hostname: str) -> bool:
    """Resolves hostname and checks if resolved IP belongs to private subnet space.
    
    Checks against: 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.169.254.
    
    Args:
        hostname: Extracted URL domain/host.
    Returns:
        True if IP is private/loopback, False if public.
    """
    ...

def validate_and_sanitize_url(url: str) -> Tuple[bool, str, str]:
    """Performs full security validation on user-supplied URL.
    
    Args:
        url: Raw input URL string.
    Returns:
        Tuple of (is_valid: bool, sanitized_url: str, error_message: str)
    """
    ...
```

---

### 2.3 Sanitization Utility (`backend/app/utils/sanitizer.py`)

- **Purpose:** Sanitize user-provided or extracted media titles for OS filename compatibility.
- **Responsibilities:** Remove Windows reserved characters (`<>:"/\|?*`), control characters, leading/trailing whitespace, and truncate to maximum character limit.
- **Dependencies:** Standard Library (`string`, `re`).

#### Public Function Signatures

```python
def safe_name(name: str, max_length: int = 60) -> str:
    """Sanitizes file name for Windows OS & cross-platform compatibility.
    
    Args:
        name: Raw extracted media title string.
        max_length: Maximum allowed string length (default 60).
    Returns:
        Sanitized, OS-safe filename string.
    """
    ...
```

---

### 2.4 Formatting Utility (`backend/app/utils/formatter.py`)

- **Purpose:** Format media metadata primitives into human-readable strings.
- **Responsibilities:** Convert integer/float duration seconds into `HH:MM:SS` or `MM:SS` format.
- **Dependencies:** Standard Library (`typing`).

#### Public Function Signatures

```python
from typing import Union, Optional

def format_duration(seconds: Optional[Union[int, float]]) -> str:
    """Converts duration in seconds to formatted time string (e.g. '03:45' or '1:15:30').
    
    Args:
        seconds: Numeric seconds value or None.
    Returns:
        Formatted time string or empty string if input is invalid.
    """
    ...
```

---

### 2.5 Spotify Resolver Service (`backend/app/services/spotify.py`)

- **Purpose:** Resolve Spotify track URLs into metadata and find matching YouTube video streams.
- **Responsibilities:** Fetch public Spotify track title via HTTP header scraping, parse track/artist names, execute `ytsearch1:` lookup via `yt-dlp`.
- **Dependencies:** Third-Party (`requests`, `yt_dlp`), Standard Library (`re`, `typing`).

#### Public Function Signatures

```python
from typing import Dict, Any, Optional

def extract_spotify_metadata(url: str) -> Dict[str, Any]:
    """Scrapes Spotify track webpage title and returns fallback metadata dictionary.
    
    Args:
        url: Public Spotify track URL.
    Returns:
        Dict containing title, thumbnail, uploader, duration, and default format list.
    """
    ...

def resolve_spotify_to_youtube(url: str) -> str:
    """Extracts track title from Spotify link and performs ytsearch to get YouTube video URL.
    
    Args:
        url: Spotify track URL.
    Returns:
        Matching YouTube watch URL string or fallback search query URL.
    """
    ...
```

---

### 2.6 Media Extractor Service (`backend/app/services/extractor.py`)

- **Purpose:** Wrap `yt-dlp` info extraction engine to analyze media links and parse resolution options.
- **Responsibilities:** Execute `yt-dlp` in `skip_download` mode, handle Spotify workarounds, format video/audio resolution options, return structured format payloads.
- **Dependencies:** Third-Party (`yt_dlp`), Internal Modules (`spotify.py`, `formatter.py`).

#### Public Function Signatures

```python
from typing import Dict, Any

def analyze_media_url(url: str) -> Dict[str, Any]:
    """Parses media URL using yt-dlp and returns extracted metadata & available formats.
    
    Args:
        url: Validated public media URL string.
    Returns:
        Dict containing success flag, title, thumbnail, uploader, duration, and formats list.
    Raises:
        ValueError: If URL extraction fails or platform is unsupported.
    """
    ...
```

---

### 2.7 Media Downloader & Cleanup Service (`backend/app/services/downloader.py`)

- **Purpose:** Execute binary media downloads, stream merging, audio extraction, and temporary file rotation.
- **Responsibilities:** Configure `yt-dlp` download options, invoke FFmpeg for MP3 extraction or MP4 merging, sanitize output filename, locate output file, purge old temporary files.
- **Dependencies:** Third-Party (`yt_dlp`), Standard Library (`os`, `uuid`, `time`, `typing`), Internal Modules (`sanitizer.py`, `config.py`, `spotify.py`).

#### Public Function Signatures

```python
from typing import Tuple, Optional, Dict, Any

def cleanup_old_files(max_age_seconds: int = 600) -> int:
    """Removes temporary downloaded files older than max_age_seconds.
    
    Args:
        max_age_seconds: Threshold age in seconds (default 600s).
    Returns:
        Count of deleted files.
    """
    ...

def process_download(url: str, format_id: str = "best", media_type: str = "video") -> Tuple[str, str, str]:
    """Executes yt-dlp media download and returns output file path, download name, and mimetype.
    
    Args:
        url: Target media URL.
        format_id: Selected resolution height or 'best'/'mp3_best'.
        media_type: 'video' or 'audio'.
    Returns:
        Tuple of (file_path: str, download_filename: str, mimetype: str)
    Raises:
        FileNotFoundError: If output file was not found after download.
        RuntimeError: If yt-dlp download execution failed.
    """
    ...
```

---

### 2.8 API Response Schema Helper (`backend/app/models/schemas.py`)

- **Purpose:** Standardize JSON API payload response structures across all endpoints.
- **Responsibilities:** Construct consistent `success`, `data`, `error` JSON responses.
- **Dependencies:** Standard Library (`typing`).

#### Public Function Signatures

```python
from typing import Dict, Any, Optional

def api_response(success: bool, data: Optional[Any] = None, error: Optional[str] = None) -> Dict[str, Any]:
    """Constructs standardized API response envelope dictionary.
    
    Args:
        success: Boolean status flag.
        data: Optional payload dictionary or list.
        error: Optional human-readable error message string.
    Returns:
        Dictionary payload suitable for jsonify().
    """
    ...
```

---

### 2.9 Endpoint Blueprints (`backend/app/api/v1/endpoints/`)

#### 2.9.1 Health Endpoint (`health.py`)
- **Blueprint Name:** `health_bp`
- **Route:** `GET /health`
- **Controller Function:** `health_check()` -> `200 OK` JSON status.

#### 2.9.2 Media Analysis Endpoint (`analyze.py`)
- **Blueprint Name:** `analyze_bp`
- **Routes:** `POST /api/analyze`, `POST /formats`
- **Controller Function:** `analyze_url_endpoint()` -> JSON format payload via `extractor.analyze_media_url()`.

#### 2.9.3 Media Download Endpoint (`download.py`)
- **Blueprint Name:** `download_bp`
- **Routes:** `GET /api/download`, `GET /download`
- **Controller Function:** `download_file_endpoint()` -> Attachment stream via `downloader.process_download()`.

#### 2.9.4 Static Web PWA Server (`web_server.py`)
- **Blueprint Name:** `web_bp`
- **Routes:** `GET /`, `GET /manifest.json`, `GET /sw.js`
- **Controller Function:** `serve_static_asset()` -> Serves static files from `web/` directory.

---

### 2.10 Flask Application Entry Point (`backend/app/main.py`)

- **Purpose:** Primary application gateway assembling Flask app instance, CORS configurations, blueprint registrations, and local browser launch daemon thread.
- **Responsibilities:** Initialize Flask `app`, configure `CORS(app, resources={r"/*": {"origins": "*"}})` for local mode, register all blueprints, launch browser thread on `127.0.0.1`, start Uvicorn/Flask server.
- **Dependencies:** `flask`, `flask_cors`, `webbrowser`, `threading`, `backend.app.core.config`, `backend.app.api.v1...`.

```python
# Architecture Blueprint Assembly in main.py
def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Register API Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(web_bp)
    
    return app
```

---

## 3. Module Dependency Matrix

| Module | Depends On Internal | Depends On Third-Party / StdLib |
| :--- | :--- | :--- |
| `config.py` | None | `os`, `dataclasses` |
| `security.py` | None | `urllib.parse`, `socket`, `ipaddress` |
| `sanitizer.py` | None | `string`, `re` |
| `formatter.py` | None | `typing` |
| `spotify.py` | None | `requests`, `re`, `yt_dlp` |
| `extractor.py` | `spotify.py`, `formatter.py` | `yt_dlp` |
| `downloader.py` | `sanitizer.py`, `config.py`, `spotify.py` | `yt_dlp`, `os`, `uuid`, `time` |
| `schemas.py` | None | `typing` |
| `endpoints/*.py` | `security.py`, `extractor.py`, `downloader.py`, `schemas.py` | `flask` |
| `main.py` | `config.py`, `endpoints/*.py` | `flask`, `flask_cors`, `webbrowser`, `threading` |

---

## 4. Freeze Ratification Checklist

- [x] All 10 backend sub-modules explicitly defined.
- [x] Every public function signature declared with typing hints.
- [x] Zero dependency cycles present in module graph.
- [x] Read-only reference `server.py` preserved; `backend/app/main.py` established as target.
- [x] Ready to proceed directly with Phase 2 (Flask Modularization) code implementation.

---

> **BACKEND DESIGN FROZEN & RATIFIED**  
> *No architectural refactoring will occur during code implementation.*
