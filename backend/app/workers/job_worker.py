import os
from typing import Dict, Any
from backend.app.workers.task_queue import task_manager
from backend.app.services.downloader import process_download
from backend.app.services import job_service
from backend.app.models.job import JobStatus
from backend.app.logger import get_logger

logger = get_logger()

def _make_progress_hook(job_id: str):
    """Creates a yt-dlp progress_hook callback targeting specific job_id."""
    def _hook(d: Dict[str, Any]):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0
            
            progress = (downloaded / total * 100.0) if total > 0 else 0.0
            speed_str = d.get("_speed_str", "").strip()
            eta_str = d.get("_eta_str", "").strip()
            
            job_service.update_job_progress(
                job_id=job_id,
                status=JobStatus.RUNNING,
                progress=progress,
                speed=speed_str,
                eta=eta_str
            )
        elif d.get("status") == "finished":
            job_service.update_job_progress(
                job_id=job_id,
                status=JobStatus.RUNNING,
                progress=99.0,
                speed="Merging/Transcoding...",
                eta="Finalizing"
            )
    return _hook

def execute_background_job(job_id: str, url: str, format_id: str, media_type: str) -> None:
    """Executes background download job in ThreadPool worker thread."""
    logger.info(f"Background worker starting execution for job {job_id}")
    job_service.update_job_progress(job_id, JobStatus.RUNNING, 0.1, "Starting...", "Calculating")
    
    try:
        hook = _make_progress_hook(job_id)
        file_path, download_filename, mimetype, info = process_download(
            url=url,
            fmt=format_id,
            typ=media_type,
            progress_callback=hook
        )
        
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        title = info.get("title", "Downloaded Media")
        thumbnail = info.get("thumbnail", "")
        
        job_service.complete_job(
            job_id=job_id,
            title=title,
            thumbnail=thumbnail,
            file_name=download_filename,
            file_path=file_path,
            file_size=file_size,
            media_type=media_type,
            url=url
        )
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Background job {job_id} failed: {err_msg}")
        job_service.fail_job(job_id, err_msg)

def start_download_job(url: str, format_id: str = "best", media_type: str = "video") -> Dict[str, Any]:
    """Enqueues a new background download job."""
    job_record = job_service.create_job(url, format_id, media_type)
    job_id = job_record["id"]
    
    task_manager.submit_task(execute_background_job, job_id, url, format_id, media_type)
    return job_record
