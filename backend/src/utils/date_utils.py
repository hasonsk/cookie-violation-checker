from datetime import datetime, timedelta
from typing import Optional
import re

def parse_iso_date(date_string: Optional[str]) -> Optional[datetime]:
    """Parse ISO date string to datetime object"""
    if not date_string:
        return None
    try:
        # Handle various ISO formats
        if date_string.endswith('Z'):
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return datetime.fromisoformat(date_string)
    except (ValueError, AttributeError):
        return None

def parse_retention_to_days(retention_str: str) -> Optional[int]:
    """Convert retention string to number of days"""
    if not retention_str:
        return None

    retention_lower = retention_str.lower()

    if 'session' in retention_lower:
        return 0

    # Parse common formats
    patterns = [
        (r'(\d+)\s*year', 365),
        (r'(\d+)\s*month', 30),
        (r'(\d+)\s*week', 7),
        (r'(\d+)\s*day', 1),
        (r'(\d+)\s*hour', 1/24)
    ]

    for pattern, multiplier in patterns:
        match = re.search(pattern, retention_lower)
        if match:
            return int(float(match.group(1)) * multiplier)

    return None

def calculate_actual_retention_days(expires: Optional[datetime]) -> Optional[int]:
    """Calculate actual retention days from expiration date"""
    if not expires:
        return 0  # Session cookie

    now = datetime.now()
    if expires <= now:
        return 0

    delta = expires - now
    return delta.days
