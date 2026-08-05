import os
import socket
import ipaddress
from urllib.parse import urlparse
from typing import Tuple

# Reserved private & internal network subnets to guard against SSRF
PRIVATE_SUBNETS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private Class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private Class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private Class C
    ipaddress.ip_network("169.254.169.254/32")# AWS / Cloud Metadata Endpoint
]

def is_valid_scheme(url: str) -> bool:
    """Checks if the URL scheme is strictly http or https."""
    try:
        parsed = urlparse(url)
        return parsed.scheme.lower() in ("http", "https")
    except Exception:
        return False

def is_private_ip(hostname: str) -> bool:
    """Resolves hostname and checks if resolved IP belongs to a private subnet."""
    try:
        # Resolve hostname to IP address
        ip_str = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip_str)
        
        for subnet in PRIVATE_SUBNETS:
            if ip_obj in subnet:
                return True
        return False
    except Exception:
        # If DNS resolution fails, allow yt-dlp to handle or reject downstream
        return False

def is_safe_path(base_dir: str, target_path: str) -> bool:
    """Verifies that target_path is within base_dir, guarding against path traversal."""
    try:
        abs_base = os.path.abspath(base_dir)
        abs_target = os.path.abspath(target_path)
        return os.path.commonpath([abs_base]) == os.path.commonpath([abs_base, abs_target])
    except Exception:
        return False

def validate_and_sanitize_url(url: str) -> Tuple[bool, str, str]:
    """Performs full security validation on a user-supplied URL string.
    
    Returns:
        Tuple of (is_valid: bool, sanitized_url: str, error_message: str)
    """
    if not url or not isinstance(url, str):
        return False, "", "Please enter a valid media URL"
        
    sanitized = url.strip()
    if not sanitized:
        return False, "", "Please enter a valid media URL"
        
    if not is_valid_scheme(sanitized):
        return False, "", "Invalid URL scheme. Only HTTP and HTTPS URLs are supported."
        
    try:
        parsed = urlparse(sanitized)
        hostname = parsed.hostname
        if hostname and is_private_ip(hostname):
            return False, "", "Access to local or private network addresses is forbidden."
    except Exception:
        pass
        
    return True, sanitized, ""
