import string

def safe_name(name: str, max_length: int = 60) -> str:
    """Sanitize file name for Windows OS & cross-platform compatibility.
    
    Removes Windows reserved characters (<>:"/\\|?*), trims whitespace,
    and caps maximum length to max_length.
    """
    if not name:
        return "downloaded_media"
        
    valid = set(string.printable) - set('<>:"/\\|?*')
    cleaned = "".join(c for c in name if c in valid)
    cleaned = cleaned.strip()[:max_length]
    
    return cleaned or "downloaded_media"
