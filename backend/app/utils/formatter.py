from typing import Union, Optional

def format_duration(seconds: Optional[Union[int, float]]) -> str:
    """Format duration in seconds into HH:MM:SS or MM:SS string."""
    if not seconds or not isinstance(seconds, (int, float)):
        return ""
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
