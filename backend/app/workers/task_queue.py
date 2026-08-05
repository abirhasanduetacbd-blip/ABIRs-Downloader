import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, Any, Callable, Optional
from backend.app.logger import get_logger

logger = get_logger()

class TaskManager:
    """In-memory ThreadPoolExecutor task queue manager for background jobs."""
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="DownloadWorker")
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def submit_task(self, func: Callable, *args, **kwargs) -> str:
        """Submits a function to execute asynchronously in the thread pool."""
        task_id = str(uuid.uuid4())[:8]
        
        with self._lock:
            self.tasks[task_id] = {
                "id": task_id,
                "status": "pending",
                "result": None,
                "error": None
            }
            
        def _wrapper():
            with self._lock:
                self.tasks[task_id]["status"] = "running"
            try:
                logger.info(f"Task {task_id} execution started.")
                res = func(*args, **kwargs)
                with self._lock:
                    self.tasks[task_id]["status"] = "completed"
                    self.tasks[task_id]["result"] = res
                logger.info(f"Task {task_id} completed successfully.")
            except Exception as e:
                logger.error(f"Task {task_id} failed: {str(e)}")
                with self._lock:
                    self.tasks[task_id]["status"] = "failed"
                    self.tasks[task_id]["error"] = str(e)

        self.executor.submit(_wrapper)
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Returns current state dict for a submitted task_id."""
        with self._lock:
            return self.tasks.get(task_id)

# Module singleton instance
task_manager = TaskManager(max_workers=4)

def get_task_manager() -> TaskManager:
    """Returns task manager instance."""
    return task_manager
