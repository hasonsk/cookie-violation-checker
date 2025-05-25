import re
from typing import List

class PatternMatcher:
    """Utility class for pattern matching operations"""

    @staticmethod
    def is_policy_link(url: str, patterns: List[str]) -> bool:
        """Check if URL matches cookie policy patterns"""
        url_lower = url.lower()
        return any(re.search(pattern, url_lower, re.IGNORECASE) for pattern in patterns)

    @staticmethod
    def is_policy_text(text: str, patterns: List[str]) -> bool:
        """Check if link text matches cookie policy patterns"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns)
