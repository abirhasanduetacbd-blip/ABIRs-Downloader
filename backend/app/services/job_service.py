import uuid
from typing import Dict, Any, List, Optional
from backend.app.core.database import get_db
from backend.app.models.job import JobStatus, DownloadJobDTO
from backend.app.logger import get_logger

logger = get_logger()

def create_job(url: str, format_id: str = "best", media_type: str = "video") -> Dict[str, Any]:
    """Creates a new download job record in SQLite database."""
    job_id = f"job_{str(uuid.uuid4())[:8]}"
    
    with get_db() as conn:
        conn.execute("""
            INSERT INTO download_jobs (id, url, format_id, media_type, status, progress)
            VALUES (?, ?, ?, ?, ?, 0.0)
        """, (job_id, url, format_id, media_type, JobStatus.PENDING))
        
    logger.info(f"Created download job record: {job_id} for URL: {url}")
    return get_job_by_id(job_id)

def get_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a download job record by ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM download_jobs WHERE id = ?", (job_id,)).fetchone()
        if row:
            return dict(row)
    return None

def update_job_progress(job_id: str, status: str, progress: float, speed: str = "", eta: str = "", error_message: str = "") -> None:
    """Updates job status, progress percentage, speed, and ETA."""
    with get_db() as conn:
        conn.execute("""
            UPDATE download_jobs
            SET status = ?, progress = ?, speed = ?, eta = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, round(progress, 1), speed, eta, error_message, job_id))

def complete_job(job_id: str, title: str, thumbnail: str, file_name: str, file_path: str, file_size: int, media_type: str, url: str) -> None:
    """Marks job as COMPLETED and records entry into download history."""
    download_url = f"/api/v1/jobs/{job_id}/stream"
    
    with get_db() as conn:
        # 1. Mark Job as Completed
        conn.execute("""
            UPDATE download_jobs
            SET status = ?, progress = 100.0, title = ?, thumbnail = ?, file_name = ?, file_path = ?, file_size = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (JobStatus.COMPLETED, title, thumbnail, file_name, file_path, file_size, job_id))

        # 2. Record Entry in Download History
        conn.execute("""
            INSERT INTO download_history (job_id, title, url, media_type, file_name, file_size, download_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (job_id, title, url, media_type, file_name, file_size, download_url))

    logger.info(f"Job {job_id} completed and recorded in history: {file_name}")

def fail_job(job_id: str, error_message: str) -> None:
    """Marks job as FAILED with error message."""
    with get_db() as conn:
        conn.execute("""
            UPDATE download_jobs
            SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (JobStatus.FAILED, error_message[:250], job_id))
    logger.error(f"Job {job_id} failed: {error_message}")

def cancel_job(job_id: str) -> bool:
    """Marks job as CANCELLED."""
    with get_db() as conn:
        cursor = conn.execute("""
            UPDATE download_jobs
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status IN ('pending', 'running')
        """, (JobStatus.CANCELLED, job_id))
        return cursor.rowcount > 0

def list_recent_jobs(limit: int = 20) -> List[Dict[str, Any]]:
    """Returns recent download jobs."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM download_jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

def list_history(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Returns persistent download history items."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM download_history ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        return [dict(r) for r in rows]

def clear_history(history_id: Optional[int] = None) -> bool:
    """Clears a single history entry or all history."""
    with get_db() as conn:
        if history_id:
            cursor = conn.execute("DELETE FROM download_history WHERE id = ?", (history_id,))
        else:
            cursor = conn.execute("DELETE FROM download_history")
        return cursor.rowcount > 0
