class DownloaderBaseException(Exception):
    """Base exception for all downloader backend errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class InvalidURLError(DownloaderBaseException):
    """Raised when the user submits an invalid or malformed URL."""
    def __init__(self, message: str = "Please enter a valid media URL"):
        super().__init__(message, status_code=400)

class SSRFValidationError(DownloaderBaseException):
    """Raised when a URL fails SSRF safety validation (e.g. internal IP target)."""
    def __init__(self, message: str = "Access to private or local network addresses is forbidden"):
        super().__init__(message, status_code=403)

class ExtractionError(DownloaderBaseException):
    """Raised when yt-dlp metadata extraction fails."""
    def __init__(self, message: str = "Failed to extract media formats"):
        super().__init__(message, status_code=400)

class DownloadExecutionError(DownloaderBaseException):
    """Raised when yt-dlp binary media download execution fails."""
    def __init__(self, message: str = "Media download execution failed"):
        super().__init__(message, status_code=500)
