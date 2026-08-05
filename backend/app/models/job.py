from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

class JobStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class DownloadJobDTO:
    id: str
    url: str
    format_id: str
    media_type: str
    status: str = JobStatus.PENDING
    progress: float = 0.0
    speed: str = ""
    eta: str = ""
    title: str = ""
    thumbnail: str = ""
    file_name: str = ""
    file_path: str = ""
    file_size: int = 0
    error_message: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
