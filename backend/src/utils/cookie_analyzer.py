import re
from typing import Dict, List, Tuple

class CookieValueAnalyzer:
    @staticmethod
    def analyze_cookie_value(value: str) -> Dict[str, float]:
        """Phân tích giá trị cookie để xác định loại"""
        if not value:
            return {}

        analysis = {}

        # JWT token pattern
        if re.match(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$', value):
            analysis['jwt_token'] = 0.9

        # Hash-like values (security tokens, session IDs)
        if re.match(r'^[a-f0-9]{32,}$', value.lower()):
            analysis['hash_token'] = 0.8

        # UUID pattern
        if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value.lower()):
            analysis['uuid'] = 0.8

        # Base64 encoded data
        if re.match(r'^[A-Za-z0-9+/=]+$', value) and len(value) % 4 == 0:
            analysis['base64'] = 0.6

        # Timestamp values
        if re.match(r'^\d{10,13}$', value):  # Unix timestamp
            analysis['timestamp'] = 0.5

        return analysis

class CookieSecurityAnalyzer:
    @staticmethod
    def check_security_indicators(cookie) -> bool:
        """Kiểm tra các chỉ số bảo mật của cookie"""
        security_flags = 0

        # Secure flag
        if hasattr(cookie, 'secure') and cookie.secure:
            security_flags += 1

        # HttpOnly flag
        if hasattr(cookie, 'httponly') and cookie.httponly:
            security_flags += 1

        # SameSite attribute
        if hasattr(cookie, 'samesite') and cookie.samesite:
            security_flags += 1

        # Path restriction (more specific paths are more likely to be functional)
        if hasattr(cookie, 'path') and cookie.path and cookie.path != '/':
            security_flags += 0.5

        return security_flags >= 2  # Có ít nhất 2 chỉ số bảo mật

class ConfidenceCalculator:
    @staticmethod
    def calculate_confidence_score(matches: List[Tuple[str, float]]) -> Dict[str, float]:
        """Tính toán độ tin cậy cho mỗi loại cookie"""
        confidence_scores = {}

        for purpose, score in matches:
            if purpose not in confidence_scores:
                confidence_scores[purpose] = 0
            confidence_scores[purpose] += score

        # Normalize scores
        if confidence_scores:
            max_score = max(confidence_scores.values())
            for purpose in confidence_scores:
                confidence_scores[purpose] = min(confidence_scores[purpose] / max_score, 1.0)

        return confidence_scores
